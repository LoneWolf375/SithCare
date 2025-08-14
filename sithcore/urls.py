from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView  # ✅

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/agendamiento/', include('agendamiento.urls')),
    path('api/chatbot/', include('chatbot.urls')),

    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('triaje/', TemplateView.as_view(template_name='triaje.html'), name='triaje'),
    path('traslado_urgente/', TemplateView.as_view(template_name='traslado_urgente.html'), name='traslado_urgente'),
    path('traslado_confirmado/', TemplateView.as_view(template_name='traslado_confirmado.html'), name='traslado_confirmado'),
    path('profesional_enviado/', TemplateView.as_view(template_name='profesional_enviado.html'), name='profesional_enviado'),
    path('agendamiento/', TemplateView.as_view(template_name='agendamiento.html'), name='agendamiento'),
    path('cita_agendada/', TemplateView.as_view(template_name='cita_agendada.html'), name='cita_agendada'),
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('perfil_usuario/', TemplateView.as_view(template_name='perfil_usuario.html'), name='perfil_usuario'),
    path('motivo/', TemplateView.as_view(template_name='motivo.html'), name='motivo'),
]