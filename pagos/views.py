# pagos/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Pago

class PagoListView(ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

class PagoDetailView(DetailView):
    model = Pago
    template_name = 'pagos/pago_detail.html'
    context_object_name = 'pago'

class PagoCreateView(CreateView):
    model = Pago
    fields = ['estado', 'concepto', 'fecha', 'monto']
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:list')

class PagoUpdateView(UpdateView):
    model = Pago
    fields = ['estado', 'concepto', 'fecha', 'monto']
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:list')

class PagoDeleteView(DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pagos:list')
