from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['usuario', 'concepto', 'fecha', 'monto', 'anio', 'mes']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        usuario = cleaned_data.get('usuario')
        concepto = cleaned_data.get('concepto')
        anio = cleaned_data.get('anio')
        mes = cleaned_data.get('mes')

        if not usuario or not concepto:
            return cleaned_data  # evitar errores si faltan datos básicos

        # ✅ Validación de matrícula única
        if concepto == 'matricula':
            existe_matricula = Pago.objects.filter(usuario=usuario, concepto='matricula').exists()
            if existe_matricula:
                raise forms.ValidationError("Este usuario ya tiene una matrícula registrada.")

        # ✅ Validación de mensualidad por mes y año
        if concepto == 'mensualidad' and anio and mes:
            mismo_mes = Pago.objects.filter(
                usuario=usuario,
                concepto='mensualidad',
                anio=anio,
                mes=mes
            ).exists()
            if mismo_mes:
                raise forms.ValidationError(f"Este usuario ya pagó la mensualidad de {mes}/{anio}.")

        return cleaned_data
