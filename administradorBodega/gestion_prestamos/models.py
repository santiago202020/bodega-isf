
from django.db import models
from docente.prestamo.models import Prestamo  # usa el modelo de préstamo que ya tienes

class Devolucion(models.Model):
    id_devolucion = models.BigAutoField(primary_key=True)
    id_prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, db_column='id_prestamo')
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'devolucion'
        managed = False  # si en tu BD ya existe la tabla; si no, quita esto y crea migraciones

class DevolucionDetalle(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    id_devolucion = models.ForeignKey(Devolucion, on_delete=models.CASCADE, db_column='id_devolucion', related_name='detalles')
    tipo_articulo = models.CharField(max_length=50)
    id_articulo = models.BigIntegerField()
    cantidad_devuelta = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'devolucion_detalle'
        managed = False
