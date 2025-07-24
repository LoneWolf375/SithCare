from django.urls import path
from .views import (
    registrarUsuario,
    LoginUsuarioView,
    logoutUsuario,
    cambiarPassword,
    obtenerPerfilUsuario,
    chatbot_inicio,
    registrarSintoma,
    listar_sintomas_por_usuario,
    listarUsuarios,
    obtenerUsuario,
    editarUsuario,
    eliminarUsuario,
    eliminar_sintoma,
    editar_sintoma
)

urlpatterns = [
    # Auth
    path('registrar/', registrarUsuario, name='registrar_usuario'),
    path('login/', LoginUsuarioView.as_view(), name='login_usuario'),
    path('logout/', logoutUsuario, name='logout_usuario'),
    path('cambiar-password/', cambiarPassword, name='cambiar_password'),

    # Perfil
    path('me/', obtenerPerfilUsuario, name='obtener_perfil_usuario'),

    # Chatbot
    path('chatbot-inicio/', chatbot_inicio, name='chatbot_inicio'),

    # Usuarios
    path('', listarUsuarios, name='listar_usuarios'),
    path('<int:usuario_id>/', obtenerUsuario, name='obtener_usuario'),
    path('<int:usuario_id>/sintomas/', listar_sintomas_por_usuario, name='listar_sintomas'),
    path('editar/<int:usuario_id>/', editarUsuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', eliminarUsuario, name='eliminar_usuario'),

    # Síntomas
    path('registrar-sintoma/', registrarSintoma, name='registrar_sintoma'),
    path('sintomas/<int:sintoma_id>/editar/', editar_sintoma, name='editar_sintoma'),
    path('sintomas/<int:sintoma_id>/eliminar/', eliminar_sintoma, name='eliminar_sintoma'),
]