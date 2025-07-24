# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

# admin.site.register(Usuario) # Puedes dejar esta línea comentada

class CustomUserAdmin(UserAdmin):
    # Definición de cómo se mostrará el modelo Usuario en la lista (esto ya lo hicimos antes)
    list_display = ('username', 'rut', 'nombre', 'telefono', 'is_staff', 'is_active')
    search_fields = ('username', 'rut', 'nombre', 'telefono')
    ordering = ('username',) # Opcional: ordena la lista por username

    # Definición de campos que aparecerán en el formulario al EDITAR un usuario existente
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('rut', 'nombre', 'telefono', 'email')}), # Agregamos tus campos aquí
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Definición de campos que aparecerán en el formulario al AGREGAR un NUEVO usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'rut', 'nombre', 'telefono', 'email', 'password', 'password2') # Agregamos tus campos aquí
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )


admin.site.register(Usuario, CustomUserAdmin)