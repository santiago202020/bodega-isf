from django.db import models

class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    id_prestamo = models.IntegerField()  # Referencia al préstamo
    cantidad_devuelta = models.BigIntegerField(default=0)
    fecha_devolucion = models.DateField(auto_now_add=True)
    observaciones = models.CharField(max_length=500, blank=True)
    
    class Meta:
        db_table = 'devolucion'

class DetalleDevolucion(models.Model):
    id_detalle_devolucion = models.AutoField(primary_key=True)
    id_devolucion = models.BigIntegerField()  # Relación con Devolucion
    tipo_articulo = models.CharField(max_length=50)  # 'papeleria', 'hardware', 'deportivo'
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_devolucion = models.CharField(max_length=50, default='DEVUELTO')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'detalle_devolucion'
        # administradorBodega/gestionPrestamos/models.py
