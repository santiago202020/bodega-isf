from django.urls import path
from . import views

app_name = "solicitarPrestamo"

urlpatterns = [
    path('', views.menu_docente, name='menu'),

    # Crear solicitud (seleccionar artículos)
    path('crear/', views.seleccionar_articulos, name='seleccionar'),

    # Bolsa
    path('bolsa/', views.ver_bolsa, name='bolsa_ver'),
    path('bolsa/add/', views.add_to_bolsa, name='bolsa_add'),
    path('bolsa/remove/', views.remove_from_bolsa, name='bolsa_remove'),

    # Confirmación
    path('confirmar/', views.confirmar_solicitud, name='confirmar'),
    path('bolsa/confirmar/', views.confirmar_solicitud, name='confirmar_solicitud'),

    # Historial de préstamos
    path('historial/', views.historial, name='historial'),

    # Detalle del préstamo
    path('detalle/<int:id_prestamo>/', views.detalle, name='detalle'),
]
