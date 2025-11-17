from .models import ArticulosHardware
from django.shortcuts import render, redirect, get_object_or_404


def inventario_hardware(request):
    modo = request.GET.get("modo", "lista")
    id_edit = request.GET.get("id", None)

    # Modo editar (solo para mostrar el formulario)
    item = None
    if modo == "editar" and id_edit:
        item = get_object_or_404(ArticulosHardware, pk=id_edit)

    # Crear / Editar / Eliminar desde POST
    if request.method == "POST":
        accion = request.POST.get("accion")

        # --- CARGAR EL ITEM SIEMPRE EN POST SI EXISTE ID ---  
        if id_edit:
            item = get_object_or_404(ArticulosHardware, pk=id_edit)

        # Crear
        if accion == "crear":
            ArticulosHardware.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                marca=request.POST['marca'],
                modelo=request.POST['modelo'],
                serial=request.POST['serial'],
                cantidad_total=request.POST['cantidad_total'],
                estado=request.POST['estado'],
                devolucion=request.POST['devolucion'],
            )
            return redirect('/hardware/')

        # Editar
        if accion == "editar":
            item.nombre = request.POST['nombre']
            item.descripcion = request.POST['descripcion']
            item.marca = request.POST['marca']
            item.modelo = request.POST['modelo']
            item.serial = request.POST['serial']
            item.cantidad_total = request.POST['cantidad_total']
            item.estado = request.POST['estado']
            item.devolucion = request.POST['devolucion']
            item.save()
            return redirect('/hardware/')

        # Eliminar
        if accion == "eliminar":
            item.delete()
            return redirect('/hardware/')

    # Consultar lista
    datos = ArticulosHardware.objects.all()

    return render(request, "inventario_hardware.html", {
        "modo": modo,
        "item": item,
        "datos": datos
    })
