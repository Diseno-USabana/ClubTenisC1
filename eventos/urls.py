from django.urls import path
from .views import (
    EntrenamientoListView,
    TorneoListView,
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
    # Listados separados
    path('entrenamientos/', EntrenamientoListView.as_view(), name='entrenamientos_list'),
    path('torneos/', TorneoListView.as_view(), name='torneos_list'),
    # Vistas para crear, editar y eliminar (usadas para ambos tipos)
    path('create/', EventoCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', EventoUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', EventoDeleteView.as_view(), name='delete'),
    # Acciones para entrenamientos
    path('<int:evento_id>/inscribirse_entrenamiento/', inscribirse_entrenamiento, name='inscribirse_entrenamiento'),
    path('<int:evento_id>/desinscribirse_entrenamiento/', desinscribirse_entrenamiento, name='desinscribirse_entrenamiento'),
    # Acciones para torneos
    path('<int:evento_id>/inscribirse_torneo/', inscribirse_torneo, name='inscribirse_torneo'),
    path('<int:evento_id>/desinscribirse_torneo/', desinscribirse_torneo, name='desinscribirse_torneo'),
]
