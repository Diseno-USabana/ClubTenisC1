from .models import Usuario

def current_user(request):
    """
    Si hay un 'custom_user_id' en la sesión, intenta obtener el Usuario correspondiente,
    y lo agrega al contexto como 'current_user'. De lo contrario, devuelve None.
    """
    user = None
    user_id = request.session.get('custom_user_id')
    if user_id:
        try:
            user = Usuario.objects.get(id=user_id)
        except Usuario.DoesNotExist:
            user = None
    return {'current_user': user}
