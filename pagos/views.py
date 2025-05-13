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
from utils.role_mixins import UsuarioSessionMixin

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
class PagoUpdateView(SoloPropioMixin, UpdateView):
    model = Pago
    form_class = PagoForm
    template_name = 'pagos/pago_form_admin.html'
    success_url = reverse_lazy('pagos:list')

# Vista: detalle de un pago (solo lectura, no necesita form)
class PagoDetailView(SoloPropioMixin, DetailView):
    model = Pago
    template_name = 'pagos/pago_detail.html'
    context_object_name = 'pago'

# Vista: eliminar un pago (no necesita fields si no usa form)
class PagoDeleteView(SoloPropioMixin, DeleteView):
    model = Pago
    template_name = 'pagos/pago_confirm_delete.html'
    success_url = reverse_lazy('pagos:list')


# Vista: registrar automáticamente la mensualidad del mes
def registrar_mensualidad(request):
    usuario = UsuarioSessionMixin().get_current_user(request)

    if not usuario:
        messages.error(request, "Debes iniciar sesión para registrar tu mensualidad.")
        return redirect('usuarios:login')

    hoy = now().date()
    mes = hoy.month
    anio = hoy.year

    ya_pagado = Pago.objects.filter(usuario=usuario, concepto="mensualidad", anio=anio, mes=mes).exists()
    if ya_pagado:
        messages.warning(request, "Ya has registrado tu mensualidad de este mes.")
        return redirect('pagos:mis_pagos', usuario_id=usuario.id)

    Pago.objects.create(
        usuario=usuario,
        concepto="mensualidad",
        fecha=hoy,
        monto=170000,
        anio=anio,
        mes=mes
    )

    messages.success(request, "¡Mensualidad registrada exitosamente!")
    return redirect('pagos:mis_pagos', usuario_id=usuario.id)


# Vista: crear pago desde formulario (rol-aware)

def vista_crear_pago(request):
    usuario = UsuarioSessionMixin().get_current_user(request)

    if not usuario:
        messages.error(request, "Debes iniciar sesión para registrar un pago.")
        return redirect('usuarios:login')

    es_admin = usuario.rol == 'admin'

    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)

            # 1) Asignar usuario si no es admin
            if not es_admin:
                pago.usuario = usuario

            # 2) Año/mes: preferir valores del formulario si vienen
            if pago.concepto == "mensualidad":
                anio_form = form.cleaned_data.get('anio')
                mes_form = form.cleaned_data.get('mes')
                if anio_form and mes_form:
                    pago.anio = anio_form
                    pago.mes = mes_form
                else:
                    pago.anio = pago.fecha.year
                    pago.mes = pago.fecha.month
            else:
                pago.anio = None
                pago.mes = None

            pago.save()
            messages.success(request, "Pago creado correctamente.")
            if es_admin:
                return redirect('pagos:list')
            else:
                return redirect('pagos:mis_pagos', usuario_id=usuario.id)

    else:
        form = PagoForm()

    template = "pagos/pago_form_admin.html" if es_admin else "pagos/pago_form.html"
    return render(request, template, {"form": form})
