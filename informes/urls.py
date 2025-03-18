# informes/urls.py
from django.urls import path
from .views import (
    InformeListView,
    InformeDetailView,
    InformeCreateView,
    InformeUpdateView,
    InformeDeleteView,
)

app_name = 'informes'

urlpatterns = [
    path('', InformeListView.as_view(), name='list'),
    path('detalle/<int:pk>/', InformeDetailView.as_view(), name='detail'),
    path('crear/', InformeCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', InformeUpdateView.as_view(), name='update'),
    path('eliminar/<int:pk>/', InformeDeleteView.as_view(), name='delete'),
]
