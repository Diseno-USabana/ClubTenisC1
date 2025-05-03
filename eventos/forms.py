from django import forms
from .models import Evento
from usuarios.models import Usuario  # Para configurar el dropdown de entrenadores
from datetime import datetime, timedelta, time, date
from dateutil.relativedelta import relativedelta

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
            self.fields['tipo'].widget = forms.HiddenInput()  # Ocultar el campo tipo
        else:
            # Para entrenamientos, se elimina el campo costo y se establece el tipo automáticamente.
            if 'costo' in self.fields:
                del self.fields['costo']
            if 'nombre' in self.fields and not (self.instance and self.instance.id):
                del self.fields['nombre']
            
            self.fields['tipo'].initial = 'entrenamiento'
            self.fields['tipo'].widget = forms.HiddenInput()  # Ocultar el campo tipo
            # Incluir el dropdown de entrenadores
            if 'entrenador' in self.fields:
                self.fields['entrenador'].queryset = Usuario.objects.filter(rol='entrenador')
                # Si el current_user es entrenador, usarlo como inicial
                if current_user and current_user.rol == 'entrenador':
                    self.fields['entrenador'].initial = current_user

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')
        duracion = cleaned_data.get('duracion')
        capacidad = cleaned_data.get('capacidad')
        evento_id = self.instance.id if self.instance and self.instance.id else None

        if not fecha or not hora or not duracion:
            return cleaned_data  # Campos incompletos, ya los marcará el form

        today = date.today()
        new_start = datetime.combine(fecha, hora)
        new_end = new_start + timedelta(minutes=duracion)

        # 1. Validaciones por tipo
        if tipo == 'entrenamiento':
            if fecha < today:
                self.add_error('fecha', 'No se pueden crear entrenamientos en el pasado.')
            elif fecha > today + relativedelta(months=+6):
                self.add_error('fecha', 'No se pueden crear entrenamientos con más de 6 meses de antelación.')
            # Horario prohibido: 12:00 AM a 6:00 AM
            if hora < time(6, 0):
                self.add_error('hora', 'No se pueden programar entrenamientos antes de las 6:00 AM.')
        elif tipo == 'torneo':
            if fecha < today - timedelta(days=7):
                self.add_error('fecha', 'No se pueden crear torneos de más de una semana atrás.')
            elif fecha > today + relativedelta(years=+1):
                self.add_error('fecha', 'No se pueden crear torneos con más de un año de antelación.')
            if hora < time(6, 0) or hora >= time(22, 0):
                self.add_error('hora', 'Los torneos deben realizarse entre 6:00 AM y 10:00 PM.')

        # 2. Validar solapamientos
        overlapping_events = Evento.objects.filter(fecha=fecha).exclude(id=evento_id)
        if tipo == 'torneo':
            for evt in overlapping_events:
                evt_start = datetime.combine(evt.fecha, evt.hora)
                evt_end = evt_start + timedelta(minutes=evt.duracion)
                if new_start < evt_end and new_end > evt_start:
                    raise forms.ValidationError("Existe un evento que se cruza en ese horario; no se puede crear el torneo.")
        else:
            overlapping = []
            for evt in overlapping_events.filter(tipo='entrenamiento'):
                evt_start = datetime.combine(evt.fecha, evt.hora)
                evt_end = evt_start + timedelta(minutes=evt.duracion)
                if new_start < evt_end and new_end > evt_start:
                    overlapping.append(evt)

            if len(overlapping) >= 2:
                raise forms.ValidationError("Ya se han reservado las dos canchas en ese horario.")
            if len(overlapping) == 0 and capacidad and capacidad > 12:
                self.add_error('capacidad', "La capacidad sin solapamiento no puede exceder 12 (dos canchas).")
            elif len(overlapping) == 1 and capacidad and capacidad > 6:
                self.add_error('capacidad', "La capacidad con una sola cancha no puede exceder 6.")

        return cleaned_data
