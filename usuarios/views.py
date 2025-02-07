# usuarios/views.py
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.contrib import messages
from .models import Usuario
from .forms import UsuarioForm, RegistrationForm, CustomLoginForm

# Importamos los mixins desde la carpeta utils (asegúrate de que la carpeta utils esté en PYTHONPATH)
from utils.role_mixins import AdminRequiredForListMixin, SoloPropioMixin

class UsuarioListView(AdminRequiredForListMixin, ListView):
    model = Usuario
    context_object_name = 'usuarios'

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado:
            if estado == 'inscrito':
                estado_filtrado = 'activo'
            elif estado == 'matriculado':
                estado_filtrado = 'activo'  # O el valor que corresponda
            else:
                estado_filtrado = estado
            qs = qs.filter(estado=estado_filtrado)
        return qs

class UsuarioDetailView(SoloPropioMixin, DetailView):
    model = Usuario
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

class UsuarioUpdateView(SoloPropioMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'
    template_name = 'usuarios/usuario_edit.html'

    def get_success_url(self):
        return reverse('usuarios:detail', kwargs={'usuario_id': self.object.id})

class UsuarioDeleteView(SoloPropioMixin, DeleteView):
    model = Usuario
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'
    success_url = reverse_lazy('usuarios:list')

class CustomLoginView(FormView):
    """
    Vista para el login. Utiliza el template 'usuarios/login.html' y asigna en la sesión
    el id del usuario logueado.
    """
    template_name = 'usuarios/login.html'
    form_class = CustomLoginForm
    success_url = reverse_lazy('usuarios:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'login'
        return context

    def form_valid(self, form):
        user = form.cleaned_data.get("user")
        # Guardamos el id del usuario en la sesión (login manual)
        self.request.session['custom_user_id'] = user.id
        messages.success(self.request, "Login exitoso")
        return super().form_valid(form)

class RegistrationView(FormView):
    """
    Vista para el registro de nuevos usuarios. Utiliza el mismo template 'usuarios/login.html'
    y provee el formulario de registro (RegistrationForm). Se asigna el campo 'estado' en "activo".
    """
    template_name = 'usuarios/login.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('usuarios:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'register'
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.estado = 'activo'
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)
