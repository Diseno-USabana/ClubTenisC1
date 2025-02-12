# eventos/forms.py
from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
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
    
    def __init__(self, *args, **kwargs):
        tipo = kwargs.pop('tipo', None)  # Se pasa desde la vista
        super().__init__(*args, **kwargs)
        if tipo == 'torneo':
            # Para torneos, se eliminan campos que no corresponden:
            if 'categoria' in self.fields:
                del self.fields['categoria']
            if 'capacidad' in self.fields:
                del self.fields['capacidad']
            # Dejar costo como obligatorio y forzar tipo:
            self.fields['costo'].required = True
            self.fields['tipo'].initial = 'torneo'
            # Opcional: si se quiere evitar que el usuario modifique el tipo, se puede marcar como disabled o hidden.
        else:
            # Para entrenamientos, se elimina el campo costo:
            if 'costo' in self.fields:
                del self.fields['costo']
            self.fields['tipo'].initial = 'entrenamiento'
