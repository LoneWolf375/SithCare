from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Usuario, Sintoma
from .serializers import UsuarioSerializer, SintomaSerializer, UsuarioUpdateSerializer, UsuarioReadSerializer


@api_view(['POST'])
def registrarUsuario(request):
    serializer = UsuarioSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    response_serializer = UsuarioReadSerializer(user) 
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class LoginUsuarioView(ObtainAuthToken):
    """
    Endpoint para login de usuarios con RUT y password.
    Devuelve un token si las credenciales son válidas.
    """
    def post(self, request, *args, **kwargs):
        rut = request.data.get('rut')
        password = request.data.get('password')

        if not rut or not password:
            return Response({"error": "Debes enviar rut y password."}, status=status.HTTP_400_BAD_REQUEST)

        normalized_rut = rut.strip().upper()

        try:
            usuario = Usuario.objects.get(rut__iexact=normalized_rut)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'username': usuario.username,
            'password': password
        }

        serializer = self.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'rut': user.rut
        })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutUsuario(request):
    """
    Endpoint para cerrar sesión eliminando el token del usuario.
    """
    request.user.auth_token.delete()
    return Response({"mensaje": "Logout exitoso. Token eliminado."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cambiarPassword(request):
    """
    Endpoint para cambiar la contraseña del usuario autenticado.
    Requiere old_password y new_password en el body.
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not old_password or not new_password:
        return Response(
            {"error": "Debes enviar 'old_password' y 'new_password'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.check_password(old_password):
        return Response(
            {"error": "La contraseña actual es incorrecta."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.set_password(new_password)
    user.save()

    return Response({"mensaje": "Contraseña cambiada exitosamente."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def chatbot_inicio(request):
    rut = request.data.get('rut')
    nombre = request.data.get('nombre')
    telefono = request.data.get('telefono')

    if not rut:
        return Response({"error": "El campo 'rut' es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)

    rut_normalizado = rut.strip().upper()

    try:
        usuario = Usuario.objects.get(rut__iexact=rut_normalizado)
        serializer = UsuarioReadSerializer(usuario)
        return Response({
            "mensaje": "Usuario encontrado",
            "usuario": serializer.data
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        if not nombre or not telefono:
            return Response(
                {"error": "Para registrar un nuevo usuario se requieren 'nombre' y 'telefono'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "rut": rut_normalizado,
            "nombre": nombre,
            "telefono": telefono
        }
        serializer = UsuarioSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()

        return Response({
            "mensaje": "Usuario registrado correctamente",
            "usuario": UsuarioReadSerializer(usuario).data
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def obtenerUsuario(request, usuario_id):
    """
    Obtiene la información de un usuario específico por su ID.
    """
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def registrarSintoma(request):
    """
    Registra un nuevo síntoma para un usuario existente.
    """
    usuario_id = request.data.get('usuario')
    descripcion = request.data.get('descripcion')

    if not usuario_id or not descripcion:
        return Response(
            {"error": "Debes enviar 'usuario' (ID) y 'descripcion'."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {"error": "El usuario especificado no existe."},
            status=status.HTTP_404_NOT_FOUND
        )

    sintoma = Sintoma.objects.create(
        usuario=usuario,
        descripcion=descripcion
    )

    serializer = SintomaSerializer(sintoma)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def listar_sintomas_por_usuario(request, usuario_id):
    sintomas = Sintoma.objects.filter(usuario_id=usuario_id).order_by('-fecha_registro')
    serializer = SintomaSerializer(sintomas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def listarUsuarios(request):
    usuarios = Usuario.objects.all().order_by('id')
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def editarUsuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UsuarioUpdateSerializer(usuario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def eliminarUsuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    usuario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def eliminar_sintoma(request, sintoma_id):
    try:
        sintoma = Sintoma.objects.get(id=sintoma_id)
    except Sintoma.DoesNotExist:
        return Response({'error': 'Síntoma no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    sintoma.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PATCH'])
def editar_sintoma(request, sintoma_id):
    try:
        sintoma = Sintoma.objects.get(id=sintoma_id)
    except Sintoma.DoesNotExist:
        return Response({'error': 'Síntoma no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    descripcion = request.data.get('descripcion')
    if not descripcion:
        return Response({'error': 'El campo descripcion es obligatorio.'}, status=status.HTTP_400_BAD_REQUEST)

    sintoma.descripcion = descripcion
    sintoma.save()

    serializer = SintomaSerializer(sintoma)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def obtenerPerfilUsuario(request):
    """
    Devuelve los datos del usuario autenticado.
    """
    usuario = request.user
    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data, status=status.HTTP_200_OK)