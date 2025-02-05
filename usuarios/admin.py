# usuarios/admin.py
from django.contrib import admin
from .models import Usuario, Categoria

class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'nombre', 'apellidos', 'email', 'telefono', 'rol',
        'tipo_documento', 'num_documento', 'fecha_nacimiento',
        'id_categoria', 'estado', 'matricula'
    )
    search_fields = ('nombre', 'apellidos', 'email', 'num_documento')
    list_filter = ('rol', 'estado', 'tipo_documento')
    
    # Organizar los campos en secciones dentro del formulario
    fieldsets = (
        (None, {
            'fields': ('username', 'rol', 'nombre', 'apellidos', 'email', 'telefono', 'password')
        }),
        ('Datos de identificación', {
            'fields': ('tipo_documento', 'num_documento')
        }),
        ('Información adicional', {
            'fields': ('fecha_nacimiento', 'id_categoria', 'estado', 'matricula')
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Categoria)
