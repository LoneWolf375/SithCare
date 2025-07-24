from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.nombre} ({self.rut})'


class Sintoma(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sintomas')
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Síntoma de {self.usuario.nombre} en {self.fecha_registro}'