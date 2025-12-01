# administradorBodega/gestionDevolucion/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import Prestamo, DetallePrestamo, DetalleDevolucion, ArticuloPapeleria, ArticuloHardware, ArticuloDeportivo

def prestamos_para_devolucion(request):
    """Muestra préstamos ACEPTADOS que están listos para devolución"""
    if request.session.get("id_rol") != 100:
        messages.error(request, "Acceso denegado")
        return redirect('/login/')
    
    prestamos = Prestamo.objects.filter(estado='ACEPTADA')
    
    prestamos_con_detalles = []
    for prestamo in prestamos:
        detalles = DetallePrestamo.objects.filter(id_prestamo=prestamo.id_prestamo)
        
        detalles_con_info = []
        for detalle in detalles:
            info_articulo = _obtener_info_articulo(detalle.tipo_articulo, detalle.id_articulo)
            requiere_devolucion = _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo)
            
            # Verificar si ya fue devuelto
            ya_devuelto = DetalleDevolucion.objects.filter(
                id_articulo=detalle.id_articulo,
                tipo_articulo=detalle.tipo_articulo,
                id_devolucion=prestamo.id_prestamo  # Usamos id_prestamo como id_devolucion
            ).exists()
            
            detalles_con_info.append({
                'detalle': detalle,
                'info_articulo': info_articulo,
                'requiere_devolucion': requiere_devolucion,
                'ya_devuelto': ya_devuelto
            })
        
        prestamos_con_detalles.append({
            'prestamo': prestamo,
            'detalles': detalles_con_info
        })
    
    return render(request, 'devolucion_pendiente.html', {
        'prestamos_con_detalles': prestamos_con_detalles
    })

def registrar_devolucion_parcial(request, id_prestamo):
    """Registra devolución por artículo individual"""
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
                observaciones = request.POST.get('observaciones', '')
                
                # Procesar cada artículo del formulario
                for key, value in request.POST.items():
                    if key.startswith('cantidad_devuelta_'):
                        partes = key.split('_')
                        tipo_articulo = partes[2]
                        id_articulo = int(partes[3])
                        cantidad_devuelta = int(value)
                        
                        if cantidad_devuelta > 0:
                            # Buscar el detalle del préstamo
                            detalle_prestamo = DetallePrestamo.objects.get(
                                id_prestamo=id_prestamo,
                                tipo_articulo=tipo_articulo,
                                id_articulo=id_articulo
                            )
                            
                            # Registrar en detalle_devolucion
                            DetalleDevolucion.objects.create(
                                id_devolucion=id_prestamo,  # Usamos id_prestamo como referencia
                                tipo_articulo=tipo_articulo,
                                id_articulo=id_articulo,
                                cantidad=cantidad_devuelta,
                                estado_devolucion='DEVUELTO',
                                fecha_devolucion=timezone.now().date(),
                                observaciones=observaciones
                            )
                            
                            # Actualizar stock del artículo
                            _actualizar_stock_articulo(tipo_articulo, id_articulo, cantidad_devuelta)
                
                # Actualizar estado del préstamo
                estado_final = _determinar_estado_final(id_prestamo)
                prestamo.estado = estado_final
                prestamo.save()
                
                messages.success(request, f"Devolución parcial registrada. Estado: {estado_final}")
                
        except Exception as e:
            messages.error(request, f"Error al registrar devolución: {str(e)}")
    
    return redirect('gestionDevolucion:pendientes')

def registrar_devolucion_completa(request, id_prestamo):
    """Registra devolución completa de todos los artículos"""
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
                observaciones = request.POST.get('observaciones', '')
                
                detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
                
                for detalle in detalles:
                    if _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo):
                        # Registrar en detalle_devolucion
                        DetalleDevolucion.objects.create(
                            id_devolucion=id_prestamo,
                            tipo_articulo=detalle.tipo_articulo,
                            id_articulo=detalle.id_articulo,
                            cantidad=detalle.cantidad,
                            estado_devolucion='DEVUELTO',
                            fecha_devolucion=timezone.now().date(),
                            observaciones=observaciones
                        )
                        
                        # Actualizar stock
                        _actualizar_stock_articulo(detalle.tipo_articulo, detalle.id_articulo, detalle.cantidad)
                
                # Actualizar estado del préstamo
                estado_final = _determinar_estado_final(id_prestamo)
                prestamo.estado = estado_final
                prestamo.save()
                
                messages.success(request, f"Devolución completa registrada. Estado: {estado_final}")
                
        except Exception as e:
            messages.error(request, f"Error al registrar devolución: {str(e)}")
    
    return redirect('gestionDevolucion:pendientes')

def _obtener_info_articulo(tipo_articulo, id_articulo):
    """Obtiene información del artículo"""
    try:
        if tipo_articulo == 'papeleria':
            articulo = ArticuloPapeleria.objects.get(id_papeleria=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Papelería'
            }
        elif tipo_articulo == 'hardware':
            articulo = ArticuloHardware.objects.get(id_hardware=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Hardware'
            }
        else:  # deportivo
            articulo = ArticuloDeportivo.objects.get(id_deportivo=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Deportivo'
            }
    except:
        return {
            'nombre': 'Artículo no encontrado',
            'devolucion': 'NO',
            'tipo': 'Desconocido'
        }

def _requiere_devolucion(tipo_articulo, id_articulo):
    """Determina si un artículo requiere devolución"""
    info_articulo = _obtener_info_articulo(tipo_articulo, id_articulo)
    return info_articulo['devolucion'].upper() == 'SI'

def _actualizar_stock_articulo(tipo_articulo, id_articulo, cantidad_devuelta):
    """Actualiza el stock cuando se devuelve un artículo"""
    if tipo_articulo == 'papeleria':
        articulo = ArticuloPapeleria.objects.get(id_papeleria=id_articulo)
    elif tipo_articulo == 'hardware':
        articulo = ArticuloHardware.objects.get(id_hardware=id_articulo)
    else:  # deportivo
        articulo = ArticuloDeportivo.objects.get(id_deportivo=id_articulo)
    
    articulo.cantidad_total += cantidad_devuelta
    articulo.save()

def _determinar_estado_final(id_prestamo):
    """Determina el estado final basado en las devoluciones registradas"""
    detalles_prestamo = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
    detalles_devolucion = DetalleDevolucion.objects.filter(id_devolucion=id_prestamo)
    
    total_requiere_devolucion = 0
    total_devuelto = 0
    
    for detalle in detalles_prestamo:
        if _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo):
            total_requiere_devolucion += 1
            
            # Verificar si fue devuelto
            devuelto = detalles_devolucion.filter(
                tipo_articulo=detalle.tipo_articulo,
                id_articulo=detalle.id_articulo
            ).exists()
            
            if devuelto:
                total_devuelto += 1
    
    # Lógica de estados
    if total_requiere_devolucion == 0:
        return 'FINALIZADA'
    elif total_devuelto == total_requiere_devolucion:
        return 'DEVUELTO_COMPLETO'
    elif total_devuelto > 0:
        return 'DEVUELTO_PARCIAL'
    else:
        return 'NO_DEVUELTO'