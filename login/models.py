from django.db import models

class Rol(models.Model):
    id_rol = models.BigIntegerField(primary_key=True)
    tipo_rol = models.CharField(max_length=100)

    class Meta:
        db_table = 'rol'


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    correo = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='id_rol')

    class Meta:
        db_table = 'usuarios'
