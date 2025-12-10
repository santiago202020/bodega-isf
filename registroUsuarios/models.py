from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class RegistroTemporal(models.Model):
    """Guarda datos temporalmente hasta verificar el email"""
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Password hasheado
    codigo_verificacion = models.CharField(max_length=6)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    intentos = models.IntegerField(default=0)
    
    def __str__(self):
        return self.correo