from django.urls import path
from . import views

urlpatterns = [
    path('', views.gestion_articulos, name='gestion_articulos'),
    path('eliminar/<int:id>/', views.eliminar_articulo, name='eliminar_articulo'),
]