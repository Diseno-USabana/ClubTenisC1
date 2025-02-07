from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,  # Importamos la nueva vista
    RegistrationView,
    UsuarioListView,
    UsuarioDetailView,
    UsuarioUpdateView,
    UsuarioDeleteView,
)

app_name = 'usuarios'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('', UsuarioListView.as_view(), name='list'),
    path('user/<int:usuario_id>/', UsuarioDetailView.as_view(), name='detail'),
    path('<int:usuario_id>/edit/', UsuarioUpdateView.as_view(), name='edit'),
    path('<int:usuario_id>/delete/', UsuarioDeleteView.as_view(), name='delete'),
]
