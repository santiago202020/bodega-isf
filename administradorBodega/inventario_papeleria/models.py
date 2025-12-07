from django.db import models

class ArticuloPapeleria(models.Model):
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
    
    # Opciones para unidad de medida
    UNIDAD_CHOICES = [
        ('UNIDAD', 'UNIDAD'),
        ('CAJA', 'CAJA'),
        ('PAQUETE', 'PAQUETE'),
        ('RESMA', 'RESMA'),
        ('LOTE', 'LOTE'),
        ('KILO', 'KILO'),
        ('METRO', 'METRO'),
    ]
    
    id_papeleria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='UNIDAD')
    devolucion = models.CharField(max_length=2, choices=DEVOLUCION_CHOICES, default='NO')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    
    class Meta:
        managed = False
        db_table = 'articulos_papeleria'
    
    def __str__(self):
        return f"{self.nombre} - {self.cantidad_total} {self.unidad_medida}"