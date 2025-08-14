from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
def chatbot_preguntas(request):
    """
    Devuelve la lista de preguntas del chatbot para clasificación de urgencia.
    Ordenadas para flags críticos primero y score ponderado después.
    """
    preguntas = [
        "¿Presentas dificultad para respirar?",                          # Flag crítico
        "¿Presentas dolor en el pecho?",                                 # Flag crítico
        "¿Presentas confusión o desorientación?",                        # Flag crítico
        "¿Has sufrido un trauma reciente grave?",                        # Flag crítico
        "¿Sientes fiebre alta (sobre 38.5 °C)?",                         # Puntaje
        "¿Tienes dolor muy intenso (8 o más de 10)?",                     # Puntaje
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
    score = sum([peso for respuesta, peso in zip(respuestas, pesos) if respuesta])

    indices_criticos = [0, 1, 2, 3, 4, 5, 6]
    es_urgencia_flag = any([respuestas[i] for i in indices_criticos])
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

    # Aquí podrías guardar en base de datos si lo deseas (o no hacer nada todavía)
    return Response({"mensaje": "Primera parte del triaje registrada."}, status=200)

@api_view(['POST'])
def chatbot_resolver_traslado(request):
    """
    Responde al usuario orientando según su capacidad de traslado.
    """
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