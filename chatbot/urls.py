from django.urls import path
from .views import (
    chatbot_preguntas,
    chatbot_evaluar_respuestas,
    chatbot_resolver_traslado,
    chatbot_guardar_parcial
)

urlpatterns = [
    path('preguntas/', chatbot_preguntas, name='chatbot_preguntas'),
    path('evaluar/', chatbot_evaluar_respuestas, name='chatbot_evaluar_respuestas'),
    path('resolver-traslado/', chatbot_resolver_traslado, name='chatbot_resolver_traslado'),
    path('guardar-parcial/', chatbot_guardar_parcial, name='chatbot_guardar_parcial'),
]