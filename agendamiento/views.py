from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CitaSerializer
from .models import Cita
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta

@csrf_exempt
@api_view(['POST'])
def create_appointment_view(request):
    """
    Permite crear una nueva cita.
    """
    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        cita_nueva = serializer.save()
        serializer_respuesta = CitaSerializer(cita_nueva)
        return Response({
            "mensaje": "Cita creada con éxito",
            "cita": serializer_respuesta.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def listar_citas_por_usuario(request, usuario_id):
    """
    Lista todas las citas asociadas a un usuario específico, con filtros opcionales.
    ?estado=Pendiente
    ?desde=2025-06-01
    ?hasta=2025-06-30
    """
    citas = Cita.objects.filter(usuario_id=usuario_id)

    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if estado:
        citas = citas.filter(estado=estado)

    if desde:
        try:
            fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
            citas = citas.filter(fecha_hora__date__gte=fecha_desde)
        except ValueError:
            return Response({"error": "Formato de fecha 'desde' inválido. Usa YYYY-MM-DD."}, status=400)

    if hasta:
        try:
            fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
            citas = citas.filter(fecha_hora__date__lte=fecha_hasta)
        except ValueError:
            return Response({"error": "Formato de fecha 'hasta' inválido. Usa YYYY-MM-DD."}, status=400)

    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def obtener_cita(request, cita_id):
    """
    Devuelve el detalle de una cita específica por ID.
    """
    try:
        cita = Cita.objects.get(id=cita_id)
        serializer = CitaSerializer(cita)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cita.DoesNotExist:
        return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def eliminar_cita(request, cita_id):
    """
    Elimina una cita existente por su ID.
    """
    try:
        cita = Cita.objects.get(id=cita_id)
        cita.delete()
        return Response({'mensaje': 'Cita eliminada correctamente'}, status=status.HTTP_204_NO_CONTENT)
    except Cita.DoesNotExist:
        return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def actualizar_estado_cita(request, cita_id):
    """
    Permite actualizar el estado de una cita específica.
    Solo acepta: Pendiente, Completada, Cancelada.
    """
    try:
        cita = Cita.objects.get(id=cita_id)
    except Cita.DoesNotExist:
        return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = request.data.get('estado')
    ESTADOS_VALIDOS = ['Pendiente', 'Completada', 'Cancelada']

    if nuevo_estado not in ESTADOS_VALIDOS:
        return Response(
            {'error': f"Estado inválido. Debe ser uno de: {', '.join(ESTADOS_VALIDOS)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    cita.estado = nuevo_estado
    cita.save()
    return Response({
        'mensaje': 'Estado actualizado correctamente',
        'cita_id': cita.id,
        'estado_nuevo': cita.estado
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def reprogramar_cita(request, cita_id):
    """
    Permite reprogramar la fecha y hora de una cita específica.
    """
    try:
        cita = Cita.objects.get(id=cita_id)
    except Cita.DoesNotExist:
        return Response({'error': 'Cita no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    nueva_fecha_hora = request.data.get('fecha_hora')

    if not nueva_fecha_hora:
        return Response({'error': 'El campo fecha_hora es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        nueva_fecha = datetime.fromisoformat(nueva_fecha_hora.replace("Z", "+00:00"))
    except ValueError:
        return Response({'error': 'Formato de fecha_hora inválido. Usa formato ISO8601.'}, status=status.HTTP_400_BAD_REQUEST)

    if nueva_fecha <= datetime.now(nueva_fecha.tzinfo):
        return Response({'error': 'La nueva fecha y hora debe ser en el futuro.'}, status=status.HTTP_400_BAD_REQUEST)

    cita.fecha_hora = nueva_fecha
    cita.save()

    return Response({
        'mensaje': 'Cita reprogramada correctamente',
        'cita_id': cita.id,
        'nueva_fecha_hora': cita.fecha_hora
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def listar_todas_citas(request):
    """
    Endpoint administrativo para listar todas las citas, con filtros opcionales.
    ?estado=Pendiente
    ?desde=YYYY-MM-DD
    ?hasta=YYYY-MM-DD
    """
    citas = Cita.objects.all()

    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    if estado:
        citas = citas.filter(estado=estado)

    if desde:
        try:
            fecha_desde = datetime.strptime(desde, "%Y-%m-%d")
            citas = citas.filter(fecha_hora__date__gte=fecha_desde)
        except ValueError:
            return Response({"error": "Formato de fecha 'desde' inválido. Usa YYYY-MM-DD."}, status=400)

    if hasta:
        try:
            fecha_hasta = datetime.strptime(hasta, "%Y-%m-%d")
            citas = citas.filter(fecha_hora__date__lte=fecha_hasta)
        except ValueError:
            return Response({"error": "Formato de fecha 'hasta' inválido. Usa YYYY-MM-DD."}, status=400)

    citas = citas.order_by('fecha_hora')
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def verificar_disponibilidad(request):
    """
    Endpoint para consultar horas disponibles en un día específico.
    Horario fijo 09:00 - 17:30, intervalos de 30 min.
    Filtra horas ya agendadas.
    """
    fecha_str = request.data.get('fecha')
    if not fecha_str:
        return Response(
            {"error": "El campo 'fecha' es obligatorio. Usa formato YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return Response(
            {"error": "Formato de fecha inválido. Usa YYYY-MM-DD."},
            status=status.HTTP_400_BAD_REQUEST
        )

    hora_inicio = time(9, 0)
    hora_fin = time(18, 0)
    intervalo = timedelta(minutes=30)

    slots = []
    actual_dt = datetime.combine(fecha_obj, hora_inicio)
    fin_dt = datetime.combine(fecha_obj, hora_fin)

    while actual_dt < fin_dt:
        slots.append(actual_dt.time())
        actual_dt += intervalo

    citas_ocupadas = Cita.objects.filter(
        fecha_hora__date=fecha_obj
    ).values_list('fecha_hora', flat=True)

    horas_ocupadas = [cita_dt.time().replace(second=0, microsecond=0) for cita_dt in citas_ocupadas]

    horas_disponibles = [
        slot.strftime("%H:%M")
        for slot in slots
        if slot not in horas_ocupadas
    ]

    return Response({
        "fecha": fecha_str,
        "horas_disponibles": horas_disponibles
    }, status=status.HTTP_200_OK)