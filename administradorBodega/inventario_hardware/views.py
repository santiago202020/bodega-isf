from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ArticulosHardware

def inventario_hardware(request):
    """
    Vista para gestionar el inventario de hardware
    """
    # Obtener todos los items para la lista
    datos = ArticulosHardware.objects.all().order_by('id_hardware')
    
    # Verificar si estamos en modo edición (GET)
    modo = request.GET.get("modo", "lista")
    id_edit = request.GET.get("id", None)
    
    item = None
    if modo == "editar" and id_edit:
        item = get_object_or_404(ArticulosHardware, pk=id_edit)
    
    # Manejar operaciones POST (Crear, Editar, Eliminar)
    if request.method == "POST":
        accion = request.POST.get("accion")
        
        try:
            # Crear nuevo item
            if accion == "crear":
                ArticulosHardware.objects.create(
                    nombre=request.POST.get('nombre', '').strip(),
                    descripcion=request.POST.get('descripcion', '').strip(),
                    marca=request.POST.get('marca', '').strip(),
                    modelo=request.POST.get('modelo', '').strip(),
                    serial=request.POST.get('serial', '').strip(),
                    cantidad_total=request.POST.get('cantidad_total', 0),
                    estado=request.POST.get('estado', 'DISPONIBLE'),
                    devolucion=request.POST.get('devolucion', 'NO'),
                )
                messages.success(request, "Hardware creado exitosamente")
                return redirect('inventario_hardware')
            
            # Editar item existente
            elif accion == "editar":
                id_item = request.POST.get('id_hardware')
                if id_item:
                    item = get_object_or_404(ArticulosHardware, pk=id_item)
                    item.nombre = request.POST.get('nombre', '').strip()
                    item.descripcion = request.POST.get('descripcion', '').strip()
                    item.marca = request.POST.get('marca', '').strip()
                    item.modelo = request.POST.get('modelo', '').strip()
                    item.serial = request.POST.get('serial', '').strip()
                    item.cantidad_total = request.POST.get('cantidad_total', 0)
                    item.estado = request.POST.get('estado', 'DISPONIBLE')
                    item.devolucion = request.POST.get('devolucion', 'NO')
                    item.save()
                    messages.success(request, "Hardware actualizado exitosamente")
                    return redirect('inventario_hardware')
            
            # Eliminar item
            elif accion == "eliminar":
                id_item = request.POST.get('id_hardware')
                if id_item:
                    item = get_object_or_404(ArticulosHardware, pk=id_item)
                    nombre_item = item.nombre
                    item.delete()
                    messages.success(request, f"Hardware '{nombre_item}' eliminado exitosamente")
                    return redirect('inventario_hardware')
        
        except Exception as e:
            messages.error(request, f"Error en la operación: {str(e)}")
    
    # Contexto para el template
    context = {
        "modo": modo,
        "item": item,
        "datos": datos,
        "estado_choices": ArticulosHardware.ESTADO_CHOICES,
        "devolucion_choices": ArticulosHardware.DEVOLUCION_CHOICES,
    }
    
    return render(request, "inventario_hardware.html", context)


def eliminar_hardware(request, id):
    """
    Vista para eliminar hardware mediante URL (GET)
    """
    if request.method == "GET":
        try:
            item = get_object_or_404(ArticulosHardware, pk=id)
            nombre_item = item.nombre
            item.delete()
            messages.success(request, f"Hardware '{nombre_item}' eliminado exitosamente")
        except Exception as e:
            messages.error(request, f"Error al eliminar: {str(e)}")
    
    return redirect('inventario_hardware')