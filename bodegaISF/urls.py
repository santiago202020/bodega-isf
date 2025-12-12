"""
URL configuration for bodegaISF project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.urls import include, path
from django.shortcuts import redirect

def redirect_to_login(request):
    return redirect('/login/')
from django.http import HttpResponse

def health_check(request):
    """Ruta simple para health check de Railway"""
    return HttpResponse("OK", status=200, content_type="text/plain")

urlpatterns = [
    path('', redirect_to_login),  
    path('', health_check),  # Ruta raíz responde OK
    path('health/', health_check),  # Ruta alternativa
    path('admin/', admin.site.urls),
    path('hardware/', include('administradorBodega.inventario_hardware.urls')),
    path('deportivo/', include('administradorBodega.inventario_deportivo.urls')),
    path('papeleria/', include('administradorBodega.inventario_papeleria.urls')),
    path('login/', include('login.urls')),
    path('registro/', include('registroUsuarios.urls')),
    path('menu/', include('administradorBodega.menu.urls')),
    path('docente/', include('docente.menuDocente.urls')),
    path('docente/solicitar/', include('docente.solicitarPrestamo.urls')), 
    path('administradorBodega/prestamos/', include('administradorBodega.gestionPrestamos.urls')),
    path('administradorBodega/devoluciones/', include('administradorBodega.gestionDevolucion.urls')),
    path('administradorBodega/reportes/', include('administradorBodega.reportes.urls')),
]
