from django.db import models

class ArticuloPapeleria(models.Model):
    id_papeleria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    cantidad_total = models.IntegerField(null=True, default=0)
    unidad_medida = models.CharField(max_length=100, null=True, blank=True)
    devolucion = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'articulos_papeleria'
        managed = False

class ArticuloHardware(models.Model):
    id_hardware = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    marca = models.CharField(max_length=255, null=True, blank=True)
    modelo = models.CharField(max_length=255, null=True, blank=True)
    serial = models.CharField(max_length=255, null=True, blank=True)
    cantidad_total = models.IntegerField(null=True, default=0)
    devolucion = models.CharField(max_length=50, null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'articulos_hardware'
        managed = False

class ArticuloDeportivo(models.Model):
    id_deportivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    cantidad_total = models.IntegerField(null=True, default=0)
    estado = models.CharField(max_length=50, null=True, blank=True)
    devolucion = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'articulos_deportivos'
        managed = False

# MODELOS PROPIOS PARA PRESTAMO (mapeados a tus tablas reales)
class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.BigIntegerField()
    fecha_prestamo = models.DateField(auto_now_add=True)
    hora_prestamo = models.TimeField(auto_now_add=True)
    estado = models.CharField(max_length=50)  # RESERVA, PENDIENTE, ACEPTADA, ENTREGADO, FINALIZADO...
    observaciones = models.CharField(max_length=500, null=True, blank=True)
    fecha_inicio = models.DateField()   # cuando el docente usará los artículos
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        db_table = 'prestamo'
        managed = True  # si la tabla ya existe, no crear migraciones destructivas; ajustar si hace falta

class DetallePrestamo(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_prestamo = models.BigIntegerField()
    tipo_articulo = models.CharField(max_length=50)  # 'papeleria'|'hardware'|'deportivo'
    id_articulo = models.BigIntegerField()
    cantidad = models.IntegerField()
    estado_detalle = models.CharField(max_length=50, default='SOLICITADO')  # SOLICITADO, DEVUELTO, ...

    class Meta:
        db_table = 'detalle_prestamo'
        managed = True
    