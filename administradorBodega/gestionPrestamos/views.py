# administradorBodega/gestionPrestamos/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Prestamo, DetallePrestamo, ArticuloPapeleria, ArticuloHardware, ArticuloDeportivo

def prestamos_pendientes(request):
    if request.session.get("id_rol") != 100:
        messages.error(request, "Acceso denegado")
        return redirect('/login/')
    
    prestamos = Prestamo.objects.filter(estado__in=['PENDIENTE', 'RESERVA'])
    
    prestamos_con_detalles = []
    for prestamo in prestamos:
        detalles = DetallePrestamo.objects.filter(id_prestamo=prestamo.id_prestamo)
        
        detalles_con_info = []
        puede_aprobar = True
        
        for detalle in detalles:
            # Obtener información completa del artículo
            info_articulo = _obtener_info_articulo(detalle.tipo_articulo, detalle.id_articulo)
            
            # Verificar disponibilidad
            disponible = _verificar_disponibilidad_articulo(
                detalle.tipo_articulo, 
                detalle.id_articulo, 
                detalle.cantidad
            )
            
            if not disponible['puede_prestar']:
                puede_aprobar = False
            
            detalles_con_info.append({
                'detalle': detalle,
                'info_articulo': info_articulo,
                'disponible': disponible
            })
        
        prestamos_con_detalles.append({
            'prestamo': prestamo,
            'detalles': detalles_con_info,
            'puede_aprobar': puede_aprobar
        })
    
    return render(request, 'pendientes.html', {
        'prestamos_con_detalles': prestamos_con_detalles
    })

def _obtener_info_articulo(tipo_articulo, id_articulo):
    """Obtiene la información completa del artículo"""
    try:
        if tipo_articulo == 'papeleria':
            articulo = ArticuloPapeleria.objects.get(id_papeleria=id_articulo)
            return {
                'nombre': articulo.nombre,
                'descripcion': articulo.descripcion,
                'cantidad_total': articulo.cantidad_total,
                'estado': articulo.estado,
                'tipo': 'Papelería'
            }
        elif tipo_articulo == 'hardware':
            articulo = ArticuloHardware.objects.get(id_hardware=id_articulo)
            return {
                'nombre': articulo.nombre,
                'descripcion': articulo.descripcion,
                'marca': articulo.marca,
                'modelo': articulo.modelo,
                'cantidad_total': articulo.cantidad_total,
                'estado': articulo.estado,
                'tipo': 'Hardware'
            }
        else:  # deportivo
            articulo = ArticuloDeportivo.objects.get(id_deportivo=id_articulo)
            return {
                'nombre': articulo.nombre,
                'descripcion': articulo.descripcion,
                'cantidad_total': articulo.cantidad_total,
                'estado': articulo.estado,
                'tipo': 'Deportivo'
            }
    except:
        return {
            'nombre': 'Artículo no encontrado',
            'descripcion': '',
            'cantidad_total': 0,
            'estado': 'no_encontrado',
            'tipo': 'Desconocido'
        }

def _verificar_disponibilidad_articulo(tipo_articulo, id_articulo, cantidad_solicitada):
    """Verifica disponibilidad del artículo - VERSIÓN CORREGIDA"""
    info_articulo = _obtener_info_articulo(tipo_articulo, id_articulo)
    
    if info_articulo['estado'] == 'no_encontrado':
        return {'puede_prestar': False, 'razon': 'Artículo no encontrado'}
    
    # ✅ CORREGIDO: Normalizar a minúsculas para comparar
    estado_articulo = info_articulo['estado'].lower().strip()
    
    # Verificar estado del artículo
    if estado_articulo != 'disponible':
        return {'puede_prestar': False, 'razon': f'Artículo {info_articulo["estado"]}'}
    
    # Verificar stock
    if info_articulo['cantidad_total'] < cantidad_solicitada:
        return {
            'puede_prestar': False, 
            'razon': f'Stock insuficiente. Disponible: {info_articulo["cantidad_total"]}, Solicitado: {cantidad_solicitada}'
        }
    
    return {'puede_prestar': True, 'razon': 'Disponible'}

def aprobar_prestamo(request, id_prestamo):
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    try:
        prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
        
        # Verificar nuevamente antes de aprobar
        detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
        puede_aprobar = True
        
        for detalle in detalles:
            disponible = _verificar_disponibilidad_articulo(
                detalle.tipo_articulo, 
                detalle.id_articulo, 
                detalle.cantidad
            )
            if not disponible['puede_prestar']:
                puede_aprobar = False
                messages.error(request, f"No se puede aprobar: {disponible['razon']}")
                break
        
        if puede_aprobar:
            prestamo.estado = 'ACEPTADA'
            prestamo.save()
            messages.success(request, f"Préstamo #{id_prestamo} aprobado exitosamente")
        else:
            messages.error(request, "No se pudo aprobar el préstamo")
            
    except Prestamo.DoesNotExist:
        messages.error(request, "Préstamo no encontrado")
    
    return redirect('gestionPrestamos:pendientes')

def rechazar_prestamo(request, id_prestamo):
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    try:
        prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
        prestamo.estado = 'RECHAZADA'
        prestamo.save()
        messages.success(request, f"Préstamo #{id_prestamo} rechazado")
    except Prestamo.DoesNotExist:
        messages.error(request, "Préstamo no encontrado")
    
    return redirect('gestionPrestamos:pendientes')