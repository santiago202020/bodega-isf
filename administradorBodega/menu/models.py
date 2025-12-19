# administradorBodega/models.py (o donde tengas tu app de administrador)
from django.db import models

# Modelo Prestamo para el administrador
class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.BigIntegerField()
    fecha_prestamo = models.DateField()
    hora_prestamo = models.TimeField()
    estado = models.CharField(max_length=50)
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    class Meta:
        managed = False  # La tabla ya existe
        db_table = 'prestamo'
    
    def __str__(self):
        return f"Préstamo #{self.id_prestamo}"

# Modelo Usuario para mostrar nombres
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField()
    id_rol = models.BigIntegerField()
    
    class Meta:
        managed = False
        db_table = 'usuarios'
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"