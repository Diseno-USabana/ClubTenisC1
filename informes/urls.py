# informes/urls.py
from django.urls import path
from .views import (
    InformeDetailAdminView,
    InformeDetailMiembroView,
    InformeListView,
    InformeCreateView,
    InformeUpdateView,
    InformeDeleteView,
    MisInformesListView,
    generar_informe_view,
)

app_name = 'informes'


urlpatterns = [
    path('', InformeListView.as_view(), name='list'),
    path('crear/', InformeCreateView.as_view(), name='create'),
    path('editar/<int:pk>/', InformeUpdateView.as_view(), name='update'),
    path('eliminar/<int:pk>/', InformeDeleteView.as_view(), name='delete'),
    path('detalle/<int:pk>/', InformeDetailAdminView.as_view(), name='detail_admin'),
    path('mi-informe/<int:pk>/', InformeDetailMiembroView.as_view(), name='detail_miembro'),
    path('mis-informes/', MisInformesListView.as_view(), name='mis_informes'),
    path('generar/', generar_informe_view, name='generar'),
]

