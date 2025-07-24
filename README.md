# 🛡️ SithCare Backend

**SithCare** es un sistema de gestión de citas médicas desarrollado con Django, que incluye un **chatbot de triaje automatizado**. Este backend está diseñado para su uso en centros de salud primaria, optimizando la asignación de recursos y reduciendo la saturación de los servicios de urgencia.

---

## 🚀 Funcionalidades principales

- Registro automático de usuarios desde el chatbot.
- Evaluación inicial del paciente a través de triaje automatizado.
- Gestión de síntomas asociados al paciente.
- Módulo de login con autenticación por token.
- CRUD completo de usuarios y síntomas.
- Endpoints RESTful compatibles con frontend FlutterFlow.

---

## 🧱 Tecnologías utilizadas

- Python 3.11
- Django 4+
- Django REST Framework
- SQLite (en fase inicial)
- Git + GitHub (control de versiones)

---

## 🔑 Endpoints principales

### 🗨️ Chatbot
- `POST /api/usuarios/chatbot-inicio/`  
  Inicia flujo conversacional con validación de RUT. Registra nuevo usuario si no existe.

### 👤 Usuarios
- `POST /api/usuarios/registrar/`  
  Crea un nuevo usuario manualmente.
- `POST /api/usuarios/login/`  
  Devuelve token de autenticación.
- `POST /api/usuarios/logout/`  
  Elimina token y cierra sesión.
- `PATCH /api/usuarios/editar/<usuario_id>/`  
  Edita nombre o teléfono del usuario.
- `GET /api/usuarios/perfil/`  
  Retorna el perfil del usuario autenticado (requiere token).
- `DELETE /api/usuarios/eliminar/<usuario_id>/`  
  Elimina un usuario existente.

### ⚕️ Síntomas
- `POST /api/usuarios/registrar-sintoma/`  
  Agrega un síntoma asociado a un usuario.
- `GET /api/usuarios/sintomas/<usuario_id>/`  
  Lista síntomas registrados por un usuario.
- `PATCH /api/usuarios/sintomas/editar/<sintoma_id>/`  
  Edita la descripción de un síntoma.
- `DELETE /api/usuarios/sintomas/eliminar/<sintoma_id>/`  
  Elimina un síntoma específico.

---

## 🛠️ Instalación local

```bash
# Clonar repositorio
git clone https://github.com/LoneWolf-375/sithcare-backend.git
cd sithcare-backend

# Crear entorno virtual
python -m venv venv
source venv/Scripts/activate   # En Windows

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Ejecutar servidor
python manage.py runserver

📜 Licencia
Distribuido bajo licencia Apache 2.0.

🤖 Autor
Yubram Barraza – Desarrollador backend del proyecto SithCare
GitHub: @LoneWolf-375