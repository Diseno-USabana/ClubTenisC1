# pagos/urls.py
from django.urls import path

from pagos.views import PagoListUsuarioView, vista_crear_pago
from .views import (
    PagoListView,
    PagoListUsuarioView,
    PagoUpdateView,
    PagoDeleteView,
    PagoDetailView,
    registrar_mensualidad,
    vista_crear_pago,
)

app_name = 'pagos'

urlpatterns = [
    path('', PagoListView.as_view(), name='list'),  # Para admin
    path('mis-pagos/<int:usuario_id>/', PagoListUsuarioView.as_view(), name='mis_pagos'),
    path('crear/', vista_crear_pago, name='crear'),
    path('detalle/<int:pk>/', PagoDetailView.as_view(), name='detalle'),
    path('editar/<int:pk>/', PagoUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', PagoDeleteView.as_view(), name='eliminar'),
    path('registrar-mensualidad/', registrar_mensualidad, name='registrar_mensualidad'),
]