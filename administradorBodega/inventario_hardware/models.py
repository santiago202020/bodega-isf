from django.db import models

class ArticulosHardware(models.Model):
    # Opciones para el campo estado
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'DISPONIBLE'),
        ('NO DISPONIBLE', 'NO DISPONIBLE'),
    ]
    
    # Opciones para el campo devolucion
    DEVOLUCION_CHOICES = [
        ('SI', 'SI'),
        ('NO', 'NO'),
    ]
    
    id_hardware = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    marca = models.CharField(max_length=255)
    modelo = models.CharField(max_length=255)
    serial = models.CharField(max_length=255)
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    devolucion = models.CharField(max_length=2, choices=DEVOLUCION_CHOICES, default='NO')
    
    class Meta:
        managed = False
        db_table = 'articulos_hardware'
    
    def __str__(self):
        return f"{self.nombre} - {self.marca} {self.modelo}"