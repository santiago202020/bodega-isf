from django.urls import path
from . import views

urlpatterns = [
    path('', views.gestion_articulos_papeleria, name='gestion_articulos_papeleria'),
    path('eliminar/<int:id>/', views.eliminar_articulo_papeleria, name='eliminar_articulo_papeleria'),
]