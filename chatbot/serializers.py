from rest_framework import serializers
from .models import SesionTriaje

class SesionTriajeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionTriaje
        fields = ['usuario', 'respuestas', 'urgente', 'score', 'recomendaciones']

class SesionTriajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SesionTriaje
        fields = ['id', 'usuario', 'respuestas', 'urgente', 'score', 'recomendaciones', 'creado_en']