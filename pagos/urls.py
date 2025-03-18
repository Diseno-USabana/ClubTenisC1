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
    path('detalle/<int:pk>/', PagoDetailView.as_view(), name='detail'),
    path('crear/', PagoCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', PagoUpdateView.as_view(), name='update'),
    path('eliminar/<int:pk>/', PagoDeleteView.as_view(), name='delete'),
]
