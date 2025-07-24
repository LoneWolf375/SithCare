from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Sintoma
import uuid
import secrets

class SintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sintoma
        fields = ('id', 'usuario', 'descripcion', 'fecha_registro')

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    rut = serializers.CharField()
    nombre = serializers.CharField()
    telefono = serializers.CharField()
    sintomas = SintomaSerializer(many=True, read_only=True)

class UsuarioReadSerializer(serializers.ModelSerializer):
    sintomas = SintomaSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'sintomas')

    def validate_rut(self, value):
        normalized_rut = value.strip().upper()
        if get_user_model().objects.filter(rut__iexact=normalized_rut).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT.")
        return normalized_rut

    def validate_nombre(self, value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return value.strip()

    def validate_telefono(self, value):
        if not value:
            raise serializers.ValidationError("El teléfono es obligatorio.")
        cleaned = value.strip()
        if len(cleaned) < 8:
            raise serializers.ValidationError("El teléfono debe tener al menos 8 dígitos o caracteres.")
        if not cleaned.replace("+", "").replace(" ", "").isdigit():
            raise serializers.ValidationError("El teléfono debe contener solo números y opcional '+'.")
        return cleaned

    def create(self, validated_data):
        rut = validated_data.get('rut').strip().upper()
        nombre = validated_data.get('nombre')
        telefono = validated_data.get('telefono')

        username = validated_data.get('username')
        if not username and rut:
            username = f"user_{rut}"
        elif not username:
            username = f"user_{uuid.uuid4()}"

        password = validated_data.get('password')
        if not password:
            password = secrets.token_urlsafe(12)

        user = get_user_model().objects.create_user(
            username=username,
            password=password,
        )
        user.rut = rut
        user.nombre = nombre
        user.telefono = telefono
        user.save()

        Token.objects.create(user=user)

        return user

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('nombre', 'telefono')