# administradorBodega/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from login.decorators import login_required_custom

@login_required_custom
def menu_view(request):
    """
    Vista principal del administrador con estadísticas
    """
    # Verificar que sea administrador (ajusta el ID de rol según tu sistema)
    if request.session.get('id_rol') != 100:  # 100 = admin
        messages.error(request, "Acceso denegado. Solo para administradores.")
        return redirect('/login/')
    
    # Variables para estadísticas
    solicitudes_pendientes = 0
    prestamos_en_curso = 0
    devoluciones_pendientes = 0
    total_mes = 0
    total_prestamos = 0
    ultimas_solicitudes = []
    
    try:
        # USAR SQL DIRECTO para evitar problemas de importación
        with connection.cursor() as cursor:
            # 1. Contar solicitudes pendientes
            cursor.execute("""
                SELECT COUNT(*) FROM prestamo 
                WHERE estado IN ('PENDIENTE', 'RESERVA')
            """)
            solicitudes_pendientes = cursor.fetchone()[0]
            
            # 2. Contar préstamos en curso
            cursor.execute("""
                SELECT COUNT(*) FROM prestamo 
                WHERE estado IN ('APROBADO', 'EN CURSO', 'ACTIVO', 'AUTORIZADO')
            """)
            prestamos_en_curso = cursor.fetchone()[0]
            
            # 3. Total del mes (mes actual)
            cursor.execute("""
                SELECT COUNT(*) FROM prestamo 
                WHERE EXTRACT(MONTH FROM fecha_prestamo) = EXTRACT(MONTH FROM CURRENT_DATE)
                AND EXTRACT(YEAR FROM fecha_prestamo) = EXTRACT(YEAR FROM CURRENT_DATE)
            """)
            total_mes = cursor.fetchone()[0]
            
            # 4. Total general
            cursor.execute("SELECT COUNT(*) FROM prestamo")
            total_prestamos = cursor.fetchone()[0]
            
            # 5. Últimas solicitudes pendientes
            cursor.execute("""
                SELECT p.id_prestamo, p.id_usuario, p.estado, p.fecha_prestamo,
                       u.nombres, u.apellidos
                FROM prestamo p
                LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                WHERE p.estado IN ('PENDIENTE', 'RESERVA')
                ORDER BY p.fecha_prestamo DESC, p.id_prestamo DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                id_prestamo, id_usuario, estado, fecha_prestamo, nombres, apellidos = row
                nombre_usuario = f"{nombres} {apellidos}" if nombres else f"Usuario #{id_usuario}"
                
                ultimas_solicitudes.append({
                    'id_prestamo': id_prestamo,
                    'usuario': nombre_usuario,
                    'estado': estado,
                    'fecha': fecha_prestamo,
                })
                
            # 6. Devoluciones pendientes (si tienes tabla devolucion)
            try:
                cursor.execute("""
                    SELECT COUNT(*) FROM prestamo 
                    WHERE estado IN ('POR DEVOLVER', 'EN MORA', 'PENDIENTE DEVOLUCION')
                """)
                devoluciones_pendientes = cursor.fetchone()[0]
            except:
                devoluciones_pendientes = 0
                
    except Exception as e:
        print(f"Error en consultas SQL: {str(e)}")
        messages.warning(request, "No se pudieron cargar todas las estadísticas.")
    
    # Contexto para la plantilla
    context = {
        'usuario_nombre': request.session.get('nombre', 'Administrador'),
        'usuario_id': request.session.get('id_usuario'),
        'usuario_rol': request.session.get('rol', 'Administrador'),
        
        # Estadísticas
        'solicitudes_pendientes': solicitudes_pendientes,
        'prestamos_en_curso': prestamos_en_curso,
        'devoluciones_pendientes': devoluciones_pendientes,
        'total_mes': total_mes,
        'total_prestamos': total_prestamos,
        
        # Lista de solicitudes
        'ultimas_solicitudes': ultimas_solicitudes,
        'tiene_solicitudes_pendientes': solicitudes_pendientes > 0,
        
        # Fecha
        'fecha_actual': "Hoy",
    }
    
    return render(request, "menu.html", context)