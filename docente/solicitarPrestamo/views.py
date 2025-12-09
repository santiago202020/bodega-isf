from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import date, datetime
from .models import (
    ArticuloPapeleria, ArticuloHardware, ArticuloDeportivo,
    Prestamo, DetallePrestamo
)
from administradorBodega.utils.sql_helpers import actualizar_stock_sql

# ----- helpers -----
def _es_docente(request):
    return request.session.get("id_rol") == 200 and request.session.get("id_usuario") is not None

def _inicializar_bolsa(request):
    bolsa = request.session.get('bolsa')
    if not bolsa:
        bolsa = {'papeleria': {}, 'hardware': {}, 'deportivo': {}}
        request.session['bolsa'] = bolsa
    return bolsa

def _get_art_by_cat(cat, aid):
    if cat == 'papeleria':
        return ArticuloPapeleria.objects.filter(pk=aid).first()
    if cat == 'hardware':
        return ArticuloHardware.objects.filter(pk=aid).first()
    return ArticuloDeportivo.objects.filter(pk=aid).first()

# ----- vistas -----
def menu_docente(request):
    return redirect(reverse('solicitarPrestamo:seleccionar'))

def seleccionar_articulos(request):
    if not _es_docente(request):
        messages.error(request, "Acceso denegado.")
        return redirect('/login/')
    
    # Solo mostrar artículos DISPONIBLES
    papeleria = ArticuloPapeleria.objects.filter(estado='DISPONIBLE')
    hardware = ArticuloHardware.objects.filter(estado='DISPONIBLE')
    deportivos = ArticuloDeportivo.objects.filter(estado='DISPONIBLE')
    
    usuario_id = request.session.get('id_usuario')
    return render(request, "crear.html", {
        "papeleria": papeleria,
        "hardware": hardware,
        "deportivos": deportivos,
        "usuario_id": usuario_id,
    })

def add_to_bolsa(request):
    if request.method != 'POST' or not _es_docente(request):
        return redirect('/login/')

    categoria = request.POST.get('categoria')
    try:
        art_id = int(request.POST.get('art_id'))
        cantidad = int(request.POST.get('cantidad'))
    except:
        messages.error(request, "Datos inválidos.")
        return redirect(reverse('solicitarPrestamo:seleccionar'))

    if cantidad <= 0:
        messages.error(request, "Seleccione una cantidad mayor a 0.")
        return redirect(reverse('solicitarPrestamo:seleccionar'))

    art = _get_art_by_cat(categoria, art_id)
    if not art:
        messages.error(request, "Artículo no encontrado.")
        return redirect(reverse('solicitarPrestamo:seleccionar'))
    
    # Verificar que el artículo esté DISPONIBLE
    if art.estado != 'DISPONIBLE':
        messages.error(request, f"El artículo {art.nombre} no está disponible.")
        return redirect(reverse('solicitarPrestamo:seleccionar'))

    bolsa = _inicializar_bolsa(request)
    existente = int(bolsa.get(categoria, {}).get(str(art_id), 0))
    stock_actual = art.cantidad_total or 0

    if existente + cantidad > stock_actual:
        messages.error(request, f"No hay suficiente stock de {art.nombre}. Disponible: {stock_actual - existente}")
        return redirect(reverse('solicitarPrestamo:seleccionar'))

    bolsa[categoria][str(art_id)] = existente + cantidad
    request.session['bolsa'] = bolsa
    request.session.modified = True  # Asegurar que se guarde la sesión
    messages.success(request, f"Añadido {cantidad} x {art.nombre} a la bolsa.")
    return redirect(reverse('solicitarPrestamo:seleccionar'))

def remove_from_bolsa(request):
    if request.method != 'POST' or not _es_docente(request):
        return redirect('/login/')

    categoria = request.POST.get('categoria')
    try:
        art_id = str(int(request.POST.get('art_id')))
    except:
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    bolsa = _inicializar_bolsa(request)
    if categoria in bolsa and art_id in bolsa[categoria]:
        del bolsa[categoria][art_id]
        request.session['bolsa'] = bolsa
        request.session.modified = True
        messages.success(request, "Eliminado de la bolsa.")

    return redirect(reverse('solicitarPrestamo:bolsa_ver'))

def ver_bolsa(request):
    if not _es_docente(request):
        return redirect('/login/')

    bolsa = _inicializar_bolsa(request)
    items = []
    total_articulos = 0

    for cat, mapping in bolsa.items():
        for aid_str, qty in mapping.items():
            aid = int(aid_str)
            art = _get_art_by_cat(cat, aid)
            if art:
                items.append({
                    'categoria': cat, 
                    'art': art, 
                    'cantidad': qty,
                    'subtotal': qty
                })
                total_articulos += qty

    return render(request, "bolsa.html", {
        'items': items,
        'total_articulos': total_articulos,
        'bolsa_vacia': len(items) == 0
    })

def confirmar_solicitud(request):
    if request.method != 'POST' or not _es_docente(request):
        return redirect('/login/')

    bolsa = _inicializar_bolsa(request)
    usuario_id = request.session.get('id_usuario')

    # Verificar que la bolsa no esté vacía
    if not any(bolsa.values()):
        messages.error(request, "La bolsa está vacía. Agregue artículos antes de confirmar.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    fecha_inicio = request.POST.get('fecha_inicio')
    hora_inicio = request.POST.get('hora_inicio')
    hora_fin = request.POST.get('hora_fin')
    observaciones = request.POST.get('observaciones', '')

    if not fecha_inicio or not hora_inicio:
        messages.error(request, "Debe especificar fecha y hora de inicio.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    if not hora_fin:
        messages.error(request, "Debe especificar la hora de fin.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # Parsear fecha
    try:
        fi = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    except:
        messages.error(request, "Formato de fecha inválido. Use YYYY-MM-DD")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # Validar que la fecha de inicio no sea en el pasado
    if fi < date.today():
        messages.error(request, "La fecha de inicio no puede ser en el pasado.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # Validar que hora_fin sea mayor que hora_inicio
    try:
        hora_inicio_dt = datetime.strptime(hora_inicio, "%H:%M").time()
        hora_fin_dt = datetime.strptime(hora_fin, "%H:%M").time()
        if hora_fin_dt <= hora_inicio_dt:
            messages.error(request, "La hora de fin debe ser posterior a la hora de inicio.")
            return redirect(reverse('solicitarPrestamo:bolsa_ver'))
    except:
        messages.error(request, "Formato de hora inválido. Use HH:MM (24h)")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # Validar stock antes de crear (transacción manual)
    errors = []
    for cat, mapping in bolsa.items():
        for aid_str, qty in mapping.items():
            aid = int(aid_str)
            art = _get_art_by_cat(cat, aid)
            if not art:
                errors.append(f"Artículo ID {aid} no encontrado en {cat}.")
                continue

            # Verificar estado DISPONIBLE
            if art.estado != 'DISPONIBLE':
                errors.append(f"El artículo {art.nombre} no está disponible.")
                continue

            stock_actual = art.cantidad_total or 0
            if qty > stock_actual:
                errors.append(f"Stock insuficiente para {art.nombre}. Disponible: {stock_actual}")

    if errors:
        for error in errors[:5]:  # Mostrar máximo 5 errores
            messages.error(request, error)
        if len(errors) > 5:
            messages.error(request, f"... y {len(errors)-5} errores más.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # Determinar estado inicial
    hoy = date.today()
    if fi > hoy:
        estado_inicial = 'RESERVA'
    elif fi == hoy:
        estado_inicial = 'PENDIENTE'
    else:
        estado_inicial = 'PENDIENTE'  # Por si acaso

    try:
        # PRIMERO: Crear el préstamo
        prestamo = Prestamo.objects.create(
            id_usuario=usuario_id,
            fecha_prestamo=date.today(),  # Fecha actual
            hora_prestamo=datetime.now().time(),  # Hora actual
            estado=estado_inicial,
            observaciones=observaciones,
            fecha_inicio=fi,
            hora_inicio=hora_inicio_dt,
            hora_fin=hora_fin_dt
        )

        # SEGUNDO: Procesar artículos y actualizar inventario
        errores_actualizacion = []
        detalles_creados = []
        
        for cat, mapping in bolsa.items():
            for aid_str, qty in mapping.items():
                aid = int(aid_str)
                
                try:
                    # 1. Actualizar inventario con SQL directo
                    if not actualizar_stock_sql(cat, aid, qty, operacion='RESTAR'):
                        errores_actualizacion.append(f"Error al actualizar inventario para artículo ID {aid}")
                        continue
                    
                    # 2. Crear detalle de préstamo
                    detalle = DetallePrestamo.objects.create(
                        id_prestamo=prestamo.id_prestamo,
                        tipo_articulo=cat,
                        id_articulo=aid,
                        cantidad=qty,
                        estado_detalle='PRESTADO'
                    )
                    detalles_creados.append(detalle)
                    
                except Exception as e:
                    errores_actualizacion.append(f"Error procesando artículo {aid}: {str(e)}")
        
        # Si hubo errores, revertir todo
        if errores_actualizacion:
            # 1. Eliminar detalles creados
            for detalle in detalles_creados:
                detalle.delete()
            
            # 2. Eliminar préstamo
            prestamo.delete()
            
            # 3. Mostrar errores
            for error in errores_actualizacion[:3]:
                messages.error(request, error)
            if len(errores_actualizacion) > 3:
                messages.error(request, f"... y {len(errores_actualizacion)-3} errores más.")
            
            # 4. Revertir cambios en inventario (devolver lo restado)
            for cat, mapping in bolsa.items():
                for aid_str, qty in mapping.items():
                    aid = int(aid_str)
                    # Intentar devolver el stock
                    try:
                        actualizar_stock_sql(cat, aid, qty, operacion='SUMAR')
                    except:
                        pass  # Si falla, al menos loguear
                        
            return redirect(reverse('solicitarPrestamo:bolsa_ver'))
        
        # TERCERO: Limpiar bolsa si todo salió bien
        request.session['bolsa'] = {'papeleria': {}, 'hardware': {}, 'deportivo': {}}
        request.session.modified = True
        
        messages.success(request, f"¡Préstamo #{prestamo.id_prestamo} creado exitosamente! Estado: {estado_inicial}")
        return redirect(reverse('solicitarPrestamo:historial'))

    except Exception as e:
        # Si hay error general, intentar revertir
        messages.error(request, f"Error al crear el préstamo: {str(e)}")
        
        # Intentar revertir cambios en inventario
        try:
            for cat, mapping in bolsa.items():
                for aid_str, qty in mapping.items():
                    aid = int(aid_str)
                    actualizar_stock_sql(cat, aid, qty, operacion='SUMAR')
        except:
            pass
            
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))
def historial(request):
    if not _es_docente(request):
        return redirect('/login/')

    usuario_id = request.session.get('id_usuario')
    prestamos = Prestamo.objects.filter(id_usuario=usuario_id).order_by('-id_prestamo')
    
    # Enriquecer con detalles
    prestamos_con_detalles = []
    for prestamo in prestamos:
        detalles = DetallePrestamo.objects.filter(id_prestamo=prestamo.id_prestamo)
        prestamos_con_detalles.append({
            'prestamo': prestamo,
            'total_articulos': sum(d.cantidad for d in detalles)
        })
    
    return render(request, "historial.html", {
        'prestamos': prestamos_con_detalles,
        'hoy': date.today()
    })

def detalle(request, id_prestamo):
    if not _es_docente(request):
        return redirect('/login/')

    prestamo = get_object_or_404(Prestamo, pk=id_prestamo)

    if prestamo.id_usuario != request.session.get('id_usuario'):
        messages.error(request, "No tiene permiso para ver esta solicitud.")
        return redirect(reverse('solicitarPrestamo:historial'))

    detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
    detalles_enriquecidos = []
    total_cantidad = 0

    for d in detalles:
        art = _get_art_by_cat(d.tipo_articulo, d.id_articulo)
        if art:
            detalles_enriquecidos.append({
                'detalle': d, 
                'art': art,
                'subtotal': d.cantidad
            })
            total_cantidad += d.cantidad

    return render(request, "detalle.html", {
        'prestamo': prestamo, 
        'detalles': detalles_enriquecidos,
        'total_cantidad': total_cantidad,
        'hoy': date.today()
    })