from django.urls import path
from . import views

app_name = "prestamo"

urlpatterns = [
    path('confirmar/', views.confirmar_prestamo, name='confirmar_prestamo'),
    path('mis_prestamos/', views.lista_mis_prestamos, name='mis_prestamos'),
    path('detalle/<int:pk>/', views.detalle_prestamo, name='detalle_prestamo'),
]
