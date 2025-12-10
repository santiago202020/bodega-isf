from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.contrib.auth.hashers import make_password, check_password
import random
import string
from datetime import datetime, timedelta

# Generar código
def generar_codigo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 1. Vista de Registro COMPLETA
def registro_view(request):
    if request.method == 'POST':
        # Obtener datos del formulario REAL
        nombres = request.POST.get('nombres', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        correo = request.POST.get('correo', '').strip().lower()
        password = request.POST.get('password', '').strip()
        confirmar_password = request.POST.get('confirmar_password', '').strip()
        
        # Validaciones básicas
        if not all([nombres, apellidos, correo, password, confirmar_password]):
            messages.error(request, "Todos los campos son obligatorios")
            return redirect('registro')
        
        if password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro')
        
        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres")
            return redirect('registro')
        
        # Verificar si el correo ya existe en la BD
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM usuarios WHERE correo = %s", [correo])
                existe_usuario = cursor.fetchone()[0] > 0
            
            if existe_usuario:
                messages.error(request, "Este correo ya está registrado")
                return redirect('registro')
        except Exception as e:
            messages.error(request, f"Error al verificar el correo: {str(e)}")
            return redirect('registro')
        
        # Generar código REAL
        codigo_verificacion = generar_codigo()
        
        # Guardar datos REALES en sesión
        request.session['datos_registro'] = {
            'nombres': nombres,
            'apellidos': apellidos,
            'correo': correo,
            'password': password,  # Guardar sin hashear (se hashea después)
            'codigo_verificacion': codigo_verificacion,
            'fecha_creacion': datetime.now().isoformat(),
            'intentos': 0
        }
        
        # Enviar email REAL con el código
        try:
            send_mail(
                subject='Código de verificación - Sistema de Registro',
                message=f'''
                Hola {nombres},
                
                Tu código de verificación es: {codigo_verificacion}
                
                Ingresa este código en la página de verificación para completar tu registro.
                
                El código expira en 24 horas.
                
                Atentamente,
                Sistema de Gestión
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
                fail_silently=False,
            )
            
            messages.success(request, f"✅ Código de verificación enviado a {correo}")
            return redirect('verificar_codigo')
            
        except Exception as e:
            # Si falla el email, limpiar sesión
            if 'datos_registro' in request.session:
                del request.session['datos_registro']
            messages.error(request, f"❌ Error al enviar el email: {str(e)}")
            return redirect('registro')
    
    # GET request: mostrar formulario vacío
    return render(request, 'registro.html')

# 2. Vista de Verificación COMPLETA
def verificar_codigo_view(request):
    # Verificar que existan datos en sesión
    if 'datos_registro' not in request.session:
        messages.error(request, "⚠️ Sesión expirada. Por favor, regístrate nuevamente.")
        return redirect('registro')
    
    datos = request.session['datos_registro']
    
    # Verificar expiración (24 horas)
    try:
        fecha_creacion = datetime.fromisoformat(datos['fecha_creacion'])
        if datetime.now() - fecha_creacion > timedelta(hours=24):
            del request.session['datos_registro']
            messages.error(request, "⏰ El código ha expirado. Regístrate nuevamente.")
            return redirect('registro')
    except:
        del request.session['datos_registro']
        messages.error(request, "⚠️ Error en los datos de sesión. Regístrate nuevamente.")
        return redirect('registro')
    
    # Verificar intentos
    if datos['intentos'] >= 3:
        del request.session['datos_registro']
        messages.error(request, "🔒 Demasiados intentos fallidos. Regístrate nuevamente.")
        return redirect('registro')
    
    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip().upper()
        
        if codigo_ingresado == datos['codigo_verificacion']:
            # ¡CÓDIGO CORRECTO! Insertar en tabla usuarios
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO usuarios (nombres, apellidos, correo, password, id_rol)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [
                        datos['nombres'],
                        datos['apellidos'],
                        datos['correo'],
                        make_password(datos['password']),  # Hashear la contraseña
                        200  # ID para Docente
                    ])
                
                # Limpiar sesión
                del request.session['datos_registro']
                
                messages.success(request, "🎉 ¡Registro completado! Ahora puedes iniciar sesión.")
                return redirect('exito')
                
            except Exception as e:
                messages.error(request, f"❌ Error al crear el usuario: {str(e)}")
                return redirect('registro')
        
        else:
            # Código incorrecto, incrementar intentos
            datos['intentos'] += 1
            request.session['datos_registro'] = datos
            request.session.modified = True
            
            intentos_restantes = 3 - datos['intentos']
            if intentos_restantes > 0:
                messages.error(request, f"❌ Código incorrecto. Te quedan {intentos_restantes} intentos.")
            else:
                del request.session['datos_registro']
                messages.error(request, "🔒 Demasiados intentos fallidos. Regístrate nuevamente.")
                return redirect('registro')
    
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
    
    return render(request, 'verificar_codigo.html', context)

# 3. Vista de Éxito
def exito_view(request):
    return render(request, 'exito.html')