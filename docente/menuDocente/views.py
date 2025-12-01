# docente/menuDocente/views.py
from django.shortcuts import render
# Usar solo login_required_custom temporalmente si rol_required sigue dando problemas
from login.decorators import login_required_custom

@login_required_custom
def menu_docente(request):
    """
    Vista principal del menú del docente
    """
    # Verificar rol manualmente (si el decorator rol_required no funciona)
    if request.session.get('id_rol') != 200:
        from django.contrib import messages
        messages.error(request, "Acceso denegado. Solo para docentes.")
        from django.shortcuts import redirect
        return redirect('/login/')
    
    return render(request, "menuDocente.html")