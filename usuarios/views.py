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

class UsuarioCreateView(CreateView):
    """
    Vista unificada para crear nuevos usuarios.
    Si se accede a través de /usuarios/register/ se trata como registro público (sin requerir usuario autenticado),
    y se fuerza el rol a "miembro". Si se accede por /usuarios/create/ se requiere que el usuario actual sea admin.
    """
    model = Usuario
    form_class = UsuarioForm
    success_url = reverse_lazy('usuarios:list')

    def get_template_names(self):
        if "register" in self.request.path:
            return ['usuarios/login.html']
        return ['usuarios/usuario_edit.html']

    def dispatch(self, request, *args, **kwargs):
        if "register" in request.path:
            return super().dispatch(request, *args, **kwargs)
        else:
            current_user = self.get_current_user(request)
            if not current_user or current_user.rol != 'admin':
                from django.core.exceptions import PermissionDenied
                raise PermissionDenied("Solo el admin puede crear usuarios.")
            return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if "register" in self.request.path:
            kwargs['modo'] = "register"
        else:
            kwargs['modo'] = "create"
        kwargs['current_user'] = self.get_current_user(self.request)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "register" in self.request.path:
            context["action"] = "register"
        else:
            context["action"] = "create"
        return context

    def get_current_user(self, request):
        user_id = request.session.get('custom_user_id')
        if user_id:
            from usuarios.models import Usuario
            try:
                return Usuario.objects.get(id=user_id)
            except Usuario.DoesNotExist:
                return None
        return None

    def form_valid(self, form):
        user = form.save(commit=False)
        if "register" in self.request.path:
            user.rol = "miembro"
        if user.rol == 'miembro' and user.fecha_nacimiento:
            today = date.today()
            age = today.year - user.fecha_nacimiento.year  # Se usa solo el año
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
                cat_name = form.cleaned_data.get("nivel")
            print("DEBUG: Fecha de nacimiento:", user.fecha_nacimiento)
            print("DEBUG: Edad calculada:", age)
            print("DEBUG: Categoría asignada:", cat_name)
            categoria, created = Categoria.objects.get_or_create(nombre=cat_name)
            print("DEBUG: Categoria obtenida:", categoria, "Creada:", created)
            user.id_categoria = categoria
        user.set_password(form.cleaned_data['password'])
        user.estado = user.estado or "activo"
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Imprimir los errores del formulario en la consola para depuración
        print("DEBUG: Errores del formulario:", form.errors.as_json())
        return super().form_invalid(form)



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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['modo'] = 'update'
        kwargs['current_user'] = self.get_current_user(self.request)
        return kwargs
    
    def form_valid(self, form):
        current_user = self.get_current_user(self.request)
        user = form.save(commit=False)

        # Solo proteger si no es admin editando a otro
        is_admin = current_user.rol == 'admin'
        editing_self = current_user.id == user.id

        if not is_admin and editing_self:
            # Restaurar los campos protegidos a su valor original (no permitir cambios)
            original = self.get_object()
            user.rol = original.rol
            user.nombre = original.nombre
            user.apellidos = original.apellidos
            user.estado = original.estado
            user.tipo_documento = original.tipo_documento
            user.num_documento = original.num_documento
            user.fecha_nacimiento = original.fecha_nacimiento
            user.matricula = original.matricula
            user.id_categoria = original.id_categoria  # esto incluye la categoría asignada por edad
            # También nivel, si quieres protegerlo
            # user.nivel = original.nivel  # solo si lo tienes como atributo persistente

        # Guardar cambios permitidos
        user.set_password(form.cleaned_data['password'])
        user.save()
        return super().form_valid(form)



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
        # Debug: mostrar fecha de nacimiento recibida
        if user.fecha_nacimiento:
            today = date.today()
            age = today.year - user.fecha_nacimiento.year  # Usamos solo el año
            print("DEBUG: Fecha de nacimiento:", user.fecha_nacimiento)
            print("DEBUG: Edad calculada:", age)

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
            print("DEBUG: cat_name asignado:", cat_name)

            # Obtener o crear la categoría
            categoria, created = Categoria.objects.get_or_create(nombre=cat_name)
            print("DEBUG: Categoria obtenida:", categoria, "Creada:", created)
            user.id_categoria = categoria
        else:
            print("DEBUG: No se proporcionó fecha de nacimiento.")
        user.set_password(form.cleaned_data['password'])
        user.save()
        print("DEBUG: ")
        return super().form_valid(form)
