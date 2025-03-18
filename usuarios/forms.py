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
            'matricula',
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("rol")
        
        # Los campos comunes para todos los roles:
        correo = cleaned_data.get("correo")
        password = cleaned_data.get("password")
        nombre = cleaned_data.get("nombre")
        apellidos = cleaned_data.get("apellidos")
        estado = cleaned_data.get("estado")
        
        if not rol:
            self.add_error("rol", "El rol es obligatorio.")
        if not nombre:
            self.add_error("nombre", "El nombre es obligatorio.")
        if not apellidos:
            self.add_error("apellidos", "Los apellidos son obligatorios.")
        if not correo:
            self.add_error("correo", "El correo es obligatorio.")
        if not password:
            self.add_error("password", "La contraseña es obligatoria.")
        if not estado:
            self.add_error("estado", "El estado es obligatorio.")

        # Validar por rol:
        if rol == 'admin':
            # Solo se requieren los campos básicos (ya validados arriba)
            pass
        elif rol == 'entrenador':
            # Se requieren: telefono, tipo_documento, num_documento
            if not cleaned_data.get("telefono"):
                self.add_error("telefono", "El teléfono es obligatorio para entrenadores.")
            if not cleaned_data.get("tipo_documento"):
                self.add_error("tipo_documento", "El tipo de documento es obligatorio para entrenadores.")
            if not cleaned_data.get("num_documento"):
                self.add_error("num_documento", "El número de documento es obligatorio para entrenadores.")
        elif rol == 'miembro':
            # Se requieren: telefono, tipo_documento, num_documento, fecha_nacimiento, id_categoria, matricula
            if not cleaned_data.get("telefono"):
                self.add_error("telefono", "El teléfono es obligatorio para miembros.")
            if not cleaned_data.get("tipo_documento"):
                self.add_error("tipo_documento", "El tipo de documento es obligatorio para miembros.")
            if not cleaned_data.get("num_documento"):
                self.add_error("num_documento", "El número de documento es obligatorio para miembros.")
            if not cleaned_data.get("fecha_nacimiento"):
                self.add_error("fecha_nacimiento", "La fecha de nacimiento es obligatoria para miembros.")
            # id_categoria se asigna automáticamente según la edad en la vista, así que se ignora aquí.
            # matricula es un campo booleano; se puede dejar como False por defecto.
        return cleaned_data


class RegistrationForm(forms.ModelForm):
    # Este formulario se usa para registro desde el front, se mantiene igual.
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Verificar contraseña")
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
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Conversión y validaciones comunes (como se hizo antes)
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

