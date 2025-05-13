# usuarios/views.py
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from .models import Usuario, Categoria
from pagos.models import Pago
from .forms import UsuarioForm, RegistrationForm, CustomLoginForm
from django.views import View
from django.shortcuts import redirect, render
from datetime import date
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

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
            context["usuario"] = None
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
        qs        = super().get_queryset()
        estado    = self.request.GET.get('estado')
        rol       = self.request.GET.get('rol')
        categoria = self.request.GET.get('categoria')

        if estado:
            estado_filtrado = 'activo' if estado in ['inscrito', 'matriculado'] else estado
            qs = qs.filter(estado=estado_filtrado)
        
        if rol:
            qs = qs.filter(rol=rol)
            # Si filtra por miembro y hay categoría, también la aplicamos
            if rol == 'miembro' and categoria:
                qs = qs.filter(id_categoria__id=categoria)

        return qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.get_current_user(self.request)
        if current_user:
            context['can_create']  = (current_user.rol == 'admin')
            context['current_role'] = current_user.rol

        # si se está filtrando por miembro, enviamos todas las categorías
        if self.request.GET.get('rol') == 'miembro':
            from .models import Categoria
            context['categorias'] = Categoria.objects.all()
            context['selected_categoria'] = self.request.GET.get('categoria', '')
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria = self.object.id_categoria
        context["nombre_categoria"] = categoria.nombre if categoria else "Sin categoría"
        return context

    def form_valid(self, form):
        current_user = self.get_current_user(self.request)
        user = form.instance  # la instancia a modificar

        # --- Debug prints ---
        print("DEBUG ✅ POST recibido:", self.request.POST)
        print("DEBUG ✅ cleaned_data final:", form.cleaned_data)

        # --- Campos editables ---
        user.correo = form.cleaned_data.get("correo")
        user.telefono = form.cleaned_data.get("telefono")

        # --- Restaurar protegidos si no es admin y edita su propio perfil ---
        is_admin = current_user.rol == 'admin'
        editing_self = current_user.id == user.id
        original = self.get_object()
        if not is_admin and editing_self:
            for field in ['rol','nombre','apellidos','estado','tipo_documento',
                          'num_documento','fecha_nacimiento','matricula','id_categoria']:
                setattr(user, field, getattr(original, field))

        # --- Contraseña ---
        raw_pass = form.cleaned_data.get("password")
        if raw_pass:
            user.set_password(raw_pass)
        else:
            user.password = original.password

        # Actualizar categoría según edad y nivel
        if is_admin and form.cleaned_data.get("fecha_nacimiento") and form.cleaned_data.get("rol") == "miembro":
            fecha_nueva = form.cleaned_data["fecha_nacimiento"]
            edad = date.today().year - fecha_nueva.year

            if edad > 21:
                # Adulto → usa el nivel como categoría
                nivel = form.cleaned_data.get("nivel")
                if nivel:
                    categoria, _ = Categoria.objects.get_or_create(nombre=nivel)
                    user.id_categoria = categoria
            else:
                # Menor de 22 → respetar selección manual del admin (si difiere de la calculada)
                categoria_form = form.cleaned_data.get("id_categoria")
                if categoria_form:
                    user.id_categoria = categoria_form
                else:
                    # fallback si no vino (debería ser raro)
                    if edad < 6:
                        cat_name = "bola-roja"
                    elif edad < 10:
                        cat_name = "bola-naranja"
                    elif edad < 12:
                        cat_name = "bola-verde"
                    elif edad < 14:
                        cat_name = "sub-14"
                    elif edad < 16:
                        cat_name = "sub-16"
                    else:
                        cat_name = "sub-21"
                    categoria, _ = Categoria.objects.get_or_create(nombre=cat_name)
                    user.id_categoria = categoria


        # --- Guardado definitivo ---
        user.save()
        print("DEBUG ✅ Usuario guardado en DB:", user)
        # Importante: asignamos self.object para que UpdateView sepa qué usar
        self.object = user
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        # Obtener el form con los datos del POST
        form = self.get_form()
        # DEBUG: validar form e imprimir errores
        print("DEBUG 🔍 form.is_valid():", form.is_valid())
        print("DEBUG 🔍 form.errors:", form.errors)
        # También los datos limpios si está validando
        if hasattr(form, 'cleaned_data'):
            print("DEBUG 🔍 form.cleaned_data:", form.cleaned_data)
        return super().post(request, *args, **kwargs)
    
    def form_invalid(self, form):
        print("DEBUG 🚫 Entramos en form_invalid")
        print("DEBUG 🚫 form.errors:", form.errors.as_json())
        return super().form_invalid(form)




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
            age = today.year - user.fecha_nacimiento.year
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
            categoria, _ = Categoria.objects.get_or_create(nombre=cat_name)
            user.id_categoria = categoria

        user.set_password(form.cleaned_data['password'])
        user.matricula = True
        user.save()

        # 🔐 IMPORTANTE: asignar `self.object` para que Django trate este form como exitoso
        self.object = user

        # ✅ Crear el pago
        print("DEBUG: Usuario guardado con ID:", user.id)
        if user.id:
            Pago.objects.create(
                usuario=user,
                concepto='matricula',
                fecha=date.today(),
                monto=100000
            )
            print("DEBUG ✅ Pago creado para el usuario:", user.id)
        else:
            print("ERROR ❌ No se pudo crear el pago, user.id es None")

        # ✅ Autologin
        self.request.session['custom_user_id'] = user.id
        messages.success(self.request, "¡Registro exitoso! Ya has iniciado sesión y se registró el pago de matrícula.")

        return redirect(reverse('usuarios:detail', kwargs={'usuario_id': user.id}))

class UsuarioPasswordUpdateView(SoloPropioMixin, View):
    def get(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        return render(request, 'usuarios/cambiar_password.html', {'usuario': usuario})

    def post(self, request, usuario_id):
        usuario = Usuario.objects.get(id=usuario_id)
        nueva_clave = request.POST.get("password")
        confirmacion = request.POST.get("confirm_password")

        if not nueva_clave or not confirmacion:
            messages.error(request, "Debes completar ambos campos.")
        elif nueva_clave != confirmacion:
            messages.error(request, "Las contraseñas no coinciden.")
        else:
            usuario.set_password(nueva_clave)
            usuario.save()
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('usuarios:detail', usuario_id=usuario.id)

        return render(request, 'usuarios/cambiar_password.html', {'usuario': usuario})

class NosotrosView(TemplateView):
    template_name = 'usuarios/nosotros.html'