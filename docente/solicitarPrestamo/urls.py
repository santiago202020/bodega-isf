# solicitarPrestamo/urls.py
from django.urls import path
from . import views

app_name = 'solicitarPrestamo'

urlpatterns = [
    path('seleccionar/', views.seleccionar_articulos, name='seleccionar'),
    path('bolsa/add/', views.add_to_bolsa, name='add_to_bolsa'),
    path('bolsa/', views.ver_bolsa, name='bolsa_ver'),
    path('bolsa/remove/', views.remove_from_bolsa, name='bolsa_remove'), 
    path('confirmar/', views.confirmar_solicitud, name='confirmar'),
    path('historial/', views.historial, name='historial'),
    path('detalle/<int:id_prestamo>/', views.detalle, name='detalle'),
    path('modificar-cantidad/', views.modificar_cantidad_bolsa, name='modificar_cantidad'),
]