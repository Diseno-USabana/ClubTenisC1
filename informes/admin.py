# informes/admin.py
from django.contrib import admin
from .models import Informe

@admin.register(Informe)
class InformeAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'mes', 'anio', 'clases_mes', 'clases_asistidas', 'torneos_asistidos')
