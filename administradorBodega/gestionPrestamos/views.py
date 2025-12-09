from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Prestamo, DetallePrestamo, ArticuloPapeleria, ArticuloHardware, ArticuloDeportivo
from login.decorators import login_required_custom
@login_required_custom
def prestamos_pendientes(request):
    if request.session.get("id_rol") != 100:
        messages.error(request, "Acceso denegado")
        return redirect('/login/')
    
    prestamos = Prestamo.objects.filter(estado__in=['PENDIENTE', 'RESERVA'])
    
    prestamos_con_detalles = []
    for prestamo in prestamos:
        detalles = DetallePrestamo.objects.filter(id_prestamo=prestamo.id_prestamo)
        
        detalles_con_info = []
        puede_aprobar = True  # Siempre True porque ya se verificó stock al crear
        
        for detalle in detalles:
            # Obtener información completa del artículo
            info_articulo = _obtener_info_articulo(detalle.tipo_articulo, detalle.id_articulo)
            
            detalles_con_info.append({
                'detalle': detalle,
                'info_articulo': info_articulo,
                # No verificamos disponibilidad porque ya se hizo al crear
            })
        
        prestamos_con_detalles.append({
            'prestamo': prestamo,
            'detalles': detalles_con_info,
            'puede_aprobar': True  # Siempre se puede aprobar (solo revisión administrativa)
        })
    
    return render(request, 'pendientes.html', {
        'prestamos_con_detalles': prestamos_con_detalles
    })
@login_required_custom
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
@login_required_custom
def aprobar_prestamo(request, id_prestamo):
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    try:
        prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
        
        # Verificar que esté en estado pendiente o reserva
        if prestamo.estado not in ['PENDIENTE', 'RESERVA']:
            messages.error(request, f"El préstamo ya está {prestamo.estado}")
            return redirect('gestionPrestamos:pendientes')
        
        # Cambiar estado a APROBADO (NO verificar stock - ya se hizo)
        prestamo.estado = 'APROBADO'
        prestamo.save()
        
        messages.success(request, f"✅ Préstamo #{id_prestamo} aprobado exitosamente")
            
    except Prestamo.DoesNotExist:
        messages.error(request, "❌ Préstamo no encontrado")
    
    return redirect('gestionPrestamos:pendientes')
@login_required_custom
def rechazar_prestamo(request, id_prestamo):
    if request.session.get("id_rol") != 100:
        return redirect('/login/')
    
    try:
        prestamo = Prestamo.objects.get(id_prestamo=id_prestamo)
        
        if prestamo.estado not in ['PENDIENTE', 'RESERVA']:
            messages.error(request, f"No se puede rechazar un préstamo {prestamo.estado}")
            return redirect('gestionPrestamos:pendientes')
        
        # Cambiar estado a RECHAZADO
        prestamo.estado = 'RECHAZADO'
        prestamo.save()
        
        # DEVOLVER ARTÍCULOS AL INVENTARIO
        detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
        devueltos = 0
        errores = 0
        
        for detalle in detalles:
            if _devolver_articulo_inventario(
                detalle.tipo_articulo,
                detalle.id_articulo,
                detalle.cantidad
            ):
                devueltos += 1
            else:
                errores += 1
        
        if errores == 0:
            messages.success(request, f"❌ Préstamo #{id_prestamo} rechazado. {devueltos} artículos devueltos al inventario.")
        else:
            messages.warning(request, f"❌ Préstamo #{id_prestamo} rechazado. {devueltos} artículos devueltos, {errores} con problemas.")
        
    except Prestamo.DoesNotExist:
        messages.error(request, "Préstamo no encontrado")
    
    return redirect('gestionPrestamos:pendientes')
@login_required_custom
def _devolver_articulo_inventario(tipo_articulo, id_articulo, cantidad):
    """Devuelve artículos al inventario cuando se rechaza un préstamo"""
    try:
        # Importar la función de utilidad (puedes mover esta importación al inicio del archivo)
        from administradorBodega.utils.sql_helpers import actualizar_stock_sql
        
        # Usar SQL directo para actualizar el inventario
        if actualizar_stock_sql(tipo_articulo, id_articulo, cantidad, operacion='SUMAR'):
            print(f"✅ Artículo {tipo_articulo} ID {id_articulo}: Devueltas {cantidad} unidades")
            return True
        else:
            print(f"❌ Error devolviendo artículo {tipo_articulo} ID {id_articulo}")
            return False
            
    except Exception as e:
        print(f"Error en _devolver_articulo_inventario: {e}")
        return False