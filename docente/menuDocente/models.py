from django.db import models

# Modelo Prestamo basado en tu tabla 'prestamo'
class Prestamo(models.Model):
    id_prestamo = models.AutoField(primary_key=True)
    id_usuario = models.BigIntegerField()
    fecha_prestamo = models.DateField()
    hora_prestamo = models.TimeField()
    estado = models.CharField(max_length=50)
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    fecha_inicio = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    class Meta:
        managed = False  # Esto es importante porque la tabla ya existe
        db_table = 'prestamo'
    
    def __str__(self):
        return f"Préstamo #{self.id_prestamo} - {self.estado}"

# Modelo DetallePrestamo basado en tu tabla 'detalle_prestamo'
class DetallePrestamo(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    id_prestamo = models.BigIntegerField()
    tipo_articulo = models.CharField(max_length=50)
    id_articulo = models.BigIntegerField()
    cantidad = models.BigIntegerField()
    estado_detalle = models.CharField(max_length=30)
    
    class Meta:
        managed = False  # La tabla ya existe en la base de datos
        db_table = 'detalle_prestamo'
    
    def __str__(self):
        return f"Detalle {self.id_detalle} - {self.tipo_articulo}"

# Modelo Devolucion basado en tu tabla 'devolucion' (opcional)
class Devolucion(models.Model):
    id_devolucion = models.AutoField(primary_key=True)
    id_prestamo = models.IntegerField()
    cantidad_devuelta = models.BigIntegerField()
    fecha_devolucion = models.DateField()
    observaciones = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'devolucion'
    
    def __str__(self):
        return f"Devolución #{self.id_devolucion}"