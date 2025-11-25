from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_docente, name='menu_docente'),
]
