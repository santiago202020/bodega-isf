from django.db import models

class ArticuloDeportivo(models.Model):
    # Opciones para el campo estado (texto completo, no un solo carácter)
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'DISPONIBLE'),
        ('NO DISPONIBLE', 'NO DISPONIBLE'),
    ]
    
    # Opciones para el campo devolucion (Sí/No, no un solo carácter)
    DEVOLUCION_CHOICES = [
        ('SI', 'SI'),
        ('NO', 'NO'),
    ]
    
    id_deportivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad_total = models.BigIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')  # Cambiado a texto
    devolucion = models.CharField(max_length=2, choices=DEVOLUCION_CHOICES, default='NO')  # Cambiado a SI/NO
    
    class Meta:
        managed = False
        db_table = 'articulos_deportivos'
    
    def __str__(self):
        return f"{self.nombre} - {self.estado}"