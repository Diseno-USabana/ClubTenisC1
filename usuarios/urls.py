# usuarios/urls.py
from django.urls import path
from .views import UsuarioListView, UsuarioDetailView, UsuarioUpdateView, UsuarioDeleteView

app_name = 'usuarios'

urlpatterns = [
    path('', UsuarioListView.as_view(), name='list'),
    path('<int:usuario_id>/', UsuarioDetailView.as_view(), name='detail'),
    path('<int:usuario_id>/edit/', UsuarioUpdateView.as_view(), name='edit'),
    path('<int:usuario_id>/delete/', UsuarioDeleteView.as_view(), name='delete'),
]
