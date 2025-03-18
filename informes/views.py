# informes/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Informe

class InformeListView(ListView):
    model = Informe
    template_name = 'informes/informe_list.html'
    context_object_name = 'informes'

class InformeDetailView(DetailView):
    model = Informe
    template_name = 'informes/informe_detail.html'
    context_object_name = 'informe'

class InformeCreateView(CreateView):
    model = Informe
    fields = [
        'usuario', 'anio', 'mes', 
        'clases', 'clases_asistidas', 'torneos_asistidos',
        'asistencia_torneo1', 'asistencia_torneo2', 'asistencia_torneo3'
    ]
    template_name = 'informes/informe_form.html'
    success_url = reverse_lazy('informes:list')

class InformeUpdateView(UpdateView):
    model = Informe
    fields = [
        'usuario', 'anio', 'mes', 
        'clases', 'clases_asistidas', 'torneos_asistidos',
        'asistencia_torneo1', 'asistencia_torneo2', 'asistencia_torneo3'
    ]
    template_name = 'informes/informe_form.html'
    success_url = reverse_lazy('informes:list')

class InformeDeleteView(DeleteView):
    model = Informe
    template_name = 'informes/informe_confirm_delete.html'
    success_url = reverse_lazy('informes:list')
