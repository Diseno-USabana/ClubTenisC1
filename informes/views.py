from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import Informe
from usuarios.models import Usuario
from eventos.models import AsistenciaEntrenamiento, AsistenciaTorneo, Evento
from utils.role_mixins import AdminEntrenadorRequiredMixin, SoloPropioMixin, UsuarioSessionMixin
from django.core.exceptions import PermissionDenied



class InformeListView(AdminEntrenadorRequiredMixin, ListView):
    model = Informe
    template_name = 'informes/informe_list.html'
    context_object_name = 'informes'

    def get_queryset(self):
        qs = Informe.objects.all().order_by('-anio', '-mes')
        anio = self.request.GET.get('anio')
        mes = self.request.GET.get('mes')
        usuario_id = self.request.GET.get('usuario')

        if anio:
            qs = qs.filter(anio=anio)
        if mes:
            qs = qs.filter(mes=mes)
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios'] = Usuario.objects.filter(estado='activo', rol='miembro')
        context['filtros'] = {
            'anio': self.request.GET.get('anio', ''),
            'mes': self.request.GET.get('mes', ''),
            'usuario': self.request.GET.get('usuario', '')
        }
        return context

class InformeDetailAdminView(AdminEntrenadorRequiredMixin, DetailView):
    model = Informe
    template_name = 'informes/informe_detail.html'
    context_object_name = 'informe'


class InformeDetailMiembroView(UsuarioSessionMixin, DetailView):
    model = Informe
    template_name = 'informes/informe_detail.html'
    context_object_name = 'informe'

    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')

        informe = self.get_object()
        if informe.usuario.id != current_user.id:
            raise PermissionDenied("No tienes permiso para ver este informe.")

        return super().dispatch(request, *args, **kwargs)


class InformeCreateView(AdminEntrenadorRequiredMixin, CreateView):
    model = Informe
    fields = [
        'usuario', 'anio', 'mes',
        'clases', 'clases_asistidas', 'torneos_asistidos',
        'asistencia_torneo1', 'asistencia_torneo2', 'asistencia_torneo3'
    ]
    template_name = 'informes/informe_form.html'
    success_url = reverse_lazy('informes:list')


class InformeUpdateView(AdminEntrenadorRequiredMixin, UpdateView):
    model = Informe
    fields = [
        'usuario', 'anio', 'mes',
        'clases', 'clases_asistidas', 'torneos_asistidos',
        'asistencia_torneo1', 'asistencia_torneo2', 'asistencia_torneo3'
    ]
    template_name = 'informes/informe_form.html'
    success_url = reverse_lazy('informes:list')


class InformeDeleteView(AdminEntrenadorRequiredMixin, DeleteView):
    model = Informe
    template_name = 'informes/informe_confirm_delete.html'
    success_url = reverse_lazy('informes:list')


def generar_informe_view(request):
    current_user_id = request.session.get("custom_user_id")
    if not current_user_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect('usuarios:login')

    usuario = Usuario.objects.get(id=current_user_id)
    if usuario.rol not in ['admin', 'entrenador']:
        messages.error(request, "No tienes permiso para generar informes.")
        return redirect('informes:list')

    hoy = now().date()
    anio = hoy.year
    mes = hoy.month

    usuarios = Usuario.objects.filter(estado='activo', rol='miembro')

    for u in usuarios:
        clases = Evento.objects.filter(
            tipo='entrenamiento',
            asistencias_entrenamiento__usuario=u,
            fecha__year=anio,
            fecha__month=mes
        ).distinct().count()

        clases_asistidas = AsistenciaEntrenamiento.objects.filter(
            usuario=u,
            estado="presente",
            entrenamiento__fecha__year=anio,
            entrenamiento__fecha__month=mes,
            entrenamiento__tipo='entrenamiento'
        ).count()

        torneos_asistidos = AsistenciaTorneo.objects.filter(
            usuario=u,
            torneo__fecha__year=anio,
            torneo__fecha__month=mes,
            torneo__tipo='torneo'
        ).count()

        top_torneos = (
            AsistenciaTorneo.objects
            .filter(
                usuario=u,
                torneo__fecha__year=anio,
                torneo__fecha__month=mes,
                torneo__tipo='torneo'
            )
            .order_by('puesto')[:3]
        )

        Informe.objects.update_or_create(
            usuario=u,
            anio=anio,
            mes=mes,
            defaults={
                'clases': clases,
                'clases_asistidas': clases_asistidas,
                'torneos_asistidos': torneos_asistidos,
                'asistencia_torneo1': top_torneos[0] if len(top_torneos) > 0 else None,
                'asistencia_torneo2': top_torneos[1] if len(top_torneos) > 1 else None,
                'asistencia_torneo3': top_torneos[2] if len(top_torneos) > 2 else None,
            }
        )

    messages.success(request, f"Informes generados para {mes}/{anio}.")
    return redirect('informes:list')


class MisInformesListView(UsuarioSessionMixin, ListView):
    model = Informe
    template_name = 'informes/mis_informes.html'
    context_object_name = 'informes'

    def get_queryset(self):
        current_user = self.get_current_user(self.request)
        return Informe.objects.filter(usuario=current_user).order_by('-anio', '-mes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.get_current_user(self.request)
        return context
