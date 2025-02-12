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
        tipo = kwargs.pop('tipo', None)  # Se puede pasar desde la vista
        super().__init__(*args, **kwargs)
        if tipo == 'torneo':
            # Para torneos, ocultar campos que no se usan: categoría y capacidad; se fijan por defecto
            if 'categoria' in self.fields:
                del self.fields['categoria']
            if 'capacidad' in self.fields:
                del self.fields['capacidad']
            # Además, se puede quitar entrenador (si estuviera en el formulario) y forzar tipo
            self.fields['costo'].required = True
            self.fields['tipo'].initial = 'torneo'
        else:
            # Para entrenamientos, se quita el campo costo y se fija tipo
            if 'costo' in self.fields:
                del self.fields['costo']
            self.fields['tipo'].initial = 'entrenamiento'
