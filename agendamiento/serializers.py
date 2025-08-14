from rest_framework import serializers
from .models import Cita
from django.utils import timezone

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = ['id', 'usuario', 'fecha_hora', 'motivo', 'estado']

    # --- BLOQUEO DE FECHA/HORA PASADA ---
    def validate_fecha_hora(self, value):
        # Normaliza a aware si viene naive
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        if value <= timezone.now():
            raise serializers.ValidationError("La fecha/hora debe ser futura.")
        return value

    # Normaliza antes de crear/actualizar
    def create(self, validated_data):
        fh = validated_data['fecha_hora']
        if timezone.is_naive(fh):
            validated_data['fecha_hora'] = timezone.make_aware(fh, timezone.get_current_timezone())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        fh = validated_data.get('fecha_hora')
        if fh and timezone.is_naive(fh):
            validated_data['fecha_hora'] = timezone.make_aware(fh, timezone.get_current_timezone())
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['usuario'] = {
            "id": instance.usuario.id,
            "nombre": f"{instance.usuario.nombre[0]}***" if instance.usuario.nombre else None
        }
        return data