from django.db import models
from django.conf import settings
from usuarios.models import Usuario

class Sintoma(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sintomas')
    descripcion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Síntoma de {self.usuario.nombre} en {self.fecha_registro}'

class SesionTriaje(models.Model):
    """
    Registro de cada ejecución del triaje.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sesiones_triaje'
    )
    respuestas = models.JSONField()                 # dict con las 8 claves del triaje
    urgente = models.BooleanField(default=False)    # resultado final
    score = models.IntegerField(default=0)          # puntaje usado en la decisión
    recomendaciones = models.JSONField(default=list, blank=True)  # textos opcionales
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        u = self.usuario_id or "anon"
        return f"Triaje u={u} urgente={self.urgente} score={self.score} {self.creado_en:%Y-%m-%d %H:%M}"