# usuarios/views.py
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views.generic.edit import FormView
from django.contrib import messages
from .models import Usuario, Categoria
from .forms import UsuarioForm, RegistrationForm, CustomLoginForm
from django.views import View
from django.shortcuts import redirect
from datetime import date
from django.core.exceptions import PermissionDenied

from utils.role_mixins import AdminRequiredForListMixin, SoloPropioMixin

class UsuarioCreateView(AdminRequiredForListMixin, CreateView):
    """
    Vista para que el admin pueda crear nuevos usuarios.
    Se utiliza el mismo formulario y template que en la edición.
    """
    model = Usuario
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_edit.html'
    success_url = reverse_lazy('usuarios:list')

    def form_valid(self, form):
        # Verificamos que el usuario actual es admin usando el método del mixin.
        current_user = self.get_current_user(self.request)
        if not current_user or current_user.rol != 'admin':
            raise PermissionDenied("Solo el admin puede crear usuarios.")
        # Aquí se podría agregar lógica adicional si se requiriera.
        return super().form_valid(form)

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
                estado_filtrado = 'activo'
            else:
                estado_filtrado = estado
            qs = qs.filter(estado=estado_filtrado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        if current_user:
            context['can_create'] = (current_user.rol == 'admin')
            # Por ejemplo, puedes pasar también el rol en el contexto
            context['current_role'] = current_user.rol
        return context

class UsuarioDetailView(SoloPropioMixin, DetailView):
    model = Usuario
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        context['current_user'] = current_user
        return context

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

    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        if current_user.rol != 'admin':
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Solo el admin puede eliminar usuarios.")
        return super().dispatch(request, *args, **kwargs)

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
        self.request.session['custom_user_id'] = user.id
        messages.success(self.request, "Login exitoso")
        return super().form_valid(form)
    
class CustomLogoutView(View):
    """
    Vista para cerrar sesión. Elimina la variable de sesión 'custom_user_id'
    y redirige al login.
    """
    def get(self, request, *args, **kwargs):
        request.session.flush()
        messages.info(request, "Has cerrado sesión")
        return redirect('usuarios:login')

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
        user.rol = 'miembro'
        user.estado = 'activo'
        if user.fecha_nacimiento:
            today = date.today()
            age = today.year - user.fecha_nacimiento.year  # Solo se usa el año
            # Asignar la categoría según la edad
            if age < 6:
                cat_name = "bola-roja"
            elif age < 10:
                cat_name = "bola-naranja"
            elif age < 12:
                cat_name = "bola-verde"
            elif age < 14:
                cat_name = "sub-14"
            elif age < 16:
                cat_name = "sub-16"
            elif age <= 21:
                cat_name = "sub-21"
            else:
                # Adultos: se usa el valor del campo 'nivel'
                cat_name = form.cleaned_data.get("nivel")
            categoria, created = Categoria.objects.get_or_create(nombre=cat_name)
            user.id_categoria = categoria
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)

