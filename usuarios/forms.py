# usuarios/forms.py
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
    # Campo opcional para nivel (solo requerido para adultos)
    nivel = forms.ChoiceField(
        choices=[
            ("basico", "Basico"),
            ("intermedio", "Intermedio"),
            ("avanzado", "Avanzado")
        ],
        required=False,
        label="Nivel de juego"
    )
    
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
            'nivel',
        ]
        widgets = {
            # Renderiza la fecha como un date picker (HTML5)
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Convertir correo a minúsculas para consistencia
        correo = cleaned_data.get("correo")
        if correo:
            correo = correo.lower()
            cleaned_data["correo"] = correo
            if Usuario.objects.filter(correo=correo).exists():
                self.add_error('correo', "Ya existe un usuario con ese correo")
        num_documento = cleaned_data.get("num_documento")
        if num_documento:
            if Usuario.objects.filter(num_documento=num_documento).exists():
                self.add_error('num_documento', "Ya existe un usuario con ese documento")
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Las contraseñas no coinciden")
        
        # Validar que la edad (calculada solo con el año) esté entre 5 y 116 años
        fecha_nacimiento = cleaned_data.get("fecha_nacimiento")
        if fecha_nacimiento:
            from datetime import date
            today = date.today()
            age = today.year - fecha_nacimiento.year  # Se usa solo el año
            if age < 5 or age > 116:
                self.add_error('fecha_nacimiento', "Solo se aceptan personas con edad entre 5 y 116 años en el año actual.")
            
            # Validar el campo 'nivel' si el usuario es adulto (edad >= 22)
            if age >= 22:
                nivel = cleaned_data.get("nivel")
                if not nivel:
                    self.add_error('nivel', "Debes seleccionar tu nivel de juego para adultos")
        return cleaned_data

class CustomLoginForm(forms.Form):
    correo = forms.CharField(label="Correo", max_length=50)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        correo = cleaned_data.get("correo")
        password = cleaned_data.get("password")
        if correo and password:
            correo = correo.lower()
            try:
                user = Usuario.objects.get(correo=correo)
            except Usuario.DoesNotExist:
                raise forms.ValidationError("Credenciales incorrectas")
            if not user.check_password(password):
                raise forms.ValidationError("Credenciales incorrectas")
            cleaned_data["user"] = user
        return cleaned_data
