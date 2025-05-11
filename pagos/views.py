from django.views.generic import ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.role_mixins import AdminRequiredForListMixin, SoloPropioMixin
from .models import Pago
from .forms import PagoForm
from usuarios.models import Usuario

# Vista: lista de todos los pagos (solo admin)
class PagoListView(AdminRequiredForListMixin, ListView):
    model = Pago
    template_name = 'pagos/pago_list.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        return Pago.objects.all().order_by('-fecha')

# Vista: lista de pagos del propio usuario (miembro)
class PagoListUsuarioView(SoloPropioMixin, ListView):
    model = Pago
    template_name = 'pagos/pago_list_usuario.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        current_user = self.get_current_user(self.request)
        return Pago.objects.filter(usuario=current_user).order_by('-fecha')

# Vista: actualizar un pago existente
class PagoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form.html'
    success_url = reverse_lazy('pagos:list')

# Vista: detalle de un pago
class PagoDetailView(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'pagos/pago_detail.html'
    context_object_name = 'pago'

# Vista: eliminar un pago
class PagoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pagos:list')

# Vista: registrar automáticamente la mensualidad del mes
@login_required
def registrar_mensualidad(request):
    user = request.user
    try:
        usuario = Usuario.objects.get(id=user.id)
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

# Vista: crear pago desde formulario (rol-aware)
@login_required
def vista_crear_pago(request):
    if request.user.is_staff:
        if request.method == "POST":
            form = PagoForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Pago creado correctamente.")
                return redirect('pagos:list')
        else:
            form = PagoForm()
        return render(request, "pagos/pago_form_admin.html", {"form": form})
    else:
        return render(request, "pagos/pago_form.html")
