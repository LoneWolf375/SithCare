from django.urls import path
from .views import (
    chatbot_preguntas,
    chatbot_evaluar_respuestas,
    chatbot_resolver_traslado
)

urlpatterns = [
    path('preguntas/', chatbot_preguntas, name='chatbot_preguntas'),
    path('evaluar/', chatbot_evaluar_respuestas, name='chatbot_evaluar_respuestas'),
    path('resolver-traslado/', chatbot_resolver_traslado, name='chatbot_resolver_traslado'),
]