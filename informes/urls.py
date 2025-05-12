# informes/urls.py
from django.urls import path
from .views import (
    InformeListView,
    InformeDetailView,
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
    path('<int:pk>/', InformeDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', InformeUpdateView.as_view(), name='update'),
    path('<int:pk>/eliminar/', InformeDeleteView.as_view(), name='delete'),
    path('generar/', generar_informe_view, name='generar'),
    path('mis-informes/', MisInformesListView.as_view(), name='mis_informes'),
]
