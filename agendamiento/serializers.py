from rest_framework import serializers
from .models import Cita # Importar modelo Cita
from usuarios.models import Usuario # Importar modelo Usuario

class CitaSerializer(serializers.ModelSerializer):
    # Por defecto, el campo ForeignKey ('usuario') se representará con el ID del usuario.
    # Si quisieras representar el usuario con más detalles (ej. username, nombre),
    # podrías usar UsuarioSerializer aquí, pero para la creación/actualización de citas, el ID suele ser suficiente.
    # usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    # O si quieres mostrar solo el nombre del usuario en la representación de la cita:
    # usuario_nombre = serializers.CharField(source='usuario.nombre', read_only=True)


    class Meta:
        model = Cita
        # Incluye todos los campos del modelo Cita que quieres exponer en la API
        # El campo 'usuario' se manejará automáticamente como un campo de relación (su ID)
        fields = '__all__'
        # O especifica los campos explícitamente:
        # fields = ['id', 'usuario', 'fecha_hora', 'motivo', 'estado']