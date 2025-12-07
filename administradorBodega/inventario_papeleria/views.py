from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ArticuloPapeleria

def gestion_articulos_papeleria(request):
    """
    Vista para gestionar el inventario de papelería
    """
    articulos = ArticuloPapeleria.objects.all().order_by('id_papeleria')
    articulo_editar = None
    
    # Si se envía el formulario para crear o editar
    if request.method == 'POST':
        articulo_id = request.POST.get('articulo_id')
        
        if articulo_id:  # Editar
            articulo = get_object_or_404(ArticuloPapeleria, id_papeleria=articulo_id)
            mensaje = "Artículo de papelería actualizado correctamente"
        else:  # Crear
            articulo = ArticuloPapeleria()
            mensaje = "Artículo de papelería creado correctamente"
        
        try:
            articulo.nombre = request.POST.get('nombre', '').strip()
            articulo.descripcion = request.POST.get('descripcion', '').strip()
            articulo.cantidad_total = request.POST.get('cantidad_total', 0)
            articulo.unidad_medida = request.POST.get('unidad_medida', 'UNIDAD')
            
            # Obtener estado (con valor por defecto)
            estado = request.POST.get('estado', 'DISPONIBLE')
            if estado not in dict(ArticuloPapeleria.ESTADO_CHOICES):
                estado = 'DISPONIBLE'
            articulo.estado = estado
            
            # Obtener devolución (con valor por defecto)
            devolucion = request.POST.get('devolucion', 'NO')
            if devolucion not in dict(ArticuloPapeleria.DEVOLUCION_CHOICES):
                devolucion = 'NO'
            articulo.devolucion = devolucion
            
            articulo.save()
            
            messages.success(request, mensaje)
            return redirect('gestion_articulos_papeleria')
            
        except Exception as e:
            messages.error(request, f"Error al guardar el artículo: {str(e)}")
    
    # Si se quiere editar (GET con ID)
    articulo_id = request.GET.get('editar')
    if articulo_id:
        articulo_editar = get_object_or_404(ArticuloPapeleria, id_papeleria=articulo_id)
    
    return render(request, 'inventario_papeleria.html', {
        'articulos': articulos,
        'articulo_editar': articulo_editar,
        'estado_choices': ArticuloPapeleria.ESTADO_CHOICES,
        'devolucion_choices': ArticuloPapeleria.DEVOLUCION_CHOICES,
        'unidad_choices': ArticuloPapeleria.UNIDAD_CHOICES
    })

def eliminar_articulo_papeleria(request, id):
    """
    Vista para eliminar artículo de papelería
    """
    articulo = get_object_or_404(ArticuloPapeleria, id_papeleria=id)
    try:
        nombre_articulo = articulo.nombre
        articulo.delete()
        messages.success(request, f"Artículo '{nombre_articulo}' eliminado correctamente")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")
    
    return redirect('gestion_articulos_papeleria')