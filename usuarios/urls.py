from django.urls import path
from .views import (
    registrarUsuario,
    loginUsuario,
    logoutUsuario,
    cambiarPassword,
    chatbot_inicio,
    registrarSintoma,
    registrar_sintoma_chatbot,
    listar_sintomas_por_usuario,
    listarUsuarios,
    obtenerUsuario,
    editarUsuario,
    eliminarUsuario,
    eliminar_sintoma,
    editar_sintoma,
    obtener_perfil_con_cita_view,
    editar_perfil_view 
)

from django.views.generic import TemplateView


urlpatterns = [
    # Auth
    path('registrar/', registrarUsuario, name='registrar_usuario'),
    path('login/', loginUsuario, name='login_usuario'),
    path('logout/', logoutUsuario, name='logout_usuario'),
    path('cambiar-password/', cambiarPassword, name='cambiar_password'),

    # Perfil (Vistas API)
    path('perfil/', obtener_perfil_con_cita_view, name='obtener_perfil_con_cita'),
    path('perfil/editar/<int:usuario_id>/', editar_perfil_view, name='editar_perfil'),
    
    # Chatbot
    path('chatbot-inicio/', chatbot_inicio, name='chatbot_inicio'),
    path('registrar-sintoma/', registrar_sintoma_chatbot, name='registrar_sintoma_chatbot'),

    # Usuarios
    path('', listarUsuarios, name='listar_usuarios'),
    path('<int:usuario_id>/', obtenerUsuario, name='obtener_usuario'),
    path('<int:usuario_id>/sintomas/', listar_sintomas_por_usuario, name='listar_sintomas'),
    path('editar/<int:usuario_id>/', editarUsuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', eliminarUsuario, name='eliminar_usuario'),
    
    # Vistas para renderizar templates (no API)
    path('perfil_usuario/', TemplateView.as_view(template_name='perfil_usuario.html'), name='perfil_usuario_html'),

    # Síntomas
    path('sintomas/<int:sintoma_id>/editar/', editar_sintoma, name='editar_sintoma'),
    path('sintomas/<int:sintoma_id>/eliminar/', eliminar_sintoma, name='eliminar_sintoma'),
]