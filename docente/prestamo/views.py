from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from login.decorators import login_required_custom
from login.models import Usuarios

from .models import Prestamo, DetallePrestamo

from administradorBodega.inventario_hardware.models import ArticulosHardware
from administradorBodega.inventario_papeleria.models import ArticuloPapeleria
from administradorBodega.inventario_deportivo.models import ArticuloDeportivo


# ===========================
# CONFIRMAR PRÉSTAMO
# ===========================
@login_required_custom
def confirmar_prestamo(request):
    bolsa = request.session.get("bolsa", [])
    if not bolsa:
        return redirect("elegir_articulo")

    usuario = Usuarios.objects.get(id_usuario=request.session["id_usuario"])

    if request.method == "POST":
        prestamo = Prestamo.objects.create(
            id_usuario=usuario,
            fecha_prestamo=timezone.now().date(),
            hora_prestamo=timezone.now().time(),
            estado="PENDIENTE",
            observaciones=request.POST.get("observaciones", "")
        )

        for uid in bolsa:
            tipo, idreal = uid.split(":")

            DetallePrestamo.objects.create(
                id_prestamo=prestamo,
                tipo_articulo=tipo,
                id_articulo=int(idreal),
                cantidad=1,
                estado_detalle="PENDIENTE"
            )

        request.session["bolsa"] = []
        request.session.modified = True

        # REDIRECCIÓN CORRECTA
        return redirect("prestamo:mis_prestamos")

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


# ===========================
# MIS PRÉSTAMOS (única vista correcta)
# ===========================
@login_required_custom
def mis_prestamos(request):
    usuario = Usuarios.objects.get(id_usuario=request.session["id_usuario"])
    prestamos = Prestamo.objects.filter(id_usuario=usuario).order_by("-fecha_prestamo", "-hora_prestamo")
    return render(request, "mis_prestamos.html", {"prestamos": prestamos})



# ===========================
# DETALLE DEL PRÉSTAMO
# ===========================
@login_required_custom
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

    return render(request, "detalle_prestamo.html", {
        "prestamo": prestamo,
        "detalles": detalles_con_obj
    })
