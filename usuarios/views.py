# usuarios/views.py
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import Usuario
from .forms import UsuarioForm

from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from .forms import RegistrationForm
from django.contrib.auth import login
class UsuarioListView(ListView):
    model = Usuario
    #template_name = 'usuarios_list.html'
    context_object_name = 'usuarios'

    def get_queryset(self):
        """
        Permite filtrar los usuarios por el parámetro 'estado' en la URL, por ejemplo: ?estado=activo
        """
        qs = super().get_queryset()
        estado = self.request.GET.get('estado')
        if estado:
            # Mapea los valores externos a los internos, por ejemplo:
            if estado == 'inscrito':
                estado_filtrado = 'activo'
            elif estado == 'matriculado':
                estado_filtrado = 'activo'  # O el valor que corresponda
            else:
                estado_filtrado = estado
            qs = qs.filter(estado=estado_filtrado)
        return qs

class UsuarioDetailView(DetailView):
    model = Usuario
    #template_name = 'usuarios_detail.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

class UsuarioUpdateView(UpdateView):
    model = Usuario
    form_class = UsuarioForm
    #template_name = 'usuarios_edit.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'

    def get_success_url(self):
        return reverse('usuarios:detail', kwargs={'usuario_id': self.object.id})

class UsuarioDeleteView(DeleteView):
    model = Usuario
    #template_name = 'usuarios_confirm_delete.html'
    context_object_name = 'usuario'
    pk_url_kwarg = 'usuario_id'
    success_url = reverse_lazy('usuarios:list')


class CustomLoginView(LoginView):
    """
    Vista para el login. Utiliza el template 'usuarios/login.html' y,
    en el contexto se agrega 'action' para indicar que se trata del login.
    """
    template_name = 'usuarios/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'login'
        return context
    
class RegistrationView(FormView):
    """
    Vista para el registro de nuevos usuarios. Utiliza el mismo template
    'usuarios/login.html' y provee el formulario de registro (RegistrationForm).
    Se establece que, al registrar, el usuario tendrá el campo 'estado' en "activo".
    """
    template_name = 'usuarios/login.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('usuarios:login')  # Redirige al login luego de registrarse

    def form_valid(self, form):
        user = form.save(commit=False)
        # Se establece el estado en "activo" por defecto
        user.estado = 'activo'
        # Se almacena la contraseña de forma segura
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'register'
        return context