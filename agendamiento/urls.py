from django.urls import path
from agendamiento.views import (
    create_appointment_view,
    listar_citas_por_usuario,
    obtener_cita,
    eliminar_cita,
    actualizar_estado_cita,
    reprogramar_cita,
    listar_todas_citas,
    verificar_disponibilidad,
    agendar_cita_rapida_view,
    sugerir_proximo_horario,
)

urlpatterns = [
    # CRUD de citas
    path('citas/crear/', create_appointment_view, name='create_appointment'),
    path('citas/', listar_todas_citas, name='listar_todas_citas'),
    path('citas/usuario/<int:usuario_id>/', listar_citas_por_usuario, name='listar_citas'),
    path('citas/<int:cita_id>/', obtener_cita, name='obtener_cita'),
    path('citas/<int:cita_id>/eliminar/', eliminar_cita, name='eliminar_cita'),
    path('citas/<int:cita_id>/estado/', actualizar_estado_cita, name='actualizar_estado_cita'),
    path('citas/<int:cita_id>/reprogramar/', reprogramar_cita, name='reprogramar_cita'),
    path('citas/disponibilidad/', verificar_disponibilidad, name='verificar_disponibilidad'),
    path('citas/agendar/', agendar_cita_rapida_view, name='agendar_cita_rapida'),
    path('citas/sugerir/', sugerir_proximo_horario, name='sugerir_proximo_horario')
]