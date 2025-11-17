from django.shortcuts import render, redirect, get_object_or_404
from .models import ArticuloPapeleria

def gestion_articulos_papeleria(request):
    articulos = ArticuloPapeleria.objects.all()
    
    if request.method == 'POST':
        articulo_id = request.POST.get('articulo_id')
        
        if articulo_id:
            articulo = get_object_or_404(ArticuloPapeleria, id_papeleria=articulo_id)
        else:
            articulo = ArticuloPapeleria()
        
        articulo.nombre = request.POST.get('nombre')
        articulo.descripcion = request.POST.get('descripcion')
        articulo.cantidad_total = request.POST.get('cantidad_total')
        articulo.unidad_medida = request.POST.get('unidad_medida')
        articulo.devolucion = request.POST.get('devolucion')
        articulo.save()
        
        return redirect('gestion_articulos_papeleria')
    
    articulo_editar = None
    articulo_id = request.GET.get('editar')
    if articulo_id:
        articulo_editar = get_object_or_404(ArticuloPapeleria, id_papeleria=articulo_id)
    
    return render(request, 'inventario_papeleria.html', {
        'articulos': articulos,
        'articulo_editar': articulo_editar
    })

def eliminar_articulo_papeleria(request, id):
    articulo = get_object_or_404(ArticuloPapeleria, id_papeleria=id)
    articulo.delete()
    return redirect('gestion_articulos_papeleria')