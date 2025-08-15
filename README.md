# 🛡️ SithCare Backend

**SithCare** es un sistema de gestión de citas médicas desarrollado con Django, que incluye un **chatbot de triaje automatizado**. Este backend está diseñado para su uso en centros de salud primaria, optimizando la asignación de recursos y reduciendo la saturación de los servicios de urgencia.

---

## 🚀 Funcionalidades principales

- Registro automático de usuarios desde el chatbot.
- Evaluación inicial del paciente a través de triaje automatizado.
- Gestión de síntomas asociados al paciente.
- Módulo de login con autenticación por token.
- CRUD completo de usuarios y síntomas.
- Endpoints RESTful compatibles con frontend HTML/JS o FlutterFlow.

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
- `POST /api/usuarios/chatbot-inicio/` – Inicia flujo conversacional con validación de RUT. Registra nuevo usuario si no existe.

### 👤 Usuarios
- `POST /api/usuarios/registrar/` – Crea un nuevo usuario manualmente.
- `POST /api/usuarios/login/` – Devuelve token de autenticación.
- `POST /api/usuarios/logout/` – Elimina token y cierra sesión.
- `PATCH /api/usuarios/editar/<usuario_id>/` – Edita nombre o teléfono del usuario.
- `GET /api/usuarios/perfil/` – Retorna el perfil del usuario autenticado (requiere token).
- `DELETE /api/usuarios/eliminar/<usuario_id>/` – Elimina un usuario existente.

### ⚕️ Síntomas
- `POST /api/usuarios/registrar-sintoma/` – Agrega un síntoma asociado a un usuario.
- `GET /api/usuarios/sintomas/<usuario_id>/` – Lista síntomas registrados por un usuario.
- `PATCH /api/usuarios/sintomas/editar/<sintoma_id>/` – Edita la descripción de un síntoma.
- `DELETE /api/usuarios/sintomas/eliminar/<sintoma_id>/` – Elimina un síntoma específico.

---

## 🛠️ Instalación local

```bash
# 1. Clonar repositorio
git clone https://github.com/LoneWolf375/SithCare.git
cd SithCare

# 2. Crear entorno virtual
python -m venv venv

# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migraciones
python manage.py migrate

# 5. Ejecutar servidor
python manage.py runserver
Acceder en el navegador:
👉 http://127.0.0.1:8000

🌐 Despliegue rápido en producción (VPS/Servidor)
Clonar proyecto en el servidor

bash
Copiar
Editar
git clone https://github.com/LoneWolf375/SithCare.git
cd SithCare
Crear entorno virtual e instalar dependencias

bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Configurar base de datos y migrar

Editar sithcore/settings.py para usar PostgreSQL o MySQL en lugar de SQLite.

Ejecutar:

bash
Copiar
Editar
python manage.py migrate
Crear superusuario

bash
Copiar
Editar
python manage.py createsuperuser
Configurar variables de entorno

Crear un archivo .env en la raíz:

ini
Copiar
Editar
SECRET_KEY=clave_segura
DEBUG=False
ALLOWED_HOSTS=tu_dominio.com,localhost,127.0.0.1
Servidor WSGI/ASGI con Gunicorn

bash
Copiar
Editar
pip install gunicorn
gunicorn sithcore.wsgi:application --bind 0.0.0.0:8000
Reverso con Nginx (opcional pero recomendado).

📂 Estructura de carpetas
php
Copiar
Editar
SithCare/
│
├── agendamiento/         # Módulo para gestión de citas médicas
├── chatbot/              # Lógica del chatbot y flujo de triaje
├── frontend/             # Archivos HTML, CSS y JS del frontend
├── sithcore/             # Configuración principal del proyecto Django
├── static/               # Archivos estáticos (imágenes, CSS, JS)
├── usuarios/             # Gestión de usuarios y autenticación
│
├── db.sqlite3            # Base de datos SQLite (fase inicial)
├── manage.py             # Script principal de Django
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Documentación del proyecto
└── .gitignore            # Archivos/carpetas que no se versionan
📜 Licencia
Distribuido bajo licencia Apache 2.0.

🤖 Autor
Yubram Barraza – Desarrollador backend del proyecto SithCare
GitHub: @LoneWolf375

yaml
Copiar
Editar
