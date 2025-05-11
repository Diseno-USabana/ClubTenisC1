# pagos/urls.py
from django.urls import path
from .views import (
    PagoListView,
    PagoDetailView,
    PagoCreateView,
    PagoUpdateView,
    PagoDeleteView,
)

app_name = 'pagos'

urlpatterns = [
    path('', PagoListView.as_view(), name='list'),
    path('crear/', PagoCreateView.as_view(), name='create'),
    path('<int:pk>/editar/', PagoUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', PagoDeleteView.as_view(), name='delete'),
    path('<int:pk>/', PagoDetailView.as_view(), name='detail'),
]