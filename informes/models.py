from django.db import models
from usuarios.models import Usuario  
from eventos.models import AsistenciaTorneo  

class Informe(models.Model):
    OPCIONES_MES = (
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='informes')
    anio = models.IntegerField()
    mes = models.IntegerField(choices=OPCIONES_MES, blank=True, null=True)
    clases = models.IntegerField(default=0)
    clases_asistidas = models.IntegerField(default=0)
    torneos_asistidos = models.IntegerField(default=0)
    asistencia_torneo1 = models.ForeignKey(AsistenciaTorneo, on_delete=models.SET_NULL, null=True, blank=True, related_name='asistencia_torneo1')
    asistencia_torneo2 = models.ForeignKey(AsistenciaTorneo, on_delete=models.SET_NULL, null=True, blank=True, related_name='asistencia_torneo2')
    asistencia_torneo3 = models.ForeignKey(AsistenciaTorneo, on_delete=models.SET_NULL, null=True, blank=True, related_name='asistencia_torneo3')

    def __str__(self):
        return f'Informe de {self.usuario} para {self.mes}/{self.anio}'

