from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now
from .models import Informe
from usuarios.models import Usuario
from eventos.models import AsistenciaEntrenamiento, Entrenamiento, AsistenciaTorneo
from utils.role_mixins import AdminEntrenadorRequiredMixin, SoloPropioMixin


class InformeListView(AdminEntrenadorRequiredMixin, ListView):
    model = Informe
    template_name = 'informes/informe_list.html'
    context_object_name = 'informes'


class InformeDetailView(SoloPropioMixin, DetailView):
    model = Informe
    template_name = 'informes/informe_detail.html'
    context_object_name = 'informe'


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
        clases = Entrenamiento.objects.filter(
            asistencia_entrenamiento__usuario=u,
            fecha__year=anio,
            fecha__month=mes
        ).distinct().count()

        clases_asistidas = AsistenciaEntrenamiento.objects.filter(
            usuario=u,
            estado="presente",
            entrenamiento__fecha__year=anio,
            entrenamiento__fecha__month=mes
        ).count()

        torneos_asistidos = AsistenciaTorneo.objects.filter(
            usuario=u,
            torneo__fecha__year=anio,
            torneo__fecha__month=mes
        ).count()

        top_torneos = (
            AsistenciaTorneo.objects
            .filter(usuario=u, torneo__fecha__year=anio, torneo__fecha__month=mes)
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
