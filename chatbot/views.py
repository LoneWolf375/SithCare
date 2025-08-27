from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import SesionTriaje
from .serializers import SesionTriajeCreateSerializer, SesionTriajeSerializer
from datetime import datetime

# ==========================
# Utilidad interna: misma lógica de urgencia que /evaluar
# ==========================
def _es_urgencia_con_respuestas(respuestas_obj: dict) -> bool:
    """
    Reproduce la misma evaluación que usas en chatbot_evaluar_respuestas.
    Flags críticos: SOLO los 4 primeros (0..3).
    Las otras 4 (fiebreAlta, dolorIntenso, vomitosDiarrea, enfermedadCronica) suman al score.
    """
    respuestas = [
        respuestas_obj.get('dificultadRespirar', False),
        respuestas_obj.get('dolorPecho', False),
        respuestas_obj.get('confusion', False),
        respuestas_obj.get('trauma', False),
        respuestas_obj.get('fiebreAlta', False),
        respuestas_obj.get('dolorIntenso', False),
        respuestas_obj.get('vomitosDiarrea', False),
        respuestas_obj.get('enfermedadCronica', False)
    ]

    pesos = [5, 5, 5, 3, 4, 5, 2, 1]
    score = sum(p for r, p in zip(respuestas, pesos) if r)

    # ✅ SOLO 0..3 son críticos
    indices_criticos = [0, 1, 2, 3]
    es_urgencia_flag = any(respuestas[i] for i in indices_criticos)
    es_urgencia_score = score >= 5

    return bool(es_urgencia_flag or es_urgencia_score)


@api_view(['GET'])
def chatbot_preguntas(request):
    """
    Devuelve la lista de preguntas del chatbot para clasificación de urgencia.
    Flags críticos primero y luego puntaje.
    """
    preguntas = [
        "¿Presentas dificultad para respirar?",                          # Flag crítico
        "¿Presentas dolor en el pecho?",                                 # Flag crítico
        "¿Presentas confusión o desorientación?",                        # Flag crítico
        "¿Has sufrido un trauma reciente grave?",                        # Flag crítico
        "¿Sientes fiebre alta (sobre 38.5 °C)?",                         # Puntaje
        "¿Tienes dolor muy intenso (8 o más de 10)?",                    # Puntaje
        "¿Has tenido vómitos o diarreas intensos y persistentes (más de 6 episodios en 24 horas)?",  # Puntaje
        "¿Padeces alguna enfermedad crónica (HTA, diabetes, dislipidemia, etc.)?"                   # Puntaje
    ]
    return Response({"preguntas": preguntas}, status=status.HTTP_200_OK)


@api_view(['POST'])
def chatbot_evaluar_respuestas(request):
    respuestas_obj = request.data.get('respuestas', {})

    respuestas = [
        respuestas_obj.get('dificultadRespirar', False),
        respuestas_obj.get('dolorPecho', False),
        respuestas_obj.get('confusion', False),
        respuestas_obj.get('trauma', False),
        respuestas_obj.get('fiebreAlta', False),
        respuestas_obj.get('dolorIntenso', False),
        respuestas_obj.get('vomitosDiarrea', False),
        respuestas_obj.get('enfermedadCronica', False)
    ]

    pesos = [5, 5, 5, 3, 4, 5, 2, 1]
    score = sum(p for r, p in zip(respuestas, pesos) if r)

    # ✅ SOLO 0..3 son críticos
    indices_criticos = [0, 1, 2, 3]
    es_urgencia_flag = any(respuestas[i] for i in indices_criticos)
    es_urgencia_score = score >= 5

    es_urgencia = es_urgencia_flag or es_urgencia_score

    if es_urgencia:
        resultado = {
            "urgente": True,
            "mensaje": "Presenta criterios de urgencia. Debe acudir a un servicio de urgencia.",
            "score": score
        }
    else:
        resultado = {
            "urgente": False,
            "mensaje": "No presenta criterios de urgencia. Puede continuar con el proceso de agendamiento de cita médica.",
            "score": score
        }

    return Response({
        "urgente": resultado["urgente"],
        "resultado": resultado["mensaje"]
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def chatbot_guardar_parcial(request):
    respuestas = request.data.get('respuestas')

    if not isinstance(respuestas, list) or len(respuestas) != 8:
        return Response({"error": "Debe enviar una lista de 8 respuestas."}, status=400)

    return Response({"mensaje": "Primera parte del triaje registrada."}, status=200)


@api_view(['POST'])
def chatbot_resolver_traslado(request):
    puede_trasladarse = request.data.get('puede_trasladarse')

    if not isinstance(puede_trasladarse, bool):
        return Response(
            {"error": "El campo 'puede_trasladarse' debe ser True o False."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if puede_trasladarse:
        mensaje = "Por favor acuda lo antes posible al servicio de urgencia más cercano."
    else:
        mensaje = "Entendido. Se enviará un médico o equipo de salud a su ubicación para atención urgente."

    return Response({"mensaje": mensaje}, status=status.HTTP_200_OK)


# ==========================
# Recomendaciones de autocuidado (NO urgencia)
# ==========================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recomendaciones_autocuidado(request):
    """
    Usa el MISMO objeto 'respuestas' del triaje.
    Devuelve recomendaciones SOLO si NO es urgencia.
    """
    data = request.data or {}
    respuestas_obj = data.get("respuestas", {})
    edad = data.get("edad")
    embarazada = bool(data.get("embarazada", False))
    comorbilidades = [str(x).strip().lower() for x in (data.get("comorbilidades") or [])]

    if not isinstance(respuestas_obj, dict) or not respuestas_obj:
        return Response({"error": "Debe enviar el objeto 'respuestas' del triaje."}, status=400)

    # Revalidar con la lógica corregida
    if _es_urgencia_con_respuestas(respuestas_obj):
        return Response({"error": "El módulo de autocuidado solo aplica cuando el caso NO es urgente."}, status=400)

    reglas = {
        "fiebreAlta": [
            "Hidrátate bien (agua o sueros de rehidratación).",
            "Controla la temperatura con paños tibios/fríos.",
            "Puedes usar paracetamol si no tienes contraindicación."
        ],
        "dolorIntenso": [
            "Descansa en un lugar cómodo y evita esfuerzos.",
            "Prueba frío o calor local según alivie mejor.",
            "Usa analgésico simple si no tienes contraindicación y reevalúa en 12–24 h."
        ],
        "vomitosDiarrea": [
            "Rehidrátate con sueros de rehidratación oral en pequeños sorbos frecuentes.",
            "Evita comidas grasosas y lácteos por 24–48 h; dieta blanda (arroz, sopa, pan tostado).",
            "Reintroduce alimentos gradualmente cuando ceda la sintomatología."
        ],
        "enfermedadCronica": [
            "Mantén tu medicación habitual y no la suspendas sin indicación médica.",
            "Controla signos de alarma (empeoramiento súbito, fiebre persistente, descompensación).",
            "Evita automedicación que pueda interactuar con tus tratamientos; consulta si tienes dudas."
        ],
    }

    recomendaciones, notas = [], []

    if respuestas_obj.get("fiebreAlta"):
        recomendaciones.extend(reglas["fiebreAlta"])
    if respuestas_obj.get("dolorIntenso"):
        recomendaciones.extend(reglas["dolorIntenso"])
    if respuestas_obj.get("vomitosDiarrea"):
        recomendaciones.extend(reglas["vomitosDiarrea"])
    if respuestas_obj.get("enfermedadCronica"):
        recomendaciones.extend(reglas["enfermedadCronica"])

    if embarazada:
        notas.append("Si estás embarazada, evita automedicarte; prioriza paracetamol y consulta si persisten los síntomas.")
    if isinstance(edad, int) and edad >= 65:
        notas.append("Mayor de 65 años: vigila hidratación y temperatura; consulta si hay empeoramiento.")
    if any(c in comorbilidades for c in ["asma", "epoc", "cardiopatía", "cardiopatia", "diabetes"]):
        notas.append("Con comorbilidades, controla síntomas de cerca y consulta si no mejoran.")

    if not recomendaciones:
        recomendaciones.append("Descansa, hidrátate y observa la evolución por 24–48 h.")
        recomendaciones.append("Si los síntomas persisten o empeoran, agenda una consulta.")

    recomendaciones.append("Si aparecen señales de alarma (disnea, dolor torácico intenso, confusión, desmayo), acude a urgencias.")

    def uniq(seq):
        seen, out = set(), []
        for x in seq:
            if x not in seen:
                out.append(x); seen.add(x)
        return out

    return Response({
        "recomendaciones": uniq(recomendaciones),
        "notas": uniq(notas)
    }, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_sesion_triaje(request):
    """
    Registra una sesión de triaje.
    Body:
      - respuestas (dict) [obligatorio]
      - urgente (bool)    [opcional] -> si no viene, se calcula
      - score (int)       [opcional] -> si no viene, se calcula
      - recomendaciones (list[str]) [opcional]
    """
    data = request.data or {}
    respuestas = data.get('respuestas')
    if not isinstance(respuestas, dict):
        return Response({"error": "Debe enviar 'respuestas' como objeto."}, status=400)

    # Recalcular si no se envía score/urgente
    if 'urgente' not in data or 'score' not in data:
        ordered = [
            respuestas.get('dificultadRespirar', False),
            respuestas.get('dolorPecho', False),
            respuestas.get('confusion', False),
            respuestas.get('trauma', False),
            respuestas.get('fiebreAlta', False),
            respuestas.get('dolorIntenso', False),
            respuestas.get('vomitosDiarrea', False),
            respuestas.get('enfermedadCronica', False)
        ]
        pesos = [5, 5, 5, 3, 4, 5, 2, 1]
        score = sum(p for r, p in zip(ordered, pesos) if r)
        urgente = _es_urgencia_con_respuestas(respuestas)
        data['score'] = score
        data['urgente'] = urgente

    # Asociar usuario autenticado por defecto
    data.setdefault('usuario', getattr(request.user, 'id', None))

    ser = SesionTriajeCreateSerializer(data=data)
    ser.is_valid(raise_exception=True)
    sesion = ser.save()
    return Response(SesionTriajeSerializer(sesion).data, status=201)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def listar_sesiones(request):
    """
    ADMIN: lista sesiones con filtros opcionales:
      ?usuario_id=...  ?desde=YYYY-MM-DD  ?hasta=YYYY-MM-DD  ?urgente=true/false
    """
    qs = SesionTriaje.objects.all()

    uid = request.GET.get('usuario_id')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    urgente = request.GET.get('urgente')

    if uid:
        qs = qs.filter(usuario_id=uid)
    if urgente in ('true', 'false'):
        qs = qs.filter(urgente=(urgente == 'true'))
    if desde:
        qs = qs.filter(creado_en__date__gte=datetime.strptime(desde, "%Y-%m-%d").date())
    if hasta:
        qs = qs.filter(creado_en__date__lte=datetime.strptime(hasta, "%Y-%m-%d").date())

    data = SesionTriajeSerializer(qs[:500], many=True).data
    return Response(data, status=200)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def contar_sesiones(request):
    """
    ADMIN: conteo global de sesiones.
    """
    total = SesionTriaje.objects.count()
    urg = SesionTriaje.objects.filter(urgente=True).count()
    no_urg = total - urg
    return Response({"total": total, "urgentes": urg, "no_urgentes": no_urg}, status=200)