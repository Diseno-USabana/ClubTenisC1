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
        fecha_pago = cleaned_data.get('fecha_pago')

        if concepto == 'matricula':
            existe_matricula = Pago.objects.filter(usuario=usuario, concepto='matricula').exists()
            if existe_matricula:
                raise forms.ValidationError("Este usuario ya tiene una matrícula registrada.")

        if concepto == 'mensualidad' and fecha_pago:
            mismo_mes = Pago.objects.filter(
                usuario=usuario,
                concepto='mensualidad',
                fecha_pago__year=fecha_pago.year,
                fecha_pago__month=fecha_pago.month
            ).exists()
            if mismo_mes:
                raise forms.ValidationError("Este usuario ya pagó la mensualidad de ese mes.")
