from django.db import models

class ArticulosHardware(models.Model):
    id_hardware = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    marca = models.CharField(max_length=255)
    modelo = models.CharField(max_length=255)
    serial = models.CharField(max_length=255)
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=255)
    devolucion = models.CharField(max_length=255)  # obligatorio, no obligatorio

    class Meta:
        managed = False
        db_table = 'articulos_hardware'
