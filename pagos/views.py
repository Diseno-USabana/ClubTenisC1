from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Pago
from .forms import PagoForm
from usuarios.models import Usuario



class PagoListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        return Pago.objects.all().order_by('-fecha')

class PagoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:list')

class PagoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:list')

class PagoDetailView(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'pagos/pago_detail.html'
    context_object_name = 'pago'

class PagoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pagos:list')



@login_required
def registrar_mensualidad(request):
    user = request.user
    try:
        usuario = Usuario.objects.get(id=user.id)  # Convertir correctamente
    except Usuario.DoesNotExist:
        messages.error(request, "No se encontró tu cuenta como usuario válido.")
        return redirect('pagos:list')

    hoy = now().date()
    mes = hoy.month
    anio = hoy.year

    ya_pagado = Pago.objects.filter(usuario=usuario, concepto="mensualidad", anio=anio, mes=mes).exists()
    if ya_pagado:
        messages.warning(request, "Ya has registrado tu mensualidad de este mes.")
        return redirect('pagos:list')

    Pago.objects.create(
        usuario=usuario,
        concepto="mensualidad",
        fecha=hoy,
        monto=170000,
        anio=anio,
        mes=mes
    )

    messages.success(request, "¡Mensualidad registrada exitosamente!")
    return redirect('pagos:list')
