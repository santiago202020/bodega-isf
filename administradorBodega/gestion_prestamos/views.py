# administradorBodega/gestion_prestamos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from docente.prestamo.models import Prestamo, DetallePrestamo
from administradorBodega.gestion_prestamos.models import Devolucion, DevolucionDetalle

from administradorBodega.inventario_hardware.models import ArticulosHardware
from administradorBodega.inventario_papeleria.models import ArticuloPapeleria
from administradorBodega.inventario_deportivo.models import ArticuloDeportivo

# Lista todos los préstamos PENDIENTES
def lista_pendientes(request):
    prestamos = Prestamo.objects.filter(estado="PENDIENTE").order_by("-fecha_prestamo", "-hora_prestamo")
    return render(request, "gestion_prestamos/pendientes.html", {"prestamos": prestamos})

# Mostrar detalle (igual que la vista docente pero con acciones)
def detalle_prestamo_admin(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    detalles = prestamo.detalles.all()
    detalles_con_obj = []
    for d in detalles:
        obj = None
        if d.tipo_articulo == "hardware":
            obj = ArticulosHardware.objects.filter(id_hardware=d.id_articulo).first()
        elif d.tipo_articulo == "papeleria":
            obj = ArticuloPapeleria.objects.filter(id_papeleria=d.id_articulo).first()
        elif d.tipo_articulo == "deportivo":
            obj = ArticuloDeportivo.objects.filter(id_deportivo=d.id_articulo).first()
        detalles_con_obj.append({"detalle": d, "obj": obj})
    return render(request, "gestion_prestamos/detalle_admin.html", {"prestamo": prestamo, "detalles": detalles_con_obj})

# Aceptar prestamo: aplica reglas por tipo
def aceptar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if prestamo.estado != "PENDIENTE":
        messages.warning(request, "El préstamo no está pendiente.")
        return redirect("gestion_prestamos:lista_pendientes")

    detalles = prestamo.detalles.all()

    # Intentar aplicar cambios a inventario
    errores = []
    for d in detalles:
        # buscar el objeto real
        if d.tipo_articulo == "papeleria":
            obj = ArticuloPapeleria.objects.filter(id_papeleria=d.id_articulo).first()
            if obj:
                # intenta decrementar cantidad_actual o cantidad_total si existe
                if hasattr(obj, "cantidad_actual"):
                    obj.cantidad_actual = max(0, getattr(obj, "cantidad_actual") - int(d.cantidad))
                    obj.save()
                elif hasattr(obj, "cantidad_total"):
                    obj.cantidad_total = max(0, getattr(obj, "cantidad_total") - int(d.cantidad))
                    obj.save()
                else:
                    errores.append(f"No campo cantidad en papeleria id={d.id_articulo}")
            else:
                errores.append(f"Papelería id {d.id_articulo} no encontrada")

        elif d.tipo_articulo == "hardware":
            obj = ArticulosHardware.objects.filter(id_hardware=d.id_articulo).first()
            if obj:
                # marcar inactivo si hay campo estado
                if hasattr(obj, "estado"):
                    try:
                        obj.estado = False
                        obj.save()
                    except Exception:
                        # si es booleano distinto, intenta otro campo
                        pass
                else:
                    errores.append(f"No campo estado para hardware id={d.id_articulo}")
            else:
                errores.append(f"Hardware id {d.id_articulo} no encontrado")

        elif d.tipo_articulo == "deportivo":
            obj = ArticuloDeportivo.objects.filter(id_deportivo=d.id_articulo).first()
            if obj:
                if hasattr(obj, "estado"):
                    obj.estado = False
                    obj.save()
                else:
                    errores.append(f"No campo estado para deportivo id={d.id_articulo}")
            else:
                errores.append(f"Deportivo id {d.id_articulo} no encontrado")

        # actualizar estado del detalle (si la tabla lo permite)
        try:
            d.estado_detalle = "ACEPTADO"
            d.save()
        except Exception:
            # si detalle_prestamo es managed=False y no tiene columna, ignoramos
            pass

    # marcar prestamo aceptado si no hay errores críticos
    prestamo.estado = "ACEPTADO"
    prestamo.save()

    if errores:
        messages.warning(request, "Aceptado, pero hubo advertencias: " + "; ".join(errores))
    else:
        messages.success(request, "Préstamo aceptado correctamente.")

    return redirect("gestion_prestamos:lista_pendientes")

# Rechazar préstamo (sin tocar inventario)
def rechazar_prestamo(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    prestamo.estado = "RECHAZADO"
    prestamo.save()
    messages.success(request, "Préstamo rechazado.")
    return redirect("gestion_prestamos:lista_pendientes")

# Registrar devolución: se espera que el admin proporcione las cantidades devueltas por detalle
def registrar_devolucion(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    detalles = prestamo.detalles.all()

    if request.method == "POST":
        # para cada detalle se espera un input con nombre devolver_<id_detalle>
        for d in detalles:
            key = f"devolver_{d.id_detalle}"
            val = request.POST.get(key)
            if val is None:
                continue
            try:
                qty = int(val)
            except ValueError:
                qty = 0

            # localizar objeto real
            if d.tipo_articulo == "papeleria":
                obj = ArticuloPapeleria.objects.filter(id_papeleria=d.id_articulo).first()
                if obj and hasattr(obj, "cantidad_actual"):
                    obj.cantidad_actual = getattr(obj, "cantidad_actual") + qty
                    obj.save()
            elif d.tipo_articulo in ("hardware", "deportivo"):
                obj = None
                if d.tipo_articulo == "hardware":
                    obj = ArticulosHardware.objects.filter(id_hardware=d.id_articulo).first()
                else:
                    obj = ArticuloDeportivo.objects.filter(id_deportivo=d.id_articulo).first()
                if obj and hasattr(obj, "estado"):
                    # si qty>0 asumimos que fue devuelto -> reactivar
                    if qty >= 1:
                        obj.estado = True
                        obj.save()

            # actualizar estado del detalle
            try:
                d.estado_detalle = "DEVUELTO"
                d.save()
            except Exception:
                pass

        prestamo.estado = "DEVUELTO"
        prestamo.save()
        messages.success(request, "Devolución registrada.")
        return redirect("gestion_prestamos:lista_pendientes")

    # GET -> mostrar formulario simple para devolver
    detalles_con_obj = []
    for d in detalles:
        obj = None
        if d.tipo_articulo == "hardware":
            obj = ArticulosHardware.objects.filter(id_hardware=d.id_articulo).first()
        elif d.tipo_articulo == "papeleria":
            obj = ArticuloPapeleria.objects.filter(id_papeleria=d.id_articulo).first()
        elif d.tipo_articulo == "deportivo":
            obj = ArticuloDeportivo.objects.filter(id_deportivo=d.id_articulo).first()
        detalles_con_obj.append({"detalle": d, "obj": obj})

    return render(request, "gestion_prestamos/devolver.html", {"prestamo": prestamo, "detalles": detalles_con_obj})
