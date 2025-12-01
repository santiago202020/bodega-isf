from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from datetime import date
from .models import (
    ArticuloPapeleria, ArticuloHardware, ArticuloDeportivo,
    Prestamo, DetallePrestamo
)

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
    papeleria = ArticuloPapeleria.objects.all()
    hardware = ArticuloHardware.objects.all()
    deportivos = ArticuloDeportivo.objects.all()
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

    bolsa = _inicializar_bolsa(request)
    existente = int(bolsa.get(categoria, {}).get(str(art_id), 0))
    stock_actual = art.cantidad_total or 0

    if existente + cantidad > stock_actual:
        messages.error(request, f"No hay suficiente stock de {art.nombre}. Disponible: {stock_actual - existente}")
        return redirect(reverse('solicitarPrestamo:seleccionar'))

    bolsa[categoria][str(art_id)] = existente + cantidad
    request.session['bolsa'] = bolsa
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
    if art_id in bolsa.get(categoria, {}):
        del bolsa[categoria][art_id]
        request.session['bolsa'] = bolsa
        messages.success(request, "Eliminado de la bolsa.")

    return redirect(reverse('solicitarPrestamo:bolsa_ver'))

def ver_bolsa(request):
    if not _es_docente(request):
        return redirect('/login/')

    bolsa = _inicializar_bolsa(request)
    items = []

    for cat, mapping in bolsa.items():
        for aid_str, qty in mapping.items():
            aid = int(aid_str)
            art = _get_art_by_cat(cat, aid)
            if art:
                items.append({'categoria': cat, 'art': art, 'cantidad': qty})

    return render(request, "bolsa.html", {'items': items})

def confirmar_solicitud(request):
    if request.method != 'POST' or not _es_docente(request):
        return redirect('/login/')

    bolsa = _inicializar_bolsa(request)
    usuario_id = request.session.get('id_usuario')

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

    # validar stock antes de crear
    for cat, mapping in bolsa.items():
        for aid_str, qty in mapping.items():
            aid = int(aid_str)
            art = _get_art_by_cat(cat, aid)
            if not art:
                messages.error(request, "Artículo no encontrado al confirmar.")
                return redirect(reverse('solicitarPrestamo:bolsa_ver'))

            stock_actual = art.cantidad_total or 0
            if qty > stock_actual:
                messages.error(request, f"Stock insuficiente para {art.nombre}. Disponible: {stock_actual}")
                return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    # parse fecha
    try:
        fi = timezone.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    except:
        messages.error(request, "Formato de fecha inválido.")
        return redirect(reverse('solicitarPrestamo:bolsa_ver'))

    estado_inicial = 'RESERVA' if fi > date.today() else 'PENDIENTE'

    # CREAR PRESTAMO
    prestamo = Prestamo.objects.create(
        id_usuario=usuario_id,
        estado=estado_inicial,
        observaciones=observaciones,
        fecha_inicio=fi,
        hora_inicio=hora_inicio,

        hora_fin=hora_fin
    )

    # CREAR DETALLES
    for cat, mapping in bolsa.items():
        for aid_str, qty in mapping.items():
            aid = int(aid_str)
            DetallePrestamo.objects.create(
                id_prestamo=prestamo.id_prestamo,
                tipo_articulo=cat,
                id_articulo=aid,
                cantidad=qty,
                estado_detalle='SOLICITADO'
            )

    # limpiar bolsa
    request.session['bolsa'] = {'papeleria': {}, 'hardware': {}, 'deportivo': {}}
    messages.success(request, f"Reserva creada (ID {prestamo.id_prestamo}) con estado {estado_inicial}.")
    return redirect(reverse('solicitarPrestamo:historial'))

def historial(request):
    if not _es_docente(request):
        return redirect('/login/')

    usuario_id = request.session.get('id_usuario')
    prestamos = Prestamo.objects.filter(id_usuario=usuario_id).order_by('-id_prestamo')

    return render(request, "historial.html", {'prestamos': prestamos})

def detalle(request, id_prestamo):
    if not _es_docente(request):
        return redirect('/login/')

    prestamo = get_object_or_404(Prestamo, pk=id_prestamo)

    if prestamo.id_usuario != request.session.get('id_usuario'):
        messages.error(request, "No tiene permiso para ver esta solicitud.")
        return redirect(reverse('solicitarPrestamo:historial'))

    detalles = DetallePrestamo.objects.filter(id_prestamo=id_prestamo)
    detalles_enriquecidos = []

    for d in detalles:
        art = _get_art_by_cat(d.tipo_articulo, d.id_articulo)
        detalles_enriquecidos.append({'detalle': d, 'art': art})

    return render(request, "detalle.html", {'prestamo': prestamo, 'detalles': detalles_enriquecidos})
