# eventos/forms.py
from django import forms
from .models import Evento
from usuarios.models import Usuario  # Para configurar el dropdown de entrenadores

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'entrenador',
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
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        if tipo == 'torneo':
            # Para torneos, se eliminan campos que no corresponden:
            if 'entrenador' in self.fields:
                del self.fields['entrenador']
            if 'categoria' in self.fields:
                del self.fields['categoria']
            if 'capacidad' in self.fields:
                del self.fields['capacidad']
            self.fields['costo'].required = True
            self.fields['tipo'].initial = 'torneo'
        else:
            # Para entrenamientos, se elimina el campo costo.
            if 'costo' in self.fields:
                del self.fields['costo']
            self.fields['tipo'].initial = 'entrenamiento'
            # Incluir el dropdown de entrenadores
            if 'entrenador' in self.fields:
                self.fields['entrenador'].queryset = Usuario.objects.filter(rol='entrenador')
                # Si el current_user es entrenador, usarlo como inicial
                if current_user and current_user.rol == 'entrenador':
                    self.fields['entrenador'].initial = current_user
