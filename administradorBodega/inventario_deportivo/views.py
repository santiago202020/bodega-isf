from django.shortcuts import render, redirect, get_object_or_404
from .models import ArticuloDeportivo

def gestion_articulos(request):
    articulos = ArticuloDeportivo.objects.all()
    
    # Si se envía el formulario para crear o editar
    if request.method == 'POST':
        articulo_id = request.POST.get('articulo_id')
        
        if articulo_id:  # Editar
            articulo = get_object_or_404(ArticuloDeportivo, id_deportivo=articulo_id)
        else:  # Crear
            articulo = ArticuloDeportivo()
        
        articulo.nombre = request.POST.get('nombre')
        articulo.descripcion = request.POST.get('descripcion')
        articulo.cantidad_total = request.POST.get('cantidad_total')
        articulo.estado = request.POST.get('estado')
        articulo.devolucion = request.POST.get('devolucion')
        articulo.save()
        
        return redirect('gestion_articulos')
    
    # Si se quiere editar (GET con ID)
    articulo_editar = None
    articulo_id = request.GET.get('editar')
    if articulo_id:
        articulo_editar = get_object_or_404(ArticuloDeportivo, id_deportivo=articulo_id)
    
    return render(request, 'inventario_deportivo.html', {
        'articulos': articulos,
        'articulo_editar': articulo_editar
    })

def eliminar_articulo(request, id):
    articulo = get_object_or_404(ArticuloDeportivo, id_deportivo=id)
    articulo.delete()
    return redirect('gestion_articulos')