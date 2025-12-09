# administradorBodega/gestionDevolucion/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

# Importación de modelos
from administradorBodega.gestionDevolucion.models import Devolucion, DetalleDevolucion
from administradorBodega.gestionPrestamos.models import Prestamo, DetallePrestamo 
from administradorBodega.inventario_papeleria.models import ArticuloPapeleria
from administradorBodega.inventario_hardware.models import ArticulosHardware
from administradorBodega.inventario_deportivo.models import ArticuloDeportivo
from login.decorators import login_required_custom
@login_required_custom
def prestamos_para_devolucion(request):
    """Muestra préstamos APROBADOS que están listos para devolución"""
    if request.session.get("id_rol") != 100:
        messages.error(request, "Acceso denegado")
        return redirect('/login/')

    # Obtener préstamos aprobados
    prestamos = Prestamo.objects.filter(estado='APROBADO')
    
    prestamos_con_detalles = []
    
    for prestamo in prestamos:
        # Obtener detalles del préstamo
        detalles = DetallePrestamo.objects.filter(id_prestamo=prestamo.id_prestamo)
        
        # Obtener todas las devoluciones de este préstamo
        devoluciones = Devolucion.objects.filter(id_prestamo=prestamo.id_prestamo)
        devolucion_ids = [dev.id_devolucion for dev in devoluciones]
        
        detalles_con_info = []
        total_devuelto = 0
        total_requiere = 0
        
        for detalle in detalles:
            info_articulo = _obtener_info_articulo(detalle.tipo_articulo, detalle.id_articulo)
            requiere_devolucion = _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo)
            
            # Calcular cantidad ya devuelta
            cantidad_devuelta = 0
            if devolucion_ids:
                cantidad_devuelta = DetalleDevolucion.objects.filter(
                    id_devolucion__in=devolucion_ids,
                    tipo_articulo=detalle.tipo_articulo,
                    id_articulo=detalle.id_articulo
                ).aggregate(total=Sum('cantidad'))['total'] or 0
            
            pendiente_devolver = max(0, detalle.cantidad - cantidad_devuelta)
            
            detalles_con_info.append({
                'detalle': detalle,
                'info_articulo': info_articulo,
                'requiere_devolucion': requiere_devolucion,
                'cantidad_devuelta': cantidad_devuelta,
                'pendiente_devolver': pendiente_devolver,
                'ya_devuelto_completo': cantidad_devuelta >= detalle.cantidad
            })
            
            if requiere_devolucion:
                total_requiere += detalle.cantidad
                total_devuelto += cantidad_devuelta
        
        # Calcular porcentaje
        porcentaje = 0
        if total_requiere > 0:
            porcentaje = (total_devuelto / total_requiere) * 100
        
        prestamos_con_detalles.append({
            'prestamo': prestamo,
            'detalles': detalles_con_info,
            'total_devuelto': total_devuelto,
            'total_requiere': total_requiere,
            'porcentaje_devuelto': round(porcentaje, 2)
        })
    
    return render(request, 'devolucion_pendiente.html', {
        'prestamos_con_detalles': prestamos_con_detalles
    })
@login_required_custom
def registrar_devolucion_parcial(request, id_prestamo):
    """Registra devolución por artículo individual"""
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
                observaciones = request.POST.get('observaciones', '')
                
                # 1. Crear o obtener devolución principal
                devolucion, created = Devolucion.objects.get_or_create(
                    id_prestamo=id_prestamo,
                    defaults={
                        'fecha_devolucion': timezone.now().date(),
                        'observaciones': observaciones,
                        'cantidad_devuelta': 0
                    }
                )
                
                # 2. Obtener todas las devoluciones anteriores para calcular cantidades
                devoluciones_anteriores = Devolucion.objects.filter(id_prestamo=id_prestamo)
                todas_devoluciones_ids = [dev.id_devolucion for dev in devoluciones_anteriores]
                
                # 3. Procesar cada artículo del formulario
                items_procesados = 0
                for key, value in request.POST.items():
                    if key.startswith('cantidad_devuelta_'):
                        partes = key.split('_')
                        tipo_articulo = partes[2]
                        id_articulo = int(partes[3])
                        cantidad_devuelta = int(value)
                        
                        if cantidad_devuelta > 0:
                            try:
                                # Buscar el detalle del préstamo
                                detalle_prestamo = DetallePrestamo.objects.get(
                                    id_prestamo=id_prestamo,
                                    tipo_articulo=tipo_articulo,
                                    id_articulo=id_articulo
                                )
                                
                                # Calcular cantidad ya devuelta en todas las devoluciones
                                cantidad_ya_devuelta = 0
                                if todas_devoluciones_ids:
                                    cantidad_ya_devuelta = DetalleDevolucion.objects.filter(
                                        id_devolucion__in=todas_devoluciones_ids,
                                        tipo_articulo=tipo_articulo,
                                        id_articulo=id_articulo
                                    ).aggregate(total=Sum('cantidad'))['total'] or 0
                                
                                # Verificar que no se devuelva más de lo prestado
                                max_posible = detalle_prestamo.cantidad - cantidad_ya_devuelta
                                if max_posible <= 0:
                                    continue  # Ya está completamente devuelto
                                
                                cantidad_devuelta = min(cantidad_devuelta, max_posible)
                                
                                if cantidad_devuelta > 0:
                                    # Registrar en detalle_devolucion
                                    DetalleDevolucion.objects.create(
                                        id_devolucion=devolucion.id_devolucion,
                                        tipo_articulo=tipo_articulo,
                                        id_articulo=id_articulo,
                                        cantidad=cantidad_devuelta,
                                        estado_devolucion='DEVUELTO'
                                    )
                                    
                                    # Actualizar stock del artículo
                                    if _actualizar_stock_articulo(tipo_articulo, id_articulo, cantidad_devuelta):
                                        # Actualizar cantidad total devuelta en la devolución
                                        devolucion.cantidad_devuelta = (devolucion.cantidad_devuelta or 0) + cantidad_devuelta
                                        items_procesados += 1
                                    
                            except DetallePrestamo.DoesNotExist:
                                messages.warning(request, f"Artículo no encontrado en el préstamo #{id_prestamo}")
                                continue
                
                if items_procesados > 0:
                    devolucion.save()
                    
                    # 4. Actualizar estado del préstamo
                    nuevo_estado = _actualizar_estado_prestamo(id_prestamo)
                    
                    messages.success(request, f"✅ Devolución parcial registrada. {items_procesados} artículos procesados. Estado actual: {nuevo_estado}")
                else:
                    messages.warning(request, "⚠️ No se procesaron artículos para devolución")
                
        except Exception as e:
            messages.error(request, f"❌ Error al registrar devolución: {str(e)}")
    
    return redirect('gestionDevolucion:pendientes')
@login_required_custom
def registrar_devolucion_completa(request, id_prestamo):
    """Registra devolución completa de todos los artículos"""
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
                observaciones = request.POST.get('observaciones', '')
                
                # 1. Crear devolución principal
                devolucion = Devolucion.objects.create(
                    id_prestamo=id_prestamo,
                    fecha_devolucion=timezone.now().date(),
                    observaciones=observaciones,
                    cantidad_devuelta=0
                )
                
                # Obtener todas las devoluciones anteriores
                devoluciones_anteriores = Devolucion.objects.filter(id_prestamo=id_prestamo).exclude(id_devolucion=devolucion.id_devolucion)
                todas_devoluciones_ids = [dev.id_devolucion for dev in devoluciones_anteriores]
                
                detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
                total_devuelto = 0
                items_procesados = 0
                
                for detalle in detalles:
                    if _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo):
                        # Calcular cantidad ya devuelta
                        cantidad_ya_devuelta = 0
                        if todas_devoluciones_ids:
                            cantidad_ya_devuelta = DetalleDevolucion.objects.filter(
                                id_devolucion__in=todas_devoluciones_ids,
                                tipo_articulo=detalle.tipo_articulo,
                                id_articulo=detalle.id_articulo
                            ).aggregate(total=Sum('cantidad'))['total'] or 0
                        
                        cantidad_pendiente = detalle.cantidad - cantidad_ya_devuelta
                        
                        if cantidad_pendiente > 0:
                            # Registrar en detalle_devolucion
                            DetalleDevolucion.objects.create(
                                id_devolucion=devolucion.id_devolucion,
                                tipo_articulo=detalle.tipo_articulo,
                                id_articulo=detalle.id_articulo,
                                cantidad=cantidad_pendiente,
                                estado_devolucion='DEVUELTO'
                            )
                            
                            # Actualizar stock
                            if _actualizar_stock_articulo(detalle.tipo_articulo, detalle.id_articulo, cantidad_pendiente):
                                total_devuelto += cantidad_pendiente
                                items_procesados += 1
                
                # Actualizar cantidad total devuelta
                devolucion.cantidad_devuelta = total_devuelto
                devolucion.save()
                
                # Actualizar estado del préstamo
                nuevo_estado = _actualizar_estado_prestamo(id_prestamo)
                
                if items_procesados > 0:
                    messages.success(request, f"✅ Devolución completa registrada. {items_procesados} artículos devueltos ({total_devuelto} unidades). Estado: {nuevo_estado}")
                else:
                    messages.info(request, f"ℹ️ Todos los artículos ya estaban devueltos. Estado: {nuevo_estado}")
                
        except Exception as e:
            messages.error(request, f"❌ Error al registrar devolución: {str(e)}")
    
    return redirect('gestionDevolucion:pendientes')
@login_required_custom
def _obtener_info_articulo(tipo_articulo, id_articulo):
    """Obtiene información del artículo - VERSIÓN CORREGIDA"""
    try:
        if tipo_articulo == 'papeleria':
            articulo = ArticuloPapeleria.objects.get(id_papeleria=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Papelería'
            }
        elif tipo_articulo == 'hardware':
            articulo = ArticulosHardware.objects.get(id_hardware=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Hardware'
            }
        elif tipo_articulo == 'deportivo':  # Asegúrate que coincide
            articulo = ArticuloDeportivo.objects.get(id_deportivo=id_articulo)
            return {
                'nombre': articulo.nombre,
                'devolucion': articulo.devolucion,
                'tipo': 'Deportivo'
            }
        else:
            return {
                'nombre': f'Tipo desconocido: {tipo_articulo}',
                'devolucion': 'NO',
                'tipo': 'Desconocido'
            }
            
    except Exception as e:
        print(f"❌ Error obteniendo artículo {tipo_articulo} ID {id_articulo}: {e}")
        return {
            'nombre': f'Error: {str(e)[:50]}',
            'devolucion': 'NO',
            'tipo': 'Error'
        }
@login_required_custom
def _requiere_devolucion(tipo_articulo, id_articulo):
    """Determina si un artículo requiere devolución"""
    try:
        info_articulo = _obtener_info_articulo(tipo_articulo, id_articulo)
        return info_articulo['devolucion'].upper() == 'SI'
    except:
        return False
@login_required_custom
def _actualizar_stock_articulo(tipo_articulo, id_articulo, cantidad_devuelta):
    """Actualiza el stock cuando se devuelve un artículo - USANDO SQL"""
    try:
        # Importar la función de SQL
        from administradorBodega.utils.sql_helpers import actualizar_stock_sql
        
        # Usar SQL directo para SUMAR la cantidad devuelta
        resultado = actualizar_stock_sql(
            tipo_articulo, 
            id_articulo, 
            cantidad_devuelta, 
            operacion='SUMAR'
        )
        
        if resultado:
            print(f"✅ Stock actualizado: {cantidad_devuelta} unidades devueltas a {tipo_articulo} ID {id_articulo}")
            return True
        else:
            print(f"❌ Error actualizando stock de {tipo_articulo} ID {id_articulo}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en _actualizar_stock_articulo: {e}")
        return False
@login_required_custom
def _actualizar_estado_prestamo(id_prestamo):
    """Actualiza el estado del préstamo basado en devoluciones"""
    try:
        prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
        detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
        
        # Obtener todas las devoluciones de este préstamo
        devoluciones = Devolucion.objects.filter(id_prestamo=id_prestamo)
        devolucion_ids = [dev.id_devolucion for dev in devoluciones]
        
        total_requiere_devolucion = 0
        total_devuelto = 0
        
        for detalle in detalles:
            if _requiere_devolucion(detalle.tipo_articulo, detalle.id_articulo):
                total_requiere_devolucion += detalle.cantidad
                
                # Calcular cuánto se ha devuelto
                cantidad_devuelta = 0
                if devolucion_ids:
                    cantidad_devuelta = DetalleDevolucion.objects.filter(
                        id_devolucion__in=devolucion_ids,
                        tipo_articulo=detalle.tipo_articulo,
                        id_articulo=detalle.id_articulo
                    ).aggregate(total=Sum('cantidad'))['total'] or 0
                
                total_devuelto += cantidad_devuelta
        
        # Lógica de estados
        if total_requiere_devolucion == 0:
            # No hay artículos que requieran devolución
            prestamo.estado = 'FINALIZADO'
        elif total_devuelto >= total_requiere_devolucion:
            # Todo devuelto
            prestamo.estado = 'FINALIZADO'
        elif total_devuelto > 0:
            # Devuelto parcialmente
            prestamo.estado = 'DEVUELTO_PARCIAL'
        else:
            # Aún no se ha devuelto nada
            prestamo.estado = 'APROBADO'
        
        prestamo.save()
        return prestamo.estado
        
    except Prestamo.DoesNotExist:
        print(f"Préstamo #{id_prestamo} no encontrado")
        return 'ERROR'
    except Exception as e:
        print(f"Error actualizando estado del préstamo: {e}")
        return 'ERROR'