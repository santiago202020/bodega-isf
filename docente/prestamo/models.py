from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Prestamo(models.Model):

    id_prestamo = models.BigAutoField(primary_key=True)
    id_usuario = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_prestamo = models.DateField(auto_now_add=True)
    hora_prestamo = models.TimeField(auto_now_add=True)
    estado = models.CharField(max_length=30, default='PENDIENTE') 
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'prestamo'


    def __str__(self):
        return f"Prestamo #{self.id_prestamo} - {self.id_usuario}"


class DetallePrestamo(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    id_prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, db_column='id_prestamo', related_name='detalles')
    tipo_articulo = models.CharField(max_length=50)  
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField(default=1)
    estado_detalle = models.CharField(max_length=30, default='PENDIENTE') 

    class Meta:
        db_table = 'detalle_prestamo'
        managed = False  

    def __str__(self):
        return f"{self.tipo_articulo} #{self.id_articulo} x {self.cantidad}"
