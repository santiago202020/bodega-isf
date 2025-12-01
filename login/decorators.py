# login/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def login_required_custom(function=None, redirect_url=None):
    """
    Decorador personalizado que verifica si el usuario tiene sesión activa
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if not request.session.get('id_usuario'):
                messages.error(request, "Debe iniciar sesión para acceder a esta página.")
                return redirect(redirect_url or '/login/')
            return view_func(request, *args, **kwargs)
        return wrapped_view
    
    if function:
        return decorator(function)
    return decorator

def rol_required(roles_permitidos=[]):
    """
    Decorador que verifica si el usuario tiene el rol adecuado
    Ejemplo: @rol_required([100]) para admin, @rol_required([200]) para docente
    """
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            # Primero verificar login
            if not request.session.get('id_usuario'):
                messages.error(request, "Debe iniciar sesión.")
                return redirect('/login/')
            
            # Verificar rol
            rol_usuario = request.session.get('id_rol')
            if rol_usuario not in roles_permitidos:
                messages.error(request, "No tiene permisos para acceder a esta página.")
                return redirect('/login/')
                
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator