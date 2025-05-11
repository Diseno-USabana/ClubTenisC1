from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    # RegistrationView,  # Se elimina o se deja de usar
    UsuarioListView,
    UsuarioDetailView,
    UsuarioUpdateView,
    UsuarioDeleteView,
    UsuarioCreateView,
    UsuarioPasswordUpdateView,
    RegistrationView,
)

app_name = 'usuarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('create/', UsuarioCreateView.as_view(), name='create'),
    path('', UsuarioListView.as_view(), name='list'),
    path('user/<int:usuario_id>/', UsuarioDetailView.as_view(), name='detail'),
    path('<int:usuario_id>/edit/', UsuarioUpdateView.as_view(), name='edit'),
    path('<int:usuario_id>/delete/', UsuarioDeleteView.as_view(), name='delete'),

    path('<int:usuario_id>/cambiar-clave/', UsuarioPasswordUpdateView.as_view(), name='change_password'),
]

