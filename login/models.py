from django.db import models

class Rol(models.Model):
    id_rol = models.BigIntegerField(primary_key=True)
    tipo_rol = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'rol'
    
    def __str__(self):
        return self.tipo_rol

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    
    id_rol = models.ForeignKey(
        Rol, 
        on_delete=models.CASCADE,
        db_column='id_rol',  # Esto fuerza a usar el nombre correcto
        to_field='id_rol',   # Referencia al campo correcto
        db_index=True
    )
    
    class Meta:
        db_table = 'usuarios'
    
    def __str__(self):
        return self.correo