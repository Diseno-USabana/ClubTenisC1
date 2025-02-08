# eventos/views.py
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Evento, AsistenciaEntrenamiento, AsistenciaTorneo
from .forms import EventoForm  # Debes definir un formulario basado en el modelo Evento
from utils.role_mixins import UsuarioSessionMixin

# Mixin para restringir el acceso a admin y entrenador
class AdminEntrenadorRequiredMixin(UsuarioSessionMixin):
    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        if current_user.rol not in ['admin', 'entrenador']:
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('eventos:list')
        return super().dispatch(request, *args, **kwargs)

# Vista para listar eventos
class EventoListView(ListView):
    model = Evento
    template_name = 'eventos/eventos_list.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        current_user = self.get_current_user(self.request)
        qs = super().get_queryset()
        if current_user and current_user.rol == 'miembro':
            # Mostrar solo eventos tipo entrenamiento de la categoría del usuario
            qs = qs.filter(tipo='entrenamiento', categoria=current_user.id_categoria)
            # Dejar sólo aquellos con cupo disponible
            filtrados = []
            for evento in qs:
                if evento.asistencias_entrenamiento.count() < evento.capacidad:
                    filtrados.append(evento)
            qs = filtrados
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        if current_user:
            # Admin y entrenador pueden crear eventos
            context['can_create'] = current_user.rol in ['admin', 'entrenador']
            if current_user.rol == 'miembro':
                insc_ent = AsistenciaEntrenamiento.objects.filter(usuario=current_user)
                context['user_inscripciones_entrenamiento'] = [ins.entrenamiento.id for ins in insc_ent]
                insc_torneo = AsistenciaTorneo.objects.filter(usuario=current_user)
                context['user_inscripciones_torneo'] = [ins.torneo.id for ins in insc_torneo]
        return context

# Vista para crear un nuevo evento
class EventoCreateView(AdminEntrenadorRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'
    success_url = reverse_lazy('eventos:list')

    def form_valid(self, form):
        current_user = self.get_current_user(self.request)
        form.instance.entrenador = current_user
        return super().form_valid(form)

# Vista para editar un evento existente
class EventoUpdateView(AdminEntrenadorRequiredMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/eventos_edit.html'
    success_url = reverse_lazy('eventos:list')

# Vista para eliminar un evento (se confirmará desde la plantilla de edición)
class EventoDeleteView(AdminEntrenadorRequiredMixin, DeleteView):
    model = Evento
    template_name = 'eventos/eventos_confirm_delete.html'
    success_url = reverse_lazy('eventos:list')
