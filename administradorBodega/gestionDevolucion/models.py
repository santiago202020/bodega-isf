# administradorBodega/gestionDevolucion/models.py
from django.db import models

class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.BigIntegerField()
    fecha_prestamo = models.DateField()
    hora_prestamo = models.TimeField()
    estado = models.CharField(max_length=20)
    observaciones = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'prestamo'
        managed = False

class DetallePrestamo(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_prestamo = models.BigIntegerField()
    tipo_articulo = models.CharField(max_length=30)
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_detalle = models.CharField(max_length=30)

    class Meta:
        db_table = 'detalle_prestamo'
        managed = False

class DetalleDevolucion(models.Model):
    id_detalle_devolucion = models.AutoField(primary_key=True)
    id_devolucion = models.BigIntegerField()
    tipo_articulo = models.CharField(max_length=30)
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_devolucion = models.CharField(max_length=30)
    fecha_devolucion = models.DateField()
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'detalle_devolucion'
        managed = False

class ArticuloPapeleria(models.Model):
    id_papeleria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    unidad_medida = models.CharField(max_length=100)
    devolucion = models.CharField(max_length=10)
    estado = models.CharField(max_length=50)

    class Meta:
        db_table = 'articulos_papeleria'
        managed = False

class ArticuloHardware(models.Model):
    id_hardware = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    cantidad_total = models.BigIntegerField()
    devolucion = models.CharField(max_length=10)
    estado = models.CharField(max_length=50)

    class Meta:
        db_table = 'articulos_hardware'
        managed = False

class ArticuloDeportivo(models.Model):
    id_deportivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=50)
    devolucion = models.CharField(max_length=10)

    class Meta:
        db_table = 'articulos_deportivos'
        managed = False