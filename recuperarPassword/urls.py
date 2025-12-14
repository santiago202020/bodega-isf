from django.urls import path
from . import views

urlpatterns = [
    path('solicitar/', views.solicitar_recuperacion_view, name='solicitar_recuperacion'),
    path('verificar-codigo/', views.verificar_codigo_recuperacion_view, name='verificar_codigo_recuperacion'),
    path('cambiar-password/', views.cambiar_password_view, name='cambiar_password'),
    path('exito/', views.exito_recuperacion_view, name='exito_recuperacion'),
]