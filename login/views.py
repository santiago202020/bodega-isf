from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Usuarios
def login_view(request):
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

        # 👉 AQUÍ es el lugar correcto para guardar datos en sesión
        request.session["id_usuario"] = usuario.id_usuario
        request.session["nombre"] = usuario.nombres
        request.session["rol"] = usuario.id_rol.tipo_rol
        request.session["id_rol"] = usuario.id_rol.id_rol

        # 👉 Luego haces el redirect según el rol
        if usuario.id_rol.id_rol == 100:
            return redirect("/menu/")

        elif usuario.id_rol.id_rol == 200:
            return redirect("/docente/")

        else:
            messages.error(request, "Rol no válido.")
            return render(request, "login.html")

    return render(request, "login.html")
