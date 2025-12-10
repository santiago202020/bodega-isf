from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Usuarios
from django.db import connection

def login_view(request):
    # Si ya está logueado, redirigir según su rol
    if request.session.get('id_usuario'):
        id_rol = request.session.get('id_rol')
        if id_rol == 100:
            return redirect('/menu/')
        elif id_rol == 200:
            return redirect('/docente/')
    
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip().lower()
        password = request.POST.get("password", "").strip()

        # Verificar que ambos campos estén llenos
        if not correo or not password:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, "login.html")
        
        # INTENTAR CON MODELO PRIMERO
        try:
            usuario = Usuarios.objects.get(correo=correo)
            
            # Usar check_password para comparar contraseña encriptada
            if check_password(password, usuario.password):
                # ¡CREDENCIALES CORRECTAS! Crear sesión
                request.session["id_usuario"] = usuario.id_usuario
                request.session["nombre"] = usuario.nombres
                request.session["id_rol"] = usuario.id_rol.id_rol
                request.session["rol"] = usuario.id_rol.tipo_rol
                request.session.set_expiry(3600)  # 1 hora
                
                # DEBUG: Verificar en consola
                print(f"Login exitoso: {usuario.correo}")
                print(f"Rol ID: {usuario.id_rol.id_rol}")
                print(f"Rol Tipo: {usuario.id_rol.tipo_rol}")
                
                # Redirigir según rol
                if usuario.id_rol.id_rol == 100:
                    return redirect("/menu/")
                elif usuario.id_rol.id_rol == 200:
                    return redirect("/docente/")
                else:
                    messages.error(request, "Rol no válido.")
                    return render(request, "login.html")
            else:
                messages.error(request, "Credenciales incorrectas")
                return render(request, "login.html")
                
        except Usuarios.DoesNotExist:
            # Si no existe en el modelo, intentar con SQL directo
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT u.id_usuario, u.nombres, u.password, u.id_rol, r.tipo_rol 
                        FROM usuarios u
                        JOIN rol r ON u.id_rol = r.id_rol
                        WHERE u.correo = %s
                    """, [correo])
                    
                    usuario_data = cursor.fetchone()
                    
                    if not usuario_data:
                        messages.error(request, "Credenciales incorrectas")
                        return render(request, "login.html")
                    
                    id_usuario, nombres, password_encriptada, id_rol, tipo_rol = usuario_data
                    
                    # Verificar contraseña encriptada
                    if check_password(password, password_encriptada):
                        # Crear sesión
                        request.session["id_usuario"] = id_usuario
                        request.session["nombre"] = nombres
                        request.session["id_rol"] = id_rol
                        request.session["rol"] = tipo_rol
                        request.session.set_expiry(3600)  # 1 hora
                        
                        # Redirigir según rol
                        if id_rol == 100:
                            return redirect("/menu/")
                        elif id_rol == 200:
                            return redirect("/docente/")
                        else:
                            messages.error(request, "Rol no válido.")
                            return render(request, "login.html")
                    else:
                        messages.error(request, "Credenciales incorrectas")
                        return render(request, "login.html")
                        
            except Exception as db_error:
                messages.error(request, f"Error de base de datos: {str(db_error)}")
                return render(request, "login.html")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
            return render(request, "login.html")
    
    return render(request, "login.html")

def logout_view(request):
    """
    Cierra la sesión del usuario
    """
    # Limpiar todos los datos de sesión
    request.session.flush()
    
    # Mensaje de confirmación
    messages.success(request, "Sesión cerrada exitosamente.")
    
    # Redirigir al login
    return redirect('/login/')