# reportes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.reportes_principal, name='reportes_principal'),
]