from django import forms
from .models import Usuario
from datetime import date

class UsuarioForm(forms.ModelForm):
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
            'nivel',  # campo extra
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'password': forms.PasswordInput(),
        }
    
    def __init__(self, *args, **kwargs):
        self.modo = kwargs.pop('modo', None)       # "register" o "create" o "update"
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # ——————————————————————————————————————————
        # Paso 1: lógica para register 
        if self.modo == "register":
            self.fields["password_confirm"] = forms.CharField(
                widget=forms.PasswordInput(),
                label="Confirmar contraseña",
                required=True
            )
            self.fields["rol"].initial = "miembro"
            self.fields["estado"].initial = "activo"
            self.fields["rol"].widget = forms.HiddenInput()
            self.fields["estado"].widget = forms.HiddenInput()
            self.fields["rol"].required = False
            self.fields["estado"].required = False
        # ——————————————————————————————————————————
        # EDICIÓN: restringir campos según rol
        elif self.modo == "update" and self.current_user and self.instance:
            is_admin = self.current_user.rol == 'admin'
            editing_self = self.instance.id == self.current_user.id
            if not is_admin and editing_self:
                campos_protegidos = [
                    "rol", "estado", "nombre", "apellidos", "tipo_documento", "num_documento",
                    "fecha_nacimiento", "matricula", "id_categoria", "nivel"
                ]
                for campo in campos_protegidos:
                    if campo in self.fields:
                        self.fields[campo].widget.attrs["disabled"] = "disabled"
                        self.fields[campo].widget.attrs["style"] = "pointer-events: none; border: none; background: none;"
                        # ← insertamos esta línea:
                        self.fields[campo].required = False


                # Mostrar el valor actual de nivel para adultos
                if self.instance.rol == "miembro" and self.instance.fecha_nacimiento:
                    edad = date.today().year - self.instance.fecha_nacimiento.year
                    if edad > 21 and self.instance.id_categoria:
                        self.initial["nivel"] = self.instance.id_categoria.nombre  # No es 'nivel', es 'id_categoria'
                                    

        # ——————————————————————————————————————————

        # Paso 2: si es POST, determinar rol y eliminar campos irrelevantes
        if self.data.get('rol'):
            role = self.data.get('rol')
            # Campos que siempre deben permanecer
            allowed = ['rol', 'nombre', 'apellidos', 'correo', 'password', 'estado']
            if role == 'entrenador':
                allowed += ['telefono', 'tipo_documento', 'num_documento']
            elif role == 'miembro':
                allowed += ['telefono', 'tipo_documento', 'num_documento',
                            'fecha_nacimiento', 'matricula', 'nivel']
            # Remover del form todo lo que no esté en allowed
            for field_name in list(self.fields.keys()):
                if field_name not in allowed:
                    self.fields.pop(field_name)


    
    def clean(self):
        cleaned_data = super().clean()

        # Si estamos en modo edición y el usuario se edita a sí mismo (no admin),
        if self.modo == "update" and self.instance and self.current_user:
            is_admin = self.current_user.rol == 'admin'
            editing_self = self.instance.id == self.current_user.id
            if editing_self and not is_admin:
                # 1) Restaura TODOS los campos protegidos
                protegidos = [
                    'rol','nombre','apellidos','estado',
                    'tipo_documento','num_documento',
                    'fecha_nacimiento','id_categoria','matricula'
                ]
                for field in protegidos:
                    cleaned_data[field] = getattr(self.instance, field)

                # 2) Validar solo lo que sí puede cambiar
                if not cleaned_data.get('correo'):
                    self.add_error('correo', 'El correo es obligatorio.')
                if not cleaned_data.get('telefono'):
                    self.add_error('telefono', 'El teléfono es obligatorio.')
                # La contraseña es opcional: la cambiará solo si rellena algo

                # 3) Devolver YA, sin más validaciones
                print("DEBUG ✅ cleaned_data en update:", cleaned_data)
                return cleaned_data


        # ===========================
        # Flujo normal para register/create
        # ===========================
        if self.modo == "register":
            cleaned_data["rol"] = "miembro"
            cleaned_data["estado"] = "activo"
            print("DEBUG: Entro a modo register")

        rol = cleaned_data.get("rol")
        nombre = cleaned_data.get("nombre")
        apellidos = cleaned_data.get("apellidos")
        correo = cleaned_data.get("correo")
        password = cleaned_data.get("password")
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

        if self.modo == "register":
            password_confirm = cleaned_data.get("password_confirm")
            if password and password_confirm and password != password_confirm:
                self.add_error("password_confirm", "Las contraseñas no coinciden.")

        # Validaciones específicas por rol
        if rol == 'admin':
            pass
        elif rol == 'entrenador':
            if not cleaned_data.get("telefono"):
                self.add_error("telefono", "El teléfono es obligatorio para entrenadores.")
            if not cleaned_data.get("tipo_documento"):
                self.add_error("tipo_documento", "El tipo de documento es obligatorio para entrenadores.")
            if not cleaned_data.get("num_documento"):
                self.add_error("num_documento", "El número de documento es obligatorio para entrenadores.")
        elif rol == 'miembro':
            if not cleaned_data.get("telefono"):
                self.add_error("telefono", "El teléfono es obligatorio para miembros.")
            if not cleaned_data.get("tipo_documento"):
                self.add_error("tipo_documento", "El tipo de documento es obligatorio para miembros.")
            if not cleaned_data.get("num_documento"):
                self.add_error("num_documento", "El número de documento es obligatorio para miembros.")
            if not cleaned_data.get("fecha_nacimiento"):
                self.add_error("fecha_nacimiento", "La fecha de nacimiento es obligatoria para miembros.")
            else:
                from datetime import date
                today = date.today()
                age = today.year - cleaned_data["fecha_nacimiento"].year
                if age >= 22 and not cleaned_data.get("nivel"):
                    self.add_error("nivel", "Debes seleccionar el nivel de juego para adultos.")
        else:
            self.add_error("rol", "Rol no válido o no reconocido.")

        # Restaurar valores protegidos si no vienen en POST (modo update)
        if self.modo == "update" and self.instance and self.current_user:
            is_admin = self.current_user.rol == 'admin'
            editing_self = self.instance.id == self.current_user.id

            if not is_admin and editing_self:
                for field in ["rol", "estado", "nombre", "apellidos", "tipo_documento", "num_documento", "fecha_nacimiento", "matricula", "id_categoria"]:
                    if field in self.fields and field not in self.data:
                        cleaned_data[field] = getattr(self.instance, field)
                if "nivel" not in self.data and "id_categoria" in self.fields:
                    cleaned_data["id_categoria"] = self.instance.id_categoria

        print("DEBUG ✅ cleaned_data final:", cleaned_data)
        print("DEBUG ✅ instance pre-save:", self.instance)
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

