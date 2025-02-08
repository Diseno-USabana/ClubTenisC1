# eventos/urls.py
from django.urls import path
from .views import (
    EventoListView,
    EventoCreateView,
    EventoUpdateView,
    EventoDeleteView,
    inscribirse_entrenamiento,
    desinscribirse_entrenamiento,
    inscribirse_torneo,
    desinscribirse_torneo,
)

app_name = 'eventos'

urlpatterns = [
    path('', EventoListView.as_view(), name='list'),
    path('create/', EventoCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', EventoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', EventoDeleteView.as_view(), name='delete'),
    # Acciones para entrenamientos:
    path('<int:evento_id>/inscribirse_entrenamiento/', inscribirse_entrenamiento, name='inscribirse_entrenamiento'),
    path('<int:evento_id>/desinscribirse_entrenamiento/', desinscribirse_entrenamiento, name='desinscribirse_entrenamiento'),
    # Acciones para torneos:
    path('<int:evento_id>/inscribirse_torneo/', inscribirse_torneo, name='inscribirse_torneo'),
    path('<int:evento_id>/desinscribirse_torneo/', desinscribirse_torneo, name='desinscribirse_torneo'),
]
