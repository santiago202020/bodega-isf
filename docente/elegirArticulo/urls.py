from django.urls import path
from .views import elegir_articulo, ver_bolsa

urlpatterns = [
    path("", elegir_articulo, name="elegir_articulo"),
    path("bolsa/", ver_bolsa, name="ver_bolsa"),
]
