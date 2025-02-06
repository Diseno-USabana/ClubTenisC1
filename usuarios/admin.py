# usuarios/admin.py
from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Usuario, Categoria

class UsuarioAdminForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True), 
        required=False,
        help_text="Ingrese una contraseña en texto plano. Se almacenará en forma hasheada."
    )

    class Meta:
        model = Usuario
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Si se ingresó una contraseña y no parece estar hasheada (por ejemplo, no empieza con el identificador del algoritmo)
        if password and not password.startswith('pbkdf2_'):
            return make_password(password)
        return password

class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm  # Usamos el formulario personalizado
    list_display = (
        'nombre', 'apellidos', 'correo', 'telefono', 'rol',
        'tipo_documento', 'num_documento', 'fecha_nacimiento',
        'id_categoria', 'estado', 'matricula'
    )
    search_fields = ('nombre', 'apellidos', 'correo', 'num_documento')
    list_filter = ('rol', 'estado', 'tipo_documento')
    
    # Organizar los campos en secciones dentro del formulario
    fieldsets = (
        (None, {
            'fields': ('rol', 'nombre', 'apellidos', 'correo', 'telefono', 'password')
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
