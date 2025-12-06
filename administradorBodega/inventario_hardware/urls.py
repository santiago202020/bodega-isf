from django.urls import path
from . import views

urlpatterns = [
path('', views.inventario_hardware, name='inventario_hardware'),
    path('hardware/eliminar/<int:id>/', views.eliminar_hardware, name='eliminar_hardware'),
]
