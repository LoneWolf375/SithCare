from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CitaSerializer
from .models import Cita
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, time, timedelta
from django.utils import timezone  # ⬅️ NUEVO
from django.db import IntegrityError  # ⬅️ NUEVO

@csrf_exempt
@api_view(['POST'])
def create_appointment_view(request):
    """
    Permite crear una nueva cita.
    """
    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        try:  # ⬅️ NUEVO: capturar colisión por restricción única
            cita_nueva = serializer.save()
        except IntegrityError:
            return Response({"error": "Ese horario ya está tomado."}, status=status.HTTP_400_BAD_REQUEST)
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

    # ⛔ BLOQUEO DE PASADO (con timezone)
    if timezone.is_naive(nueva_fecha):
        nueva_fecha = timezone.make_aware(nueva_fecha, timezone.get_current_timezone())
    if nueva_fecha <= timezone.now():
        return Response({'error': 'La nueva fecha y hora debe ser en el futuro.'}, status=status.HTTP_400_BAD_REQUEST)

    # ⛔ NUEVO: Evitar mover a un horario ya tomado
    if Cita.objects.filter(fecha_hora=nueva_fecha).exclude(id=cita.id).exists():
        return Response({'error': 'Ese horario ya está tomado.'}, status=status.HTTP_400_BAD_REQUEST)

    try:  # ⬅️ NUEVO: capturar colisión en DB por seguridad
        cita.fecha_hora = nueva_fecha
        cita.save()
    except IntegrityError:
        return Response({'error': 'Ese horario ya está tomado.'}, status=status.HTTP_400_BAD_REQUEST)

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

    # ⛔ BLOQUEO: no permitir consulta de fechas pasadas
    if fecha_obj < timezone.localdate():
        return Response(
            {"error": "No es posible consultar disponibilidad de fechas pasadas."},
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


# ⚠️ Nueva vista para agendar una cita rápidamente desde el frontend
@csrf_exempt
@api_view(['POST'])
def agendar_cita_rapida_view(request):
    """
    Crea una nueva cita a partir de fecha y hora, y devuelve la información de la cita creada.
    """
    usuario_id = request.data.get('usuario_id')
    fecha_str = request.data.get('fecha')
    hora_str = request.data.get('hora')

    if not all([usuario_id, fecha_str, hora_str]):
        return Response(
            {"error": "Los campos 'usuario_id', 'fecha' y 'hora' son obligatorios."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Combinar fecha y hora para crear un objeto datetime
        fecha_hora_dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return Response(
            {"error": "Formato de fecha o hora inválido. Usa YYYY-MM-DD y HH:MM."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ⛔ BLOQUEO DE PASADO (con timezone)
    if timezone.is_naive(fecha_hora_dt):
        fecha_hora_dt = timezone.make_aware(fecha_hora_dt, timezone.get_current_timezone())
    if fecha_hora_dt <= timezone.now():
        return Response({"error": "No se puede agendar en una fecha/hora pasada."}, status=status.HTTP_400_BAD_REQUEST)

    # ⛔ NUEVO: prechequeo de doble reserva (global)
    if Cita.objects.filter(fecha_hora=fecha_hora_dt).exists():
        return Response({"error": "Ese horario ya está tomado."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ NUEVO: tomar motivo desde el body (con valor por defecto)
    motivo_req = request.data.get('motivo', 'Consulta médica agendada por chatbot')

    # Preparar los datos para el serializador de la Cita
    datos_cita = {
        'usuario': usuario_id,
        'fecha_hora': fecha_hora_dt.isoformat(),
        'estado': 'Pendiente',
        'motivo': motivo_req
    }

    serializer = CitaSerializer(data=datos_cita)
    if serializer.is_valid():
        try:  # ⬅️ NUEVO: capturar colisión si ocurre entre prechequeo y save
            cita_nueva = serializer.save()
        except IntegrityError:
            return Response({"error": "Ese horario ya está tomado."}, status=status.HTTP_400_BAD_REQUEST)
        serializer_respuesta = CitaSerializer(cita_nueva)
        return Response({
            "mensaje": "Cita creada con éxito",
            "cita": serializer_respuesta.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ⬇️⬇️⬇️ NUEVO: sugerir la primera fecha/hora disponible
@api_view(['GET'])
def sugerir_proximo_horario(request):
    """
    Devuelve la primera fecha/hora disponible a partir de 'ahora' (horario 09:00–18:00, saltos de 30 min).
    Puedes pasar ?limite_dias=14 (por defecto 30).
    """
    limite_dias = int(request.GET.get('limite_dias', 30))
    ahora = timezone.localtime()

    hora_inicio = time(9, 0)
    hora_fin = time(18, 0)
    intervalo = timedelta(minutes=30)

    def siguiente_slot(t: time) -> time:
        """Redondea hacia arriba al próximo múltiplo de 30 minutos."""
        mins = t.hour * 60 + t.minute
        next_mins = ((mins + 29) // 30) * 30
        h, m = divmod(next_mins, 60)
        return time(h % 24, m)  # no debería pasar de 24 en este flujo

    for offset in range(0, limite_dias + 1):
        fecha_busqueda = (ahora.date() + timedelta(days=offset))

        # Punto de inicio del día:
        if fecha_busqueda == ahora.date():
            start_time = max(hora_inicio, siguiente_slot(ahora.time().replace(second=0, microsecond=0)))
            if start_time >= hora_fin:
                continue  # Hoy ya no quedan slots, pasar al día siguiente
        else:
            start_time = hora_inicio

        # Generar slots del día
        actual_dt = datetime.combine(fecha_busqueda, start_time)
        fin_dt = datetime.combine(fecha_busqueda, hora_fin)

        slots = []
        while actual_dt < fin_dt:
            slots.append(actual_dt.time())
            actual_dt += intervalo

        # Remover ocupados
        citas_ocupadas = Cita.objects.filter(fecha_hora__date=fecha_busqueda).values_list('fecha_hora', flat=True)
        horas_ocupadas = {dt.time().replace(second=0, microsecond=0) for dt in citas_ocupadas}

        for s in slots:
            if s not in horas_ocupadas:
                # Encontrado el primer slot libre
                return Response({
                    "fecha": fecha_busqueda.strftime("%Y-%m-%d"),
                    "hora": s.strftime("%H:%M")
                }, status=status.HTTP_200_OK)

    # Sin resultados dentro del límite
    return Response({"fecha": None, "hora": None}, status=status.HTTP_200_OK)