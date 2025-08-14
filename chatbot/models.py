from django.db import models
from usuarios.models import Usuario

class Sintoma(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sintomas')
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Síntoma de {self.usuario.nombre} en {self.fecha_registro}'  