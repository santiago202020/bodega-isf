# docente/menuDocente/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Sum, Q
from login.decorators import login_required_custom

# Importaciones basadas en tus tablas - AJUSTA ESTAS IMPORTACIONES SEGÚN TU PROYECTO
try:
    # Intenta importar desde los modelos de tu aplicación de préstamos
    from solicitarPrestamo.models import Prestamo, DetallePrestamo
except ImportError:
    # Si no existe esa app, intenta importar directamente
    from .models import Prestamo, DetallePrestamo

try:
    # Intenta importar modelos de devolución si existen
    from .models import Devolucion
    from .models import DetalleDevolucion
except ImportError:
    # Si no existe la app de devoluciones, crea clases vacías
    class Devolucion:
        objects = type('obj', (object,), {
            'filter': lambda **kwargs: type('obj', (object,), {
                'values_list': lambda *args, **kwargs: []
            })()
        })()
    
    class DetalleDevolucion:
        objects = type('obj', (object,), {
            'filter': lambda **kwargs: type('obj', (object,), {
                'aggregate': lambda **kwargs: {}
            })()
        })()

@login_required_custom
def menu_docente(request):
    """
    Vista principal del menú del docente con estadísticas reales
    """
    # Verificar rol manualmente
    if request.session.get('id_rol') != 200:
        messages.error(request, "Acceso denegado. Solo para docentes.")
        return redirect('/login/')
    
    # Obtener ID del usuario actual
    usuario_id = request.session.get('id_usuario')
    
    if not usuario_id:
        messages.error(request, "No se pudo identificar al usuario.")
        return redirect('/login/')
    
    # ESTADÍSTICAS DEL DOCENTE - USANDO TUS TABLAS EXACTAS
    try:
        # Obtener todos los préstamos del docente desde la tabla 'prestamo'
        prestamos_docente = Prestamo.objects.filter(id_usuario=usuario_id)
        
        # CONTAR POR ESTADO según los valores posibles en tu campo 'estado'
        # Ajusta estos filtros según los valores reales en tu base de datos
        prestamos_pendientes = prestamos_docente.filter(
            Q(estado='PENDIENTE') | Q(estado='RESERVA')
        ).count()
        
        prestamos_aceptados = prestamos_docente.filter(
            Q(estado='APROBADO') | Q(estado='EN CURSO') | Q(estado='ACEPTADO') |
            Q(estado='EN_PROCESO') | Q(estado='ACTIVO')
        ).count()
        
        prestamos_finalizados = prestamos_docente.filter(
            Q(estado='FINALIZADO') | Q(estado='COMPLETADO') | 
            Q(estado='DEVUELTO') | Q(estado='TERMINADO')
        ).count()
        
        total_prestamos = prestamos_docente.count()
        
        # Calcular el total de artículos prestados desde 'detalle_prestamo'
        # Primero obtenemos los IDs de los préstamos del docente
        ids_prestamos = list(prestamos_docente.values_list('id_prestamo', flat=True))
        
        if ids_prestamos:
            # Buscamos en detalle_prestamo usando el id_prestamo
            detalles_prestamo = DetallePrestamo.objects.filter(
                id_prestamo__in=ids_prestamos
            )
            
            total_articulos_prestados = detalles_prestamo.aggregate(
                total=Sum('cantidad')
            )['total'] or 0
            
            # Estadísticas por tipo de artículo desde 'tipo_articulo' en detalle_prestamo
            papeleria_count = detalles_prestamo.filter(
                tipo_articulo='papeleria'
            ).aggregate(
                total=Sum('cantidad')
            )['total'] or 0
            
            hardware_count = detalles_prestamo.filter(
                tipo_articulo='hardware'
            ).aggregate(
                total=Sum('cantidad')
            )['total'] or 0
            
            deportivo_count = detalles_prestamo.filter(
                tipo_articulo='deportivo'
            ).aggregate(
                total=Sum('cantidad')
            )['total'] or 0
        else:
            # Si no tiene préstamos, poner todo en 0
            total_articulos_prestados = 0
            papeleria_count = 0
            hardware_count = 0
            deportivo_count = 0
        
        # Obtener últimos préstamos para mostrar
        ultimos_prestamos = prestamos_docente.order_by('-fecha_prestamo', '-hora_prestamo')[:5]
        
        # Verificar si hay préstamos activos
        tiene_prestamos_activos = prestamos_docente.filter(
            Q(estado='PENDIENTE') | Q(estado='RESERVA') | 
            Q(estado='APROBADO') | Q(estado='EN CURSO') |
            Q(estado='ACEPTADO') | Q(estado='EN_PROCESO')
        ).exists()
        
        # Verificar préstamos que necesitan devolución (usando tabla 'devolucion')
        try:
            prestamos_por_devolver = 0
            # Solo si la tabla Devolucion existe
            if hasattr(Devolucion.objects, 'filter'):
                prestamos_por_devolver = prestamos_docente.filter(
                    Q(estado='APROBADO') | Q(estado='EN CURSO'),
                    id_prestamo__in=Devolucion.objects.filter(
                        observaciones__icontains='pendiente'
                    ).values_list('id_prestamo', flat=True)
                ).count()
        except:
            prestamos_por_devolver = 0
        
        # Contexto para la plantilla
        context = {
            # Información de sesión
            'usuario_nombre': request.session.get('nombre', 'Docente'),
            'usuario_id': usuario_id,
            'usuario_rol': request.session.get('rol', 'Docente'),
            
            # Estadísticas principales
            'prestamos_pendientes': prestamos_pendientes,
            'prestamos_aceptados': prestamos_aceptados,
            'prestamos_finalizados': prestamos_finalizados,
            'total_prestamos': total_prestamos,
            'total_articulos_prestados': total_articulos_prestados,
            
            # Estadísticas por tipo
            'papeleria_count': papeleria_count,
            'hardware_count': hardware_count,
            'deportivo_count': deportivo_count,
            
            # Información adicional
            'tiene_prestamos_activos': tiene_prestamos_activos,
            'prestamos_por_devolver': prestamos_por_devolver,
            'ultimos_prestamos': ultimos_prestamos,
            
            # Fecha actual
            'fecha_actual': "hoy",
        }
        
    except Exception as e:
        # En caso de error, mostrar error en consola y usar valores por defecto
        print(f"ERROR en menu_docente: {str(e)}")
        import traceback
        traceback.print_exc()
        
        context = {
            'usuario_nombre': request.session.get('nombre', 'Docente'),
            'usuario_id': usuario_id,
            'usuario_rol': request.session.get('rol', 'Docente'),
            'prestamos_pendientes': 0,
            'prestamos_aceptados': 0,
            'prestamos_finalizados': 0,
            'total_prestamos': 0,
            'total_articulos_prestados': 0,
            'papeleria_count': 0,
            'hardware_count': 0,
            'deportivo_count': 0,
            'tiene_prestamos_activos': False,
            'prestamos_por_devolver': 0,
            'ultimos_prestamos': [],
            'fecha_actual': "hoy",
            'error_estadisticas': True,
        }
        messages.warning(request, "No se pudieron cargar todas las estadísticas.")
    
    return render(request, "menuDocente.html", context)