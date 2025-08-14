# usuarios/serializers.py
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from chatbot.models import Sintoma 

Usuario = get_user_model()

# --- Serializador de síntomas ---
class SintomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sintoma
        fields = ('id', 'usuario', 'descripcion', 'fecha_registro')

# --- Serializador de escritura/registro de usuario ---
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ('id', 'rut', 'nombre', 'telefono', 'password', 'email') 

    def validate_rut(self, value):
        normalized_rut = value.strip().replace("-", "").upper()
        if Usuario.objects.filter(rut__iexact=normalized_rut).exists():
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
        rut = validated_data.pop('rut').strip().replace("-", "").upper()
        nombre = validated_data.pop('nombre')
        telefono = validated_data.pop('telefono')
        password = validated_data.pop('password')
        email = validated_data.pop('email', '')

        username = rut 

        user = get_user_model().objects.create_user(
            username=username, 
            password=password,
            rut=rut, 
            nombre=nombre,
            telefono=telefono,
            email=email
        )
        Token.objects.get_or_create(user=user)
        return user

class UsuarioReadSerializer(serializers.ModelSerializer):
    rut = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    sintomas = SintomaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'rut', 'nombre', 'telefono', 'sintomas', 'email')

    def get_rut(self, obj):
        if obj.rut:
            normalized_rut = obj.rut.strip().replace("-", "").upper()
            return f"{normalized_rut[:2]}*****{normalized_rut[-2:]}"
        return None

    def get_nombre(self, obj):
        if obj.nombre:
            partes = obj.nombre.split(" ")
            anonimizadas = [p[0] + "***" for p in partes]
            return " ".join(anonimizadas)
        return None

    def get_telefono(self, obj):
        if obj.telefono:
            return obj.telefono[:6] + "****"
        return None

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['enfermedades_sistemicas', 'tipo_de_sangre', 'telefono']
        extra_kwargs = {
            'enfermedades_sistemicas': {'required': False},
            'tipo_de_sangre': {'required': False},
            'telefono': {'required': False}
        }

    def update(self, instance, validated_data):
        # Actualiza cada campo individualmente
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.email = validated_data.get('email', instance.email)
        instance.enfermedades_sistemicas = validated_data.get('enfermedades_sistemicas', instance.enfermedades_sistemicas)
        instance.tipo_de_sangre = validated_data.get('tipo_de_sangre', instance.tipo_de_sangre)
        
        # Guarda el objeto actualizado
        instance.save()
        
        return instance
    
class UsuarioProfileSerializer(serializers.ModelSerializer):
    """
    Serializador para el perfil del usuario autenticado.
    Devuelve rut, nombre, telefono, enfermedades sistémicas y tipo de sangre sin anonimizar.
    """
    class Meta:
        model = Usuario
        fields = (
            'id',
            'rut',
            'nombre',
            'telefono',
            'enfermedades_sistemicas',
            'tipo_de_sangre',
            'email',
        )