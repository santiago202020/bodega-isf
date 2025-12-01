# administradorBodega/gestionPrestamos/models.py
from django.db import models

# Mapea la tabla existente 'prestamo'
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
        db_table = 'prestamo'  # ✅ Usa la tabla existente
        managed = False  # ✅ No crea ni modifica tablas

# Mapea la tabla existente 'detalle_prestamo'
class DetallePrestamo(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_prestamo = models.BigIntegerField()
    tipo_articulo = models.CharField(max_length=30)
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_detalle = models.CharField(max_length=30)

    class Meta:
        db_table = 'detalle_prestamo'  # ✅ Usa la tabla existente
        managed = False  # ✅ No crea ni modifica tablas

# Mapea la tabla existente 'articulos_papeleria'
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

# Mapea la tabla existente 'articulos_hardware'
class ArticuloHardware(models.Model):
    id_hardware = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=50)
    devolucion = models.CharField(max_length=10)

    class Meta:
        db_table = 'articulos_hardware'
        managed = False

# Mapea la tabla existente 'articulos_deportivos'
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