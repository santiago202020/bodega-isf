from django.urls import path
from . import views

urlpatterns = [
    path('', views.registro_view, name='registro'),
    path('verificar/', views.verificar_codigo_view, name='verificar_codigo'),
    path('exito/', views.exito_view, name='exito'),  # ← Cambia registro_exitoso_view por exito_view
]