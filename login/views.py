# login/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuarios

def login_view(request):
    # Si ya está logueado, redirigir según su rol
    if request.session.get('id_usuario'):
        id_rol = request.session.get('id_rol')
        if id_rol == 100:
            return redirect('/menu/')
        elif id_rol == 200:
            return redirect('/docente/')
    
    if request.method == "POST":
        correo = request.POST.get("correo")
        password = request.POST.get("password")

        try:
            usuario = Usuarios.objects.get(correo=correo)
        except Usuarios.DoesNotExist:
            messages.error(request, "Credenciales incorrectas")
            return render(request, "login.html")

        if usuario.password != password:
            messages.error(request, "Credenciales incorrectas")
            return render(request, "login.html")

        # Crear sesión
        request.session["id_usuario"] = usuario.id_usuario
        request.session["nombre"] = usuario.nombres
        request.session["rol"] = usuario.id_rol.tipo_rol
        request.session["id_rol"] = usuario.id_rol.id_rol
        request.session.set_expiry(3600)  # 1 hora de sesión

        # Redirigir según rol
        if usuario.id_rol.id_rol == 100:
            return redirect("/menu/")
        elif usuario.id_rol.id_rol == 200:
            return redirect("/docente/")
        else:
            messages.error(request, "Rol no válido.")
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