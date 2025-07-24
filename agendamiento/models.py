from django.db import models
from usuarios.models import Usuario

class Cita(models.Model):
    # Relación con el usuario que agenda la cita
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas')

    # Info de cita
    fecha_hora = models.DateTimeField()
    motivo = models.TextField() # Razón por la que el paciente agenda
    estado = models.CharField(max_length=20, default='Pendiente') # Ej: Pendiente, Confirmada, Cancelada, Completada

    def __str__(self):
        return f'Cita de {self.usuario.nombre} ({self.usuario.rut}) el {self.fecha_hora}'

    class Meta:
        # Un usuario no pueda tener dos citas exactamente a la misma fecha y hora
        unique_together = ('usuario', 'fecha_hora')
        # Ordenar citas por fecha y hora por defecto
        ordering = ['fecha_hora']
