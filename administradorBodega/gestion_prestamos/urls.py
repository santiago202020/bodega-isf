# administradorBodega/gestion_prestamos/urls.py
from django.urls import path
from . import views

app_name = "gestion_prestamos"

urlpatterns = [
    path("pendientes/", views.lista_pendientes, name="lista_pendientes"),
    path("detalle/<int:pk>/", views.detalle_prestamo_admin, name="detalle_prestamo_admin"),
    path("aceptar/<int:pk>/", views.aceptar_prestamo, name="aceptar_prestamo"),
    path("rechazar/<int:pk>/", views.rechazar_prestamo, name="rechazar_prestamo"),
    path("devolver/<int:pk>/", views.registrar_devolucion, name="registrar_devolucion"),
    
    
]
