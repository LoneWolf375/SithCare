from django.urls import path
from .views import (
    chatbot_preguntas,
    chatbot_evaluar_respuestas,
    chatbot_resolver_traslado,
    chatbot_guardar_parcial,
    recomendaciones_autocuidado,
    crear_sesion_triaje,
    listar_sesiones,
    contar_sesiones,
)

urlpatterns = [
    path('preguntas/', chatbot_preguntas, name='chatbot_preguntas'),
    path('evaluar/', chatbot_evaluar_respuestas, name='chatbot_evaluar_respuestas'),
    path('resolver-traslado/', chatbot_resolver_traslado, name='chatbot_resolver_traslado'),
    path('guardar-parcial/', chatbot_guardar_parcial, name='chatbot_guardar_parcial'),
    path('recomendaciones/', recomendaciones_autocuidado, name='recomendaciones_autocuidado'),
    path('sesiones/crear/', crear_sesion_triaje, name='crear_sesion_triaje'),
    path('sesiones/listar/', listar_sesiones, name='listar_sesiones'),
    path('sesiones/contar/', contar_sesiones, name='contar_sesiones'),
]