# reportes/views.py
from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.template.loader import render_to_string
from weasyprint import HTML
import datetime
import json
from login.decorators import rol_required
from .forms import FiltroReporteForm


@rol_required([100])
def reportes_principal(request):
    """
    Vista principal de reportes - Solo para administradores (rol 100)
    Primero muestra resultados en HTML, luego permite descargar PDF
    """
    form = FiltroReporteForm(request.GET or None)
    context = {'form': form, 'mostrar_resultados': False}
    
    print("=" * 50)
    print("Request GET:", request.GET)
    
    if form.is_valid():
        print("Formulario VÁLIDO")
        print("Filtros limpios:", form.cleaned_data)
        
        tipo_reporte = form.cleaned_data['tipo_reporte']
        
        # Verificar si se solicitó PDF
        if 'generar_pdf' in request.GET:
            print("Generando PDF...")
            datos = obtener_datos_filtrados(form.cleaned_data)
            return generar_pdf(request, datos, form.cleaned_data)
        else:
            print("Mostrando vista previa...")
            # Mostrar vista previa en HTML
            datos = obtener_datos_filtrados(form.cleaned_data)
            print("Total registros obtenidos:", datos.get('total_registros', 0))
            
            # Agregar datos al contexto
            context.update(datos)
            context['mostrar_resultados'] = True
            context['filtros_aplicados'] = form.cleaned_data
            
    else:
        print("Formulario INVÁLIDO")
        print("Errores:", form.errors)
    
    print("Contexto enviado:", context.keys())
    print("=" * 50)
    
    return render(request, 'reportes/reportes_principal.html', context)


def obtener_datos_filtrados(filtros):
    """Obtiene datos filtrados para reportes"""
    
    with connection.cursor() as cursor:
        condiciones = []
        params = []
        
        # Construir condiciones básicas
        if filtros.get('fecha_desde'):
            condiciones.append("p.fecha_prestamo >= %s")
            params.append(filtros['fecha_desde'])
        
        if filtros.get('fecha_hasta'):
            condiciones.append("p.fecha_prestamo <= %s")
            params.append(filtros['fecha_hasta'])
        
        if filtros.get('id_usuario'):
            condiciones.append("p.id_usuario = %s")
            params.append(filtros['id_usuario'])
        
        if filtros.get('estado_prestamo') and filtros['estado_prestamo']:
            condiciones.append("p.estado = %s")
            params.append(filtros['estado_prestamo'])
        
        where_clause = ""
        if condiciones:
            where_clause = "AND " + " AND ".join(condiciones)
        
        # CONSULTA PARA PRÉSTAMOS
        if filtros['tipo_reporte'] == 'prestamos':
            query = f"""
                SELECT 
                    p.id_prestamo,
                    p.id_usuario,
                    CONCAT(u.nombres, ' ', u.apellidos) as docente,
                    p.fecha_prestamo,
                    p.hora_prestamo,
                    p.estado,
                    p.hora_inicio,
                    p.hora_fin,
                    p.observaciones,
                    COUNT(dp.id_detalle) as total_articulos,
                    r.tipo_rol
                FROM prestamo p
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                JOIN rol r ON u.id_rol = r.id_rol
                LEFT JOIN detalle_prestamo dp ON p.id_prestamo = dp.id_prestamo
                WHERE u.id_rol = 200
                {where_clause}
                GROUP BY p.id_prestamo, u.nombres, u.apellidos, r.tipo_rol
                ORDER BY p.fecha_prestamo DESC
            """
        
        # CONSULTA PARA DEVOLUCIONES
        elif filtros['tipo_reporte'] == 'devoluciones':
            condiciones_dev = ["u.id_rol = 200"]
            params_dev = []
            
            if filtros.get('fecha_desde'):
                condiciones_dev.append("d.fecha_devolucion >= %s")
                params_dev.append(filtros['fecha_desde'])
            
            if filtros.get('fecha_hasta'):
                condiciones_dev.append("d.fecha_devolucion <= %s")
                params_dev.append(filtros['fecha_hasta'])
            
            if filtros.get('id_usuario'):
                condiciones_dev.append("p.id_usuario = %s")
                params_dev.append(filtros['id_usuario'])
            
            where_dev = " WHERE " + " AND ".join(condiciones_dev) if condiciones_dev else ""
            
            query = f"""
                SELECT 
                    d.id_devolucion,
                    d.id_prestamo,
                    CONCAT(u.nombres, ' ', u.apellidos) as docente,
                    d.fecha_devolucion,
                    d.cantidad_devuelta,
                    d.observaciones as obs_devolucion,
                    p.estado as estado_prestamo,
                    p.fecha_prestamo,
                    COUNT(dd.id_detalle_devolucion) as articulos_devueltos,
                    r.tipo_rol
                FROM devolucion d
                JOIN prestamo p ON d.id_prestamo = p.id_prestamo
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                JOIN rol r ON u.id_rol = r.id_rol
                LEFT JOIN detalle_devolucion dd ON d.id_devolucion = dd.id_devolucion
                {where_dev}
                GROUP BY d.id_devolucion, p.id_prestamo, u.nombres, u.apellidos, 
                         d.fecha_devolucion, d.cantidad_devuelta, d.observaciones,
                         p.estado, p.fecha_prestamo, r.tipo_rol
                ORDER BY d.fecha_devolucion DESC
            """
            params = params_dev
        
        # CONSULTA COMBINADA
        else:
            where_combined = ""
            if condiciones:
                where_combined = f"WHERE {condiciones[0]}"
                for cond in condiciones[1:]:
                    where_combined += f" AND {cond}"
            
            query = f"""
                -- Préstamos
                SELECT 
                    'PRÉSTAMO' as tipo_operacion,
                    p.id_prestamo as id_operacion,
                    CONCAT(u.nombres, ' ', u.apellidos) as docente,
                    p.fecha_prestamo as fecha,
                    p.estado,
                    p.observaciones,
                    COUNT(dp.id_detalle) as total_articulos,
                    NULL as cantidad_devuelta,
                    r.tipo_rol
                FROM prestamo p
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                JOIN rol r ON u.id_rol = r.id_rol
                LEFT JOIN detalle_prestamo dp ON p.id_prestamo = dp.id_prestamo
                WHERE u.id_rol = 200
                {where_clause if condiciones else ''}
                GROUP BY p.id_prestamo, u.nombres, u.apellidos, p.estado, p.observaciones, r.tipo_rol
                
                UNION ALL
                
                -- Devoluciones
                SELECT 
                    'DEVOLUCIÓN' as tipo_operacion,
                    d.id_devolucion as id_operacion,
                    CONCAT(u.nombres, ' ', u.apellidos) as docente,
                    d.fecha_devolucion as fecha,
                    p.estado,
                    d.observaciones,
                    COUNT(dd.id_detalle_devolucion) as total_articulos,
                    d.cantidad_devuelta,
                    r.tipo_rol
                FROM devolucion d
                JOIN prestamo p ON d.id_prestamo = p.id_prestamo
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                JOIN rol r ON u.id_rol = r.id_rol
                LEFT JOIN detalle_devolucion dd ON d.id_devolucion = dd.id_devolucion
                WHERE u.id_rol = 200
                GROUP BY d.id_devolucion, p.id_prestamo, u.nombres, u.apellidos, 
                         d.fecha_devolucion, d.cantidad_devuelta, d.observaciones, 
                         p.estado, r.tipo_rol
                
                ORDER BY fecha DESC
            """
        
        # Ejecutar consulta
        print(f"Ejecutando query: {query[:200]}...")
        print(f"Parámetros: {params}")
        
        cursor.execute(query, params)
        columnas = [col[0] for col in cursor.description]
        resultados = []
        
        for row in cursor.fetchall():
            fila = {}
            for i, valor in enumerate(row):
                nombre_columna = columnas[i]
                # Formatear fechas y horas en Python
                if valor is None:
                    fila[nombre_columna] = ''
                elif isinstance(valor, (datetime.date, datetime.datetime)):
                    fila[nombre_columna] = valor.strftime('%d/%m/%Y')
                elif isinstance(valor, datetime.time):
                    fila[nombre_columna] = valor.strftime('%H:%M:%S')
                else:
                    fila[nombre_columna] = str(valor)
            resultados.append(fila)
        
        print(f"Total resultados obtenidos: {len(resultados)}")
        
        return {
            'resultados': resultados,
            'total_registros': len(resultados),
            'filtros_aplicados': filtros
        }


def generar_pdf(request, datos, filtros):
    """Genera y devuelve un PDF con los datos filtrados"""
    
    print("Iniciando generación de PDF...")
    
    # Agregar información del usuario que genera el reporte
    datos['usuario_generador'] = request.session.get('nombre', 'Administrador')
    datos['rol_generador'] = request.session.get('rol', 'Administrador')
    datos['fecha_generacion'] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Renderizar template HTML
    html_string = render_to_string('reportes/reporte_pdf.html', datos)
    
    # Crear PDF
    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf_file = html.write_pdf()
        print("PDF generado exitosamente")
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        return HttpResponse(f"Error al generar PDF: {str(e)}")
    
    # Crear respuesta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    
    # Nombre del archivo
    fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tipo_reporte_nombre = {
        'prestamos': 'prestamos',
        'devoluciones': 'devoluciones',
        'combinado': 'combinado'
    }
    tipo = filtros['tipo_reporte']
    nombre_tipo = tipo_reporte_nombre.get(tipo, 'reporte')
    nombre_archivo = f"reporte_{nombre_tipo}_{fecha_actual}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    print(f"PDF listo para descargar: {nombre_archivo}")
    
    return response