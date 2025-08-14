from django.db import models
from usuarios.models import Usuario
from django.core.exceptions import ValidationError          # ⬅️ NUEVO
from django.utils import timezone                           # ⬅️ NUEVO

class Cita(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='citas')
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, default='Pendiente')

    def __str__(self):
        return f'Cita del usuario {self.usuario.id} el {self.fecha_hora}'

    # ⛔ Validación de modelo: no permitir fecha/hora pasada
    def clean(self):
        fh = self.fecha_hora
        if fh:
            # normaliza a timezone-aware si viene naive
            if timezone.is_naive(fh):
                fh = timezone.make_aware(fh, timezone.get_current_timezone())
            if fh <= timezone.now():
                raise ValidationError("No se puede agendar en una fecha/hora pasada.")

    # Asegura que la validación del modelo se ejecute siempre y que guardemos aware
    def save(self, *args, **kwargs):
        self.full_clean()  # dispara clean() y validaciones de campo
        if self.fecha_hora and timezone.is_naive(self.fecha_hora):
            self.fecha_hora = timezone.make_aware(self.fecha_hora, timezone.get_current_timezone())
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['fecha_hora']
        constraints = [
            models.UniqueConstraint(fields=['fecha_hora'], name='uniq_slot_global')
        ]