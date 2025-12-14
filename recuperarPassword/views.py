from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
import random
import string

# Generar código de 6 caracteres
def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 1. Vista para solicitar recuperación
def solicitar_recuperacion_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip().lower()
        
        if not correo:
            messages.error(request, "Por favor ingresa tu correo electrónico")
            return redirect('solicitar_recuperacion')
        
        # Verificar si el correo existe en la BD y obtener datos del usuario
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT u.correo, u.nombres, u.id_rol, r.tipo_rol 
                    FROM usuarios u 
                    LEFT JOIN rol r ON u.id_rol = r.id_rol 
                    WHERE u.correo = %s
                """, [correo])
                
                resultado = cursor.fetchone()
                
                if not resultado:
                    messages.error(request, "Este correo no está registrado en el sistema")
                    return redirect('solicitar_recuperacion')
                
                # Extraer datos
                correo_bd, nombres, id_rol, tipo_rol = resultado
                
        except Exception as e:
            messages.error(request, f"Error al verificar el correo: {str(e)}")
            return redirect('solicitar_recuperacion')
        
        # Generar código de recuperación
        codigo_recuperacion = generar_codigo()
        
        # Guardar datos en sesión (sin el rol, solo necesitamos correo)
        request.session['datos_recuperacion'] = {
            'correo': correo,
            'nombres': nombres,
            'codigo_verificacion': codigo_recuperacion,
            'fecha_creacion': datetime.now().isoformat(),
            'intentos': 0
        }
        
        # Enviar email con el código
        try:
            send_mail(
                subject='Recuperación de Contraseña - Bodega ISF',
                message=f'''
                Hola {nombres},
                
                Hemos recibido una solicitud para recuperar tu contraseña.
                
                Tu código de recuperación es: {codigo_recuperacion}
                
                Ingresa este código en la página de recuperación para continuar.
                
                El código expira en 24 horas.
                
                Si no solicitaste recuperar tu contraseña, puedes ignorar este mensaje.
                
                Atentamente,
                Sistema de Gestión Bodega ISF
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
                fail_silently=False,
            )
            
            messages.success(request, f"✅ Código de recuperación enviado a {correo}")
            return redirect('verificar_codigo_recuperacion')
            
        except Exception as e:
            # Si falla el email, limpiar sesión
            if 'datos_recuperacion' in request.session:
                del request.session['datos_recuperacion']
            messages.error(request, f"❌ Error al enviar el email: {str(e)}")
            return redirect('solicitar_recuperacion')
    
    return render(request, 'recuperarPassword/solicitar_recuperacion.html')

# 2. Vista para verificar el código
def verificar_codigo_recuperacion_view(request):
    # Verificar que existan datos en sesión
    if 'datos_recuperacion' not in request.session:
        messages.error(request, "⚠️ Sesión expirada. Por favor, solicita recuperación nuevamente.")
        return redirect('solicitar_recuperacion')
    
    datos = request.session['datos_recuperacion']
    
    # Verificar expiración (24 horas)
    try:
        fecha_creacion = datetime.fromisoformat(datos['fecha_creacion'])
        if datetime.now() - fecha_creacion > timedelta(hours=24):
            del request.session['datos_recuperacion']
            messages.error(request, "⏰ El código ha expirado. Solicita uno nuevo.")
            return redirect('solicitar_recuperacion')
    except:
        del request.session['datos_recuperacion']
        messages.error(request, "⚠️ Error en los datos de sesión. Solicita recuperación nuevamente.")
        return redirect('solicitar_recuperacion')
    
    # Verificar intentos
    if datos['intentos'] >= 3:
        del request.session['datos_recuperacion']
        messages.error(request, "🔒 Demasiados intentos fallidos. Solicita recuperación nuevamente.")
        return redirect('solicitar_recuperacion')
    
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip().upper()
        
        if codigo_ingresado == datos['codigo_verificacion']:
            # ¡CÓDIGO CORRECTO! Redirigir a cambiar contraseña
            messages.success(request, "✅ Código verificado correctamente. Ahora puedes cambiar tu contraseña.")
            return redirect('cambiar_password')
        
        else:
            # Código incorrecto, incrementar intentos
            datos['intentos'] += 1
            request.session['datos_recuperacion'] = datos
            request.session.modified = True
            
            intentos_restantes = 3 - datos['intentos']
            if intentos_restantes > 0:
                messages.error(request, f"❌ Código incorrecto. Te quedan {intentos_restantes} intentos.")
            else:
                del request.session['datos_recuperacion']
                messages.error(request, "🔒 Demasiados intentos fallidos. Solicita recuperación nuevamente.")
                return redirect('solicitar_recuperacion')
    
    # Mostrar parcialmente el correo para referencia
    correo = datos['correo']
    if '@' in correo:
        partes = correo.split('@')
        correo_parcial = f"{partes[0][:3]}***@{partes[1]}"
    else:
        correo_parcial = correo
    
    context = {
        'correo_parcial': correo_parcial,
        'intentos_restantes': 3 - datos['intentos']
    }
    
    return render(request, 'recuperarPassword/verificar_codigo.html', context)

# 3. Vista para cambiar contraseña
def cambiar_password_view(request):
    # Verificar que existan datos en sesión y que el código fue verificado
    if 'datos_recuperacion' not in request.session:
        messages.error(request, "⚠️ Sesión expirada. Por favor, solicita recuperación nuevamente.")
        return redirect('solicitar_recuperacion')
    
    datos = request.session['datos_recuperacion']
    
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password', '').strip()
        confirmar_password = request.POST.get('confirmar_password', '').strip()
        
        # Validaciones
        if not nueva_password or not confirmar_password:
            messages.error(request, "Todos los campos son obligatorios")
            return redirect('cambiar_password')
        
        if nueva_password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('cambiar_password')
        
        if len(nueva_password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres")
            return redirect('cambiar_password')
        
        # Actualizar contraseña en la BD (para cualquier rol)
        try:
            with connection.cursor() as cursor:
                # Encriptar la nueva contraseña
                password_encriptada = make_password(nueva_password)
                
                # Actualizar en la tabla usuarios (funciona para ambos roles)
                cursor.execute("""
                    UPDATE usuarios 
                    SET password = %s 
                    WHERE correo = %s
                """, [password_encriptada, datos['correo']])
                
                # Verificar que se actualizó
                if cursor.rowcount == 0:
                    messages.error(request, "❌ Error al actualizar la contraseña. Usuario no encontrado.")
                    return redirect('cambiar_password')
                
                # Limpiar sesión
                del request.session['datos_recuperacion']
                
                messages.success(request, "✅ Contraseña actualizada exitosamente. Ahora puedes iniciar sesión.")
                return redirect('exito_recuperacion')
                
        except Exception as e:
            messages.error(request, f"❌ Error al actualizar la contraseña: {str(e)}")
            return redirect('cambiar_password')
    
    return render(request, 'recuperarPassword/cambiar_password.html')

# 4. Vista de éxito
def exito_recuperacion_view(request):
    return render(request, 'recuperarPassword/exito_recuperacion.html')