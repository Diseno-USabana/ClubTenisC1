from django import forms
from .models import Pago
from datetime import date

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['usuario', 'concepto', 'fecha', 'monto', 'anio', 'mes']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        concepto = cleaned_data.get('concepto')
        anio = cleaned_data.get('anio')
        mes = cleaned_data.get('mes')

        if concepto == "mensualidad" and (not anio or not mes):
            raise forms.ValidationError("Debe especificar mes y año para mensualidad.")
        if concepto != "mensualidad" and (anio or mes):
            raise forms.ValidationError("Mes y año solo aplican a mensualidades.")
