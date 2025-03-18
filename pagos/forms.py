# pagos/forms.py
from django import forms
from .models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['usuario', 'concepto', 'fecha', 'cantidad']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
