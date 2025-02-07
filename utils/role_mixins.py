# utils/role_mixins.py
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from usuarios.models import Usuario

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
            # Redirige a su propia página de detalle
            return redirect('usuarios:detail', usuario_id=current_user.id)
        return super().dispatch(request, *args, **kwargs)

class SoloPropioMixin(UsuarioSessionMixin):
    """
    Para vistas de detalle (y edición/eliminación) que deben ser visibles solo
    por el mismo usuario o por un admin.
    """
    def dispatch(self, request, *args, **kwargs):
        current_user = self.get_current_user(request)
        if not current_user:
            return redirect('usuarios:login')
        requested_id = kwargs.get('usuario_id')
        # Si no es admin y está intentando acceder a un usuario distinto, se bloquea el acceso.
        if current_user.rol != 'admin' and current_user.id != requested_id:
            raise PermissionDenied("No tienes permiso para ver o modificar este usuario.")
        return super().dispatch(request, *args, **kwargs)
