from django.contrib import admin
from django.db.models import Count
from .models import Informe
from eventos.models import AsistenciaEntrenamiento, AsistenciaTorneo

@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'mes', 'anio', 'get_clases_mes', 'clases_asistidas', 'torneos_asistidos')

    def get_clases_mes(self, obj):
        # Buscar cantidad de asistencias a entrenamientos del usuario en el mes y año del informe
        clases_entrenamiento = AsistenciaEntrenamiento.objects.filter(
            usuario=obj.usuario,
            entrenamiento__fecha__year=obj.anio,
            entrenamiento__fecha__month=obj.mes
        ).count()

        # Buscar cantidad de asistencias a torneos del usuario en el mes y año del informe
        torneos_asistidos = AsistenciaTorneo.objects.filter(
            usuario=obj.usuario,
            torneo__fecha__year=obj.anio,
            torneo__fecha__month=obj.mes
        ).count()

        return clases_entrenamiento + torneos_asistidos  # Suma de ambos valores
    
    get_clases_mes.short_description = 'Clases en el mes'  # Nombre en el panel de admin
