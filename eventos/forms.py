# eventos/forms.py
from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        # No incluimos 'entrenador' porque se asigna automáticamente desde la sesión en la vista.
        fields = [
            'categoria',
            'nombre',
            'fecha',
            'hora',
            'capacidad',
            'duracion',
            'tipo',
            'costo',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
        }
