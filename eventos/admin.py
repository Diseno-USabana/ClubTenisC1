# eventos/admin.py
from django.contrib import admin
from .models import Evento, AsistenciaEntrenamiento, AsistenciaTorneo, Pago

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'fecha', 'hora', 'capacidad', 'duracion', 'entrenador', 'categoria', 'costo')
    list_filter = ('tipo', 'fecha')
    search_fields = ('nombre',)

@admin.register(AsistenciaEntrenamiento)
class AsistenciaEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'entrenamiento', 'estado')
    list_filter = ('estado',)
    search_fields = ('usuario__nombre',)

@admin.register(AsistenciaTorneo)
class AsistenciaTorneoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'torneo', 'puesto')
    list_filter = ('torneo',)
    search_fields = ('usuario__nombre',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'monto', 'fecha')
