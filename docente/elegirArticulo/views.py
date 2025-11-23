from django.shortcuts import render, redirect
from administradorBodega.inventario_hardware.models import ArticulosHardware
from administradorBodega.inventario_papeleria.models import ArticuloPapeleria
from administradorBodega.inventario_deportivo.models import ArticuloDeportivo

# ---------------------------------------------------------
# 1. Unificar artículos y mostrar en tabla
# ---------------------------------------------------------
def elegir_articulo(request):
    # Traemos inventarios
    hardware = ArticulosHardware.objects.all()
    papeleria = ArticuloPapeleria.objects.all()
    deportivo = ArticuloDeportivo.objects.all()

    # Crear lista unificada
    articulos = []

    for h in hardware:
        articulos.append({
            "uid": f"hardware:{h.id_hardware}",
            "nombre": h.nombre,
            "descripcion": h.descripcion,
            "cantidad": h.cantidad_total,
            "tipo": "Hardware",
        })

    for p in papeleria:
        articulos.append({
            "uid": f"papeleria:{p.id_papeleria}",
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "cantidad": p.cantidad_total,
            "tipo": "Papelería",
        })

    for d in deportivo:
        articulos.append({
            "uid": f"deportivo:{d.id_deportivo}",
            "nombre": d.nombre,
            "descripcion": d.descripcion,
            "cantidad": d.cantidad_total,
            "tipo": "Deportivo",
        })

    # Inicializar bolsa
    if "bolsa" not in request.session:
        request.session["bolsa"] = []

    # Proceso de agregar
    if request.method == "POST":
        articulo_uid = request.POST.get("articulo_uid")

        if articulo_uid not in request.session["bolsa"]:
            request.session["bolsa"].append(articulo_uid)
            request.session.modified = True

        return redirect("elegir_articulo")

    return render(request, "elegir.html", {
        "articulos": articulos
    })


# ---------------------------------------------------------
# 2. Mostrar bolsa
# ---------------------------------------------------------
def ver_bolsa(request):

    bolsa = request.session.get("bolsa", [])
    items = []

    for uid in bolsa:
        # CAMBIO IMPORTANTE: dividir por ":" en lugar de "-"
        tipo, idreal = uid.split(":")

        if tipo == "hardware":
            obj = ArticulosHardware.objects.filter(id_hardware=idreal).first()
        elif tipo == "papeleria":
            obj = ArticuloPapeleria.objects.filter(id_papeleria=idreal).first()
        elif tipo == "deportivo":
            obj = ArticuloDeportivo.objects.filter(id_deportivo=idreal).first()
        else:
            obj = None

        if obj:
            items.append({"uid": uid, "tipo": tipo, "obj": obj})

    # Eliminar de bolsa
    if request.method == "POST":
        uid = request.POST.get("eliminar_uid")

        if uid in bolsa:
            bolsa.remove(uid)
            request.session["bolsa"] = bolsa
            request.session.modified = True
        return redirect("ver_bolsa")

    return render(request, "bolsa.html", {"articulos": items})

