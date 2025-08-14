from django.db import IntegrityError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from datetime import datetime
from .utils import validar_formato_rut
from .models import Usuario
from chatbot.models import Sintoma
from agendamiento.models import Cita
from .serializers import (
    UsuarioSerializer,
    SintomaSerializer,
    UsuarioUpdateSerializer,
    UsuarioReadSerializer,
    UsuarioProfileSerializer,
)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@permission_classes([AllowAny])
def registrarUsuario(request):
    try:
        data = request.data
        if "password" not in data or not data["password"]:
            return Response({"error": "La contraseña es obligatoria."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UsuarioSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({
            "id": user.id,
            "nombre": user.nombre,
            "rut": user.rut,
            "telefono": user.telefono,
            "token": token.key,
            "username": user.username
        }, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({"error": "El RUT ya está registrado."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error en registrarUsuario: {e}")
        return Response({"error": "Ocurrió un error al registrar el usuario."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def loginUsuario(request):
    rut = request.data.get('rut')
    password = request.data.get('password')
    if not rut or not password:
        return Response({"error": "Debes enviar rut y contraseña."}, status=status.HTTP_400_BAD_REQUEST)
    rut_normalizado = rut.strip().replace("-", "").upper()
    user = authenticate(request, username=rut_normalizado, password=password)
    if user is None:
        return Response({"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "token": token.key,
        "user_id": user.id,
        "username": user.username
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logoutUsuario(request):
    request.user.auth_token.delete()
    return Response({"mensaje": "Logout exitoso. Token eliminado."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cambiarPassword(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not old_password or not new_password:
        return Response({"error": "Debes enviar 'old_password' y 'new_password'."}, status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(old_password):
        return Response({"error": "La contraseña actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
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
    rut_normalizado = rut.strip().replace(" ", "").upper()
    print(f"Intentando con RUT normalizado: {rut_normalizado}")
    try:
        usuario_existente = Usuario.objects.get(rut__iexact=rut_normalizado)
        serializer = UsuarioReadSerializer(usuario_existente)
        return Response({"mensaje": "Usuario encontrado", "usuario": serializer.data}, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        if not nombre or not telefono:
            return Response({"error": "Para registrar un nuevo usuario se requieren 'nombre' y 'telefono'."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            email = request.data.get('email', '')
            serializer = UsuarioSerializer(data={
                "rut": rut_normalizado,
                "nombre": nombre,
                "telefono": telefono,
                "email": email
            })
            serializer.is_valid(raise_exception=True)
            nuevo_usuario = serializer.save()
            return Response({
                "mensaje": "Usuario registrado correctamente",
                "usuario": UsuarioReadSerializer(nuevo_usuario).data
            }, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            print(f"⛔ Error de integridad: {e}")
            return Response({"error": "Ya existe un usuario con este RUT."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("🛑 Error interno en chatbot_inicio:", str(e))
            return Response({"error": "No se pudo registrar el usuario. Revisa el formato del RUT y los datos enviados."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtenerUsuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    serializer = UsuarioSerializer(usuario)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def registrarSintoma(request):
    rut = request.data.get('usuario')
    descripcion = request.data.get('descripcion')
    if not rut or not descripcion:
        return Response({"error": "Debes enviar 'usuario' (RUT) y 'descripcion'."}, status=status.HTTP_400_BAD_REQUEST)
    rut_normalizado = rut.strip().replace("-", "").upper()
    if not validar_formato_rut(rut_normalizado):
        return Response({"error": "Formato de RUT inválido. Usa el formato 12345678-9 o 12345678-K."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        usuario = Usuario.objects.get(rut__iexact=rut_normalizado)
    except Usuario.DoesNotExist:
        return Response({"error": "El usuario especificado no existe."}, status=status.HTTP_404_NOT_FOUND)
    sintoma = Sintoma.objects.create(usuario=usuario, descripcion=descripcion)
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
def obtener_perfil_con_cita_view(request):
    """
    Devuelve el perfil completo del usuario autenticado, sin anonimizar,
    junto con su próxima cita si la hay.
    """
    usuario = request.user
    usuario_data = UsuarioProfileSerializer(usuario).data
    try:
        proxima_cita = Cita.objects.filter(
            usuario=usuario,
            fecha_hora__gte=datetime.now()
        ).order_by('fecha_hora').first()
        cita_data = None
        if proxima_cita:
            cita_data = {
                'fecha': proxima_cita.fecha_hora.strftime("%d-%m-%Y"),
                'hora': proxima_cita.fecha_hora.strftime("%H:%M"),
            }
        usuario_data['proxima_cita'] = cita_data
        return Response(usuario_data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error al obtener el perfil con cita: {e}")
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@csrf_exempt
def editar_perfil_view(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Verifica que el usuario autenticado sea el dueño del perfil
    if usuario != request.user:
        return Response(
            {"error": "No tienes permiso para editar este perfil."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Valida sólo los campos permitidos (enfermedades_sistemicas, tipo_de_sangre, telefono)
    serializer = UsuarioUpdateSerializer(usuario, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Actualiza los campos manualmente según lo validado
    validated_data = serializer.validated_data
    if 'enfermedades_sistemicas' in validated_data:
        usuario.enfermedades_sistemicas = validated_data['enfermedades_sistemicas']
    if 'tipo_de_sangre' in validated_data:
        usuario.tipo_de_sangre = validated_data['tipo_de_sangre']
    if 'telefono' in validated_data:
        usuario.telefono = validated_data['telefono']
    # Si en el futuro amplías UsuarioUpdateSerializer con más campos, actualízalos aquí

    usuario.save()

    # Devuelve el usuario actualizado usando el serializador de perfil completo
    updated_data = UsuarioProfileSerializer(usuario).data
    return Response(updated_data, status=status.HTTP_200_OK)

def perfil_usuario_view(request):
    return render(request, 'usuarios/perfil_usuario.html')

@login_required(login_url='/login/')
def perfil_usuario_html_view(request):
    return render(request, 'perfil_usuario.html')

@login_required(login_url='/login/')
def agendamiento_html_view(request):
    return render(request, 'agendamiento.html')


@api_view(['POST'])
def registrar_sintoma_chatbot(request):
    data = request.data
    usuario_id = data.get('usuario_id')
    if not usuario_id:
        return Response({"error": "Falta el ID del usuario."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    dificultadRespirar = data.get('dificultadRespirar', False)
    dolorPecho = data.get('dolorPecho', False)
    confusion = data.get('confusion', False)
    trauma = data.get('trauma', False)
    fiebreAlta = data.get('fiebreAlta', False)
    dolorIntenso = data.get('dolorIntenso', False)
    vomitosDiarrea = data.get('vomitosDiarrea', False)
    enfermedadCronica = data.get('enfermedadCronica', False)
    flags_criticos = [dificultadRespirar, dolorPecho, confusion, trauma]
    puntaje = sum([fiebreAlta, dolorIntenso, vomitosDiarrea, enfermedadCronica])
    if any(flags_criticos):
        resultado = "⚠️ Clasificación: URGENCIA"
        es_urgencia = True
    elif puntaje >= 2:
        resultado = "⚠️ Clasificación: OBSERVACIÓN PRIORITARIA"
        es_urgencia = False
    else:
        resultado = "✅ Clasificación: NO URGENCIA"
        es_urgencia = False
    return Response({"resultado": resultado, "urgente": es_urgencia}, status=status.HTTP_201_CREATED)
