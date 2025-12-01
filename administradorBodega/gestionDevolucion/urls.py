# administradorBodega/gestionDevolucion/urls.py
from django.urls import path
from . import views

app_name = 'gestionDevolucion'

urlpatterns = [
    path('pendientes/', views.prestamos_para_devolucion, name='pendientes'),
    path('parcial/<int:id_prestamo>/', views.registrar_devolucion_parcial, name='parcial'),
    path('completa/<int:id_prestamo>/', views.registrar_devolucion_completa, name='completa'),
]