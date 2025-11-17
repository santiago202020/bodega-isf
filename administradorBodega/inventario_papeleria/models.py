from django.db import models

class ArticuloPapeleria(models.Model):
    id_papeleria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    unidad_medida = models.CharField(max_length=255)
    devolucion = models.CharField(max_length=255)
    
    class Meta:
        managed = False
        db_table = 'articulos_papeleria'