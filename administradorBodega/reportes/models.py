# reportes/models.py
from django.db import models

# Estos modelos reflejan tus tablas existentes
# Solo necesitamos definir los que usaremos para los reportes

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    correo = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    id_rol = models.BigIntegerField()
    
    class Meta:
        db_table = 'usuarios'
        managed = False  # Importante: Django no gestionará estas tablas

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Rol(models.Model):
    id_rol = models.BigIntegerField(primary_key=True)
    tipo_rol = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'rol'
        managed = False

class Prestamo(models.Model):
    ESTADOS_PRESTAMO = [
        ('RECHAZADA', 'Rechazada'),
        ('DEVUELTO_COMPLETO', 'Devuelto completo'),
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
    ]
    
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, db_column='id_usuario')
    fecha_prestamo = models.DateField()
    hora_prestamo = models.TimeField()
    estado = models.CharField(max_length=50, choices=ESTADOS_PRESTAMO)
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    hora_inicio = models.DateField()  # Nota: en tu descripción es Date, pero debería ser DateField
    hora_fin = models.TimeField()
    
    class Meta:
        db_table = 'prestamo'
        managed = False

class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    id_prestamo = models.ForeignKey(Prestamo, on_delete=models.DO_NOTHING, db_column='id_prestamo')
    cantidad_devuelta = models.BigIntegerField()
    fecha_devolucion = models.DateField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'devolucion'
        managed = False

class DetallePrestamo(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_prestamo = models.ForeignKey(Prestamo, on_delete=models.DO_NOTHING, db_column='id_prestamo')
    tipo_articulo = models.CharField(max_length=255)
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_detalle = models.CharField(max_length=30, blank=True, null=True)
    
    class Meta:
        db_table = 'detalle_prestamo'
        managed = False

# No necesitamos crear todos los modelos de artículos a menos que los uses en los reportes