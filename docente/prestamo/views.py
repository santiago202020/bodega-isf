from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Prestamo, DetallePrestamo
from administradorBodega.inventario_hardware.models import ArticulosHardware
from administradorBodega.inventario_papeleria.models import ArticuloPapeleria
from administradorBodega.inventario_deportivo.models import ArticuloDeportivo

@login_required
def confirmar_prestamo(request):
    bolsa = request.session.get("bolsa", [])
    if not bolsa:
        return redirect("elegir_articulo")  # o a ver_bolsa

    if request.method == "POST":
        # crear cabecera de prestamo
        prestamo = Prestamo.objects.create(
            id_usuario=request.user,
            fecha_prestamo=timezone.now().date(),
            hora_prestamo=timezone.now().time(),
            estado="PENDIENTE",
            observaciones = request.POST.get('observaciones', '')
        )

        # crear detalles
        for uid in bolsa:
            tipo, idreal = uid.split(":")
            # Por ahora guardamos la referencia; no tocamos inventario hasta ACEPTACION admin
            DetallePrestamo.objects.create(
                id_prestamo=prestamo,
                tipo_articulo=tipo,
                id_articulo=int(idreal),
                cantidad=1,  # si manejas cantidades distintas, cambia la lógica para tomar del formulario
                estado_detalle='PENDIENTE'
            )

        # vaciar bolsa
        request.session["bolsa"] = []
        request.session.modified = True

        return redirect("prestamo:mis_prestamos")

    # GET: mostrar resumen antes de confirmar
    items = []
    for uid in bolsa:
        tipo, idreal = uid.split(":")
        obj = None
        if tipo == "hardware":
            obj = ArticulosHardware.objects.filter(id_hardware=idreal).first()
        elif tipo == "papeleria":
            obj = ArticuloPapeleria.objects.filter(id_papeleria=idreal).first()
        elif tipo == "deportivo":
            obj = ArticuloDeportivo.objects.filter(id_deportivo=idreal).first()

        if obj:
            items.append({"uid": uid, "tipo": tipo, "obj": obj})

    return render(request, "confirmar.html", {"items": items})

@login_required
def lista_mis_prestamos(request):
    prestamos = Prestamo.objects.filter(id_usuario=request.user).order_by('-fecha_prestamo','-hora_prestamo')
    return render(request, "lista_prestamos.html", {"prestamos": prestamos})

@login_required
def detalle_prestamo(request, pk):
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
    return render(request, "detalle_prestamo.html", {"prestamo": prestamo, "detalles": detalles_con_obj})
