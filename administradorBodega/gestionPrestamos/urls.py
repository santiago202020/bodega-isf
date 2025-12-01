# administradorBodega/gestionPrestamos/urls.py
from django.urls import path
from . import views

app_name = 'gestionPrestamos'

urlpatterns = [
    path('pendientes/', views.prestamos_pendientes, name='pendientes'),
    path('aprobar/<int:id_prestamo>/', views.aprobar_prestamo, name='aprobar'),
    path('rechazar/<int:id_prestamo>/', views.rechazar_prestamo, name='rechazar'),
]   