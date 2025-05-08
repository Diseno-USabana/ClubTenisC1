from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Evento, AsistenciaEntrenamiento, AsistenciaTorneo, Pago
from .forms import EventoForm
from django.utils import timezone
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from utils.role_mixins import AdminEntrenadorRequiredMixin, UsuarioSessionMixin
from django.db import models

# ======================================
# Lista de Entrenamientos
# ======================================
class EntrenamientoListView(UsuarioSessionMixin, ListView):
    model = Evento
    template_name = 'eventos/entrenamientos_list.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        current_user = self.get_current_user(self.request)
        qs = super().get_queryset()
        filtered_qs = filter_upcoming_events(qs, 'entrenamiento')

        if current_user and current_user.rol == 'miembro':
            # Solo eventos que coincidan con su categoría
            filtered_qs = filtered_qs.filter(categoria=current_user.id_categoria)
            # Anotar cantidad de asistentes y filtrar por capacidad
            filtered_qs = filtered_qs.annotate(num_asistentes=models.Count('asistencias_entrenamiento')).filter(num_asistentes__lt=models.F('capacidad'))
            # Incluir también los eventos en los que ya está inscrito, incluso si están llenos
            inscritos_qs = AsistenciaEntrenamiento.objects.filter(usuario=current_user, entrenamiento__in=qs)
            inscritos_ids = inscritos_qs.values_list('entrenamiento_id', flat=True)
            filtered_qs = filtered_qs | Evento.objects.filter(id__in=inscritos_ids)

        return filtered_qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        if current_user:
            context['can_create'] = current_user.rol in ['admin', 'entrenador']
            context['current_role'] = current_user.rol  
            if current_user.rol == 'miembro':
                insc_ent = AsistenciaEntrenamiento.objects.filter(usuario=current_user)
                context['user_inscripciones_entrenamiento'] = [ins.entrenamiento.id for ins in insc_ent]
        return context

# ======================================
# Lista de Torneos
# ======================================
class TorneoListView(UsuarioSessionMixin, ListView):
    model = Evento
    template_name = 'eventos/torneos_list.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        qs = super().get_queryset()
        filtered_qs = filter_upcoming_events(qs, 'torneo')
        return filtered_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        if current_user:
            context['can_create'] = current_user.rol in ['admin', 'entrenador']
            if current_user.rol == 'miembro':
                insc_torneo = AsistenciaTorneo.objects.filter(usuario=current_user)
                context['user_inscripciones_torneo'] = [ins.torneo.id for ins in insc_torneo]
        return context

# ======================================
# Vistas para Crear/Editar/Eliminar Eventos
# ======================================
class EventoCreateView(AdminEntrenadorRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pasar "tipo" desde la query string (default: "entrenamiento")
        kwargs['tipo'] = self.request.GET.get('tipo', 'entrenamiento')
        # Pasar current_user para configurar el dropdown de entrenadores en el formulario (para entrenamientos)
        kwargs['current_user'] = self.get_current_user(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.request.GET.get('tipo', 'entrenamiento')
        return context

    def form_valid(self, form):
        tipo = self.request.GET.get('tipo', form.instance.tipo)
        form.instance.tipo = tipo
        if tipo == 'torneo':
            form.instance.entrenador = None
            form.instance.categoria = None
            form.instance.capacidad = 999
        else:
            form.instance.costo = None

        # Generar nombre predeterminado solo si no hay
        if tipo == 'entrenamiento' and not form.instance.nombre:
            cat_name = str(form.instance.categoria) if form.instance.categoria else "Sin categoría"
            fecha_str = form.cleaned_data['fecha'].strftime("%d %b.").lstrip("0")
            hora_str = form.cleaned_data['hora'].strftime("%I:%M %p").lstrip("0").upper()
            form.instance.nombre = f"{cat_name} - {fecha_str} {hora_str}"

        return super().form_valid(form)


    def get_success_url(self):
        tipo = self.request.GET.get('tipo', 'entrenamiento')
        if tipo == 'torneo':
            return reverse_lazy('eventos:torneos_list')
        else:
            return reverse_lazy('eventos:entrenamientos_list')

class EventoUpdateView(AdminEntrenadorRequiredMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'
    success_url = reverse_lazy('eventos:entrenamientos_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Para edición, pasar "tipo" desde la query string o usar el valor actual del objeto
        kwargs['tipo'] = self.request.GET.get('tipo', self.object.tipo)
        kwargs['current_user'] = self.get_current_user(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo'] = self.request.GET.get('tipo', self.object.tipo)
        return context

    def form_valid(self, form):
        tipo = self.request.GET.get('tipo', form.instance.tipo)
        form.instance.tipo = tipo
        if tipo == 'torneo':
            form.instance.entrenador = None
            form.instance.categoria = None
            form.instance.capacidad = 999
        else:
            form.instance.costo = None

        # Generar nombre predeterminado solo si no hay
        if tipo == 'entrenamiento' and not form.instance.nombre:
            cat_name = str(form.instance.categoria) if form.instance.categoria else "Sin categoría"
            fecha_str = form.cleaned_data['fecha'].strftime("%d %b.").lstrip("0")
            hora_str = form.cleaned_data['hora'].strftime("%I:%M %p").lstrip("0").upper()
            form.instance.nombre = f"{cat_name} - {fecha_str} {hora_str}"

        return super().form_valid(form)


class EventoDeleteView(AdminEntrenadorRequiredMixin, DeleteView):
    model = Evento
    template_name = 'eventos/eventos_confirm_delete.html'
    success_url = reverse_lazy('eventos:entrenamientos_list')

class EntrenamientoDetailView(UsuarioSessionMixin, DetailView):
    model = Evento
    template_name = 'eventos/entrenamientos_detail.html'
    context_object_name = 'evento'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        context['can_edit'] = current_user and current_user.rol in ['admin','entrenador']
        context['user_is_member'] = current_user and current_user.rol == 'miembro'
        return context

class TorneoDetailView(UsuarioSessionMixin, DetailView):
    model = Evento
    template_name = 'eventos/torneos_detail.html'
    context_object_name = 'evento'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        context['can_edit'] = current_user and current_user.rol in ['admin','entrenador']
        context['user_is_member'] = current_user and current_user.rol == 'miembro'
        asistencia = None
        if current_user:
            asistencia = AsistenciaTorneo.objects.filter(usuario=current_user, torneo=self.object).first()
        context['user_inscrito'] = True if asistencia else False
        return context

# ======================================
# Inscripción/Desinscripción
# ======================================
@require_POST
def inscribirse_entrenamiento(request, evento_id):
    current_user = UsuarioSessionMixin().get_current_user(request)
    if not current_user:
        messages.error(request, "Debes estar logueado para inscribirte.")
        return redirect('usuarios:login')
    if current_user.rol != 'miembro':
        messages.error(request, "Solo los miembros pueden inscribirse a entrenamientos.")
        return redirect('eventos:entrenamientos_list')
    evento = get_object_or_404(Evento, id=evento_id, tipo='entrenamiento')
    if evento.categoria != current_user.id_categoria:
        messages.error(request, "Este entrenamiento no corresponde a tu categoría.")
        return redirect('eventos:entrenamientos_list')
    if evento.asistencias_entrenamiento.count() >= evento.capacidad:
        messages.error(request, "El entrenamiento no tiene cupo disponible.")
        return redirect('eventos:entrenamientos_list')
    if AsistenciaEntrenamiento.objects.filter(usuario=current_user, entrenamiento=evento).exists():
        messages.info(request, "Ya estás inscrito en este entrenamiento.")
        return redirect('eventos:entrenamientos_list')
    AsistenciaEntrenamiento.objects.create(
        usuario=current_user,
        entrenamiento=evento,
        estado='presente'
    )
    messages.success(request, "Inscripción exitosa en el entrenamiento.")
    return redirect('eventos:entrenamientos_list')

@require_POST
def desinscribirse_entrenamiento(request, evento_id):
    current_user = UsuarioSessionMixin().get_current_user(request)
    if not current_user:
        messages.error(request, "Debes estar logueado para desinscribirte.")
        return redirect('usuarios:login')
    if current_user.rol != 'miembro':
        messages.error(request, "Solo los miembros pueden desinscribirse de entrenamientos.")
        return redirect('eventos:entrenamientos_list')
    evento = get_object_or_404(Evento, id=evento_id, tipo='entrenamiento')
    asistencia = AsistenciaEntrenamiento.objects.filter(usuario=current_user, entrenamiento=evento).first()
    if asistencia:
        asistencia.delete()
        messages.success(request, "Te has desinscrito del entrenamiento.")
    else:
        messages.info(request, "No estabas inscrito en este entrenamiento.")
    return redirect('eventos:entrenamientos_list')

@require_POST
def inscribirse_torneo(request, evento_id):
    current_user = UsuarioSessionMixin().get_current_user(request)
    if not current_user:
        messages.error(request, "Debes estar logueado para inscribirte.")
        return redirect('usuarios:login')
    if current_user.rol != 'miembro':
        messages.error(request, "Solo los miembros pueden inscribirse a torneos.")
        return redirect('eventos:torneos_list')
    evento = get_object_or_404(Evento, id=evento_id, tipo='torneo')
    if AsistenciaTorneo.objects.filter(usuario=current_user, torneo=evento).exists():
        messages.info(request, "Ya estás inscrito en este torneo.")
        return redirect('eventos:torneos_list')

    pago = Pago.objects.create(
        usuario=current_user,
        monto=evento.costo,
        concepto='torneo',
        fecha=date.today()
    )
    
    AsistenciaTorneo.objects.create(
        usuario=current_user,
        torneo=evento,
        categoria=current_user.id_categoria,
        pago=pago,
        puesto=0
    )
    messages.success(request, "Inscripción exitosa en el torneo. Pago registrado.")
    return redirect('eventos:torneos_list')

@require_POST
def desinscribirse_torneo(request, evento_id):
    current_user = UsuarioSessionMixin().get_current_user(request)
    if not current_user:
        messages.error(request, "Debes estar logueado para desinscribirte.")
        return redirect('usuarios:login')
    if current_user.rol != 'miembro':
        messages.error(request, "Solo los miembros pueden desinscribirse de torneos.")
        return redirect('eventos:torneos_list')
    evento = get_object_or_404(Evento, id=evento_id, tipo='torneo')
    asistencia = AsistenciaTorneo.objects.filter(usuario=current_user, torneo=evento).first()
    if asistencia:
        asistencia.delete()
        messages.success(request, "Inscripción cancelada en el torneo. El pago no fue reembolsado.")
    else:
        messages.info(request, "No estabas inscrito en este torneo.")
    return redirect('eventos:torneos_list')

from datetime import datetime, time, timedelta

def check_event_time_restrictions(form, new_start, new_end, tipo, event_date):
    # Restricción horaria según el tipo de evento
    if tipo == 'entrenamiento':
        forbidden_start = datetime.combine(event_date, time(0, 0)) + timedelta(days=1)
        forbidden_end = datetime.combine(event_date, time(6, 0))
    else:  # Suponiendo que el otro tipo es 'torneo'
        forbidden_start = datetime.combine(event_date, time(22, 0))
        forbidden_end = datetime.combine(event_date, time(6, 0))

    print(f"forbidden_start: {forbidden_start}")
    print(f"forbidden_end: {forbidden_end}")
    print(f"new_start: {new_start}")
    print(f"new_end: {new_end}")

    # Comprobar si el evento comienza antes del fin del período prohibido o termina después del inicio del período prohibido
    if new_start < forbidden_end or new_end > forbidden_start:
        if tipo == 'entrenamiento':
            form.add_error('hora', 'No se pueden crear entrenamientos que se solapen con el horario de 12:00 AM a 06:00 AM.')
        else:
            form.add_error('hora', 'No se pueden crear torneos que se solapen con el horario de 10:00 PM a 06:00 AM.')
        return form.is_valid()

    return True


from datetime import datetime, timedelta

def check_event_overlap(form, new_start, new_end, tipo, event_id):
    overlapping_events = Evento.objects.filter(fecha=form.cleaned_data['fecha']).exclude(id=event_id)
    
    if tipo == 'torneo':
        # Torneos no permiten solapamientos de ningún tipo
        for evt in overlapping_events:
            evt_start = datetime.combine(evt.fecha, evt.hora)
            evt_end = evt_start + timedelta(minutes=evt.duracion)
            if new_start < evt_end and new_end > evt_start:
                form.add_error(None, "Existe un evento que se cruza en ese horario; no se puede crear el torneo.")
                return False
    else:
        # Entrenamientos: validar solapamientos según capacidad por cancha
        overlapping = []
        for evt in overlapping_events.filter(tipo='entrenamiento'):
            evt_start = datetime.combine(evt.fecha, evt.hora)
            evt_end = evt_start + timedelta(minutes=evt.duracion)
            if new_start < evt_end and new_end > evt_start:
                overlapping.append(evt)

        new_capacity = form.cleaned_data.get('capacidad', 0)

        if len(overlapping) >= 2:
            form.add_error(None, "Ya se han reservado las dos canchas en ese horario.")
            return False

        if len(overlapping) == 0:
            if new_capacity > 12:
                form.add_error('capacidad', "La capacidad para un entrenamiento sin solapamiento no puede exceder 12 (dos canchas).")
                return False

        elif len(overlapping) == 1:
            other_event = overlapping[0]
            if other_event.capacidad > 6:
                form.add_error(None, f"El evento existente ya ocupa más de una cancha (capacidad {other_event.capacidad}).")
                return False
            if new_capacity > 6:
                form.add_error('capacidad', "La capacidad para un entrenamiento solapado no puede exceder 6 (una cancha).")
                return False

    return True

def filter_upcoming_events(queryset, event_type):
    now = timezone.now()
    upcoming_events = queryset.filter(
        tipo=event_type,
        fecha__gt=now.date()
    ) | queryset.filter(
        tipo=event_type,
        fecha=now.date(),
        hora__gte=now.time()
    )
    return upcoming_events

