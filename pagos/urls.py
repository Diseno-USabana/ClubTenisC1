from django.urls import path
from .views import (
    PagoListView,
    PagoListUsuarioView,
    PagoDetailView,
    PagoUpdateView,
    PagoDeleteView,
    registrar_mensualidad,
    vista_crear_pago,
)

app_name = 'pagos'

urlpatterns = [
    path('', PagoListView.as_view(), name='list'),  # Vista para admin
    path('mis-pagos/<int:usuario_id>/', PagoListUsuarioView.as_view(), name='mis_pagos'),  # Vista para miembros
    path('crear/', vista_crear_pago, name='crear'),
    path('detalle/<int:pk>/', PagoDetailView.as_view(), name='detalle'),
    path('editar/<int:pk>/', PagoUpdateView.as_view(), name='editar'),
    path('eliminar/<int:pk>/', PagoDeleteView.as_view(), name='eliminar'),
    path('registrar-mensualidad/', registrar_mensualidad, name='registrar_mensualidad'),
]
