# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Manager personalizado para tu modelo de usuario
class UsuarioManager(BaseUserManager):
    def create_user(self, rut, password=None, **extra_fields):
        if not rut:
            raise ValueError('El RUT es obligatorio')
        
        # Normaliza el RUT para usarlo como username interno
        rut_normalizado = rut.strip().replace("-", "").upper()

        # Asegúrate de que el username se establezca al RUT normalizado
        extra_fields.setdefault('username', rut_normalizado)
        
        # Crea una instancia del usuario
        user = self.model(rut=rut_normalizado, **extra_fields)
        
        # Hashea la contraseña y la asigna al usuario
        if password is not None:
            user.set_password(password)
            
        user.save(using=self._db)
        return user

    def create_superuser(self, rut, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(rut, password, **extra_fields)

# Tu modelo de usuario personalizado
class Usuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    
    # ⚠️ Nuevos campos agregados
    enfermedades_sistemicas = models.TextField(null=True, blank=True)
    tipo_de_sangre = models.CharField(max_length=3, null=True, blank=True)
    
    # Define 'rut' como el campo principal para la autenticación
    USERNAME_FIELD = 'rut'
    # Campos requeridos al crear un superusuario (aparte del USERNAME_FIELD y password)
    REQUIRED_FIELDS = ['nombre', 'telefono', 'email']

    # Asigna el manager personalizado a tu modelo
    objects = UsuarioManager()

    def __str__(self):
        return f'{self.nombre or "N/A"} ({self.rut})'

    def save(self, *args, **kwargs):
        if self.rut:
            self.rut = self.rut.strip().replace(" ", "").upper()
        if not self.username:
            self.username = self.rut
        super().save(*args, **kwargs)