from django.db import models

class ArticuloDeportivo(models.Model):
    id_deportivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=1)
    devolucion = models.CharField(max_length=1)
    
    class Meta:
        managed = False
        db_table = 'articulos_deportivos'