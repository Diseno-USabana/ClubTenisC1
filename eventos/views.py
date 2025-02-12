from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Evento, AsistenciaEntrenamiento, AsistenciaTorneo, Pago
from .forms import EventoForm
from django.utils import timezone
from datetime import date
from utils.role_mixins import UsuarioSessionMixin

# Función auxiliar para obtener el usuario actual desde la sesión
def get_current_user(request):
    user_id = request.session.get('custom_user_id')
    if not user_id:
        return None
    from usuarios.models import Usuario
    try:
        return Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return None

# Mixin para restringir el acceso a admin y entrenador (para creación/edición/eliminación)
class AdminEntrenadorRequiredMixin(UsuarioSessionMixin):
    def dispatch(self, request, *args, **kwargs):
        current_user = get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        if current_user.rol not in ['admin', 'entrenador']:
            messages.error(request, "No tienes permiso para acceder a esta página.")
            # Redirige a la lista de entrenamientos por defecto (puede ajustarse)
            return redirect('eventos:entrenamientos_list')
        return super().dispatch(request, *args, **kwargs)

# ======================================
# Lista de Entrenamientos
# ======================================
class EntrenamientoListView(ListView):
    model = Evento
    template_name = 'eventos/entrenamientos_list.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        current_user = get_current_user(self.request)
        qs = super().get_queryset()
        filtered_qs = filter_upcoming_events(qs, 'entrenamiento')
        
        if current_user and current_user.rol == 'miembro':
            # Filtrar por la categoría del miembro y asegurar que los eventos a los que está inscrito aparezcan
            filtered_qs = filtered_qs.filter(categoria=current_user.id_categoria)
            inscritos_qs = AsistenciaEntrenamiento.objects.filter(usuario=current_user, entrenamiento__in=filtered_qs)
            inscritos_ids = inscritos_qs.values_list('entrenamiento_id', flat=True)
            filtered_qs = filtered_qs | Evento.objects.filter(id__in=inscritos_ids)
        
        return filtered_qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = get_current_user(self.request)
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
class TorneoListView(ListView):
    model = Evento
    template_name = 'eventos/torneos_list.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        qs = super().get_queryset()
        filtered_qs = filter_upcoming_events(qs, 'torneo')
        return filtered_qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = get_current_user(self.request)
        if current_user:
            context['can_create'] = current_user.rol in ['admin', 'entrenador']
            if current_user.rol == 'miembro':
                insc_torneo = AsistenciaTorneo.objects.filter(usuario=current_user)
                context['user_inscripciones_torneo'] = [ins.torneo.id for ins in insc_torneo]
        return context
# ======================================
# Vistas para Crear/Editar/Eliminar Eventos
# (Se usan para ambos tipos)
# ======================================
class EventoCreateView(AdminEntrenadorRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'
    # Puedes redirigir a la lista de entrenamientos o torneos según convenga.
    def get_success_url(self):
        # Supongamos que el tipo se envía como parámetro GET, por ejemplo ?tipo=torneo
        tipo = self.request.GET.get('tipo', 'entrenamiento')
        if tipo == 'torneo':
            return reverse_lazy('eventos:torneos_list')
        else:
            return reverse_lazy('eventos:entrenamientos_list')

    def form_valid(self, form):
        current_user = get_current_user(self.request)
        form.instance.entrenador = current_user
        return super().form_valid(form)

class EventoUpdateView(AdminEntrenadorRequiredMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'
    success_url = reverse_lazy('eventos:entrenamientos_list')

class EventoDeleteView(AdminEntrenadorRequiredMixin, DeleteView):
    model = Evento
    template_name = 'eventos/eventos_confirm_delete.html'
    success_url = reverse_lazy('eventos:entrenamientos_list')

class EntrenamientoDetailView(DetailView):
    model = Evento
    template_name = 'eventos/entrenamientos_detail.html'
    context_object_name = 'evento'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = get_current_user(self.request)
        context['can_edit'] = False
        context['user_is_member'] = False
        if current_user:
            # Si es admin o entrenador, puede editar
            if current_user.rol in ['admin','entrenador']:
                context['can_edit'] = True
            # Si es miembro, no puede editar, pero marcamos True
            if current_user.rol == 'miembro':
                context['user_is_member'] = True
        return context

class TorneoDetailView(DetailView):
    model = Evento
    template_name = 'eventos/torneos_detail.html'
    context_object_name = 'evento'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = get_current_user(self.request)
        context['can_edit'] = False
        context['user_is_member'] = False
        if current_user:
            # Si es admin o entrenador, puede editar
            if current_user.rol in ['admin','entrenador']:
                context['can_edit'] = True
            # Si es miembro, marcamos True
            if current_user.rol == 'miembro':
                context['user_is_member'] = True
            # Verificar si está inscrito
            asistencia = AsistenciaTorneo.objects.filter(usuario=current_user, torneo=self.object).first()
            context['user_inscrito'] = True if asistencia else False
        return context


# ======================================
# Vistas para Inscripción/Desinscripción
# ======================================

@require_POST
def inscribirse_entrenamiento(request, evento_id):
    current_user = get_current_user(request)
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
    current_user = get_current_user(request)
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
    current_user = get_current_user(request)
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
        usuario=current_user,   # Se asigna el usuario al pago
        monto=evento.costo,
        concepto='torneo',      # Se asigna el concepto correspondiente
        fecha=date.today()      # Se asigna la fecha actual
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
    current_user = get_current_user(request)
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

def filter_upcoming_events(queryset, event_type):
    # Obtener la fecha y hora actuales
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
