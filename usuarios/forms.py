from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'rol',
            'nombre',
            'apellidos',
            'correo',
            'telefono',
            'password',
            'tipo_documento',
            'num_documento',
            'fecha_nacimiento',
            'id_categoria',
            'estado',
        ]

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Verificar contraseña")
    
    class Meta:
        model = Usuario
        fields = [
            'nombre',
            'apellidos',
            'telefono',
            'correo',
            'password',
            'tipo_documento',
            'num_documento',
            'fecha_nacimiento',
            'id_categoria',
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        # Convertir el correo a minúsculas para consistencia
        correo = cleaned_data.get("correo")
        if correo:
            cleaned_data["correo"] = correo.lower()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")
        return cleaned_data

class CustomLoginForm(forms.Form):
    correo = forms.CharField(label="Correo", max_length=50)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get("correo")
        password = cleaned_data.get("password")
        if correo and password:
            # Convertir el correo a minúsculas para comparar con lo almacenado
            correo = correo.lower()
            try:
                user = Usuario.objects.get(correo=correo)
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Credenciales incorrectas")
            if not user.check_password(password):
                raise forms.ValidationError("Credenciales incorrectas")
            # Se agrega el usuario validado al diccionario cleaned_data para usarlo luego
            cleaned_data["user"] = user
        return cleaned_data
