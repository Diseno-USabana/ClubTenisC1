from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from usuarios.models import Usuario
from pagos.models import Pago

class UsuarioSessionMixin:
    """
    Mixin básico para obtener el usuario desde la sesión.
    """
    def get_current_user(self, request):
        user_id = request.session.get('custom_user_id')
        if not user_id:
            return None
        try:
            return Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            return None

class AdminEntrenadorRequiredMixin(UsuarioSessionMixin):
    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        if current_user.rol not in ['admin', 'entrenador']:
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('eventos:entrenamientos_list')
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredForListMixin(UsuarioSessionMixin):
    """
    Para vistas que deben ser accesibles únicamente por administradores.
    Si el usuario es entrenador o miembro, se le redirige a su detalle.
    """
    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        if current_user.rol != 'admin':
            return redirect('usuarios:detail', usuario_id=current_user.id)
        return super().dispatch(request, *args, **kwargs)

class SoloPropioMixin(UsuarioSessionMixin):
    """
    Permite acceso solo si el usuario es el dueño del objeto (por usuario_id o pk),
    o si es administrador.
    """
    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')

        # Intentar obtener el ID del usuario relacionado
        requested_id = None
        if 'usuario_id' in kwargs:
            requested_id = kwargs['usuario_id']
        elif 'pk' in kwargs:
            try:
                pago = Pago.objects.get(pk=kwargs['pk'])
                requested_id = pago.usuario.id
            except Pago.DoesNotExist:
                raise PermissionDenied("El recurso solicitado no existe.")

        if current_user.rol != 'admin' and current_user.id != requested_id:
            raise PermissionDenied("No tienes permiso para ver o modificar este recurso.")

        return super().dispatch(request, *args, **kwargs)
