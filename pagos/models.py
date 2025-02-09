# pagos/models.py
from django.db import models
from usuarios.models import Usuario

from django.db import models
from usuarios.models import Usuario  # Asegúrate de tener la importación correcta

class Pago(models.Model):
    OPCIONES_CONCEPTO = (
        ('matricula', 'Matrícula'),
        ('mensualidad', 'Mensualidad'),
        ('torneo', 'Torneo'),
    )
    
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

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, blank=True, null=True)
    concepto = models.CharField(max_length=255, choices=OPCIONES_CONCEPTO)
    fecha = models.DateField()
    monto = models.IntegerField()
    anio = models.IntegerField(blank=True, null=True, help_text="Mensualidad únicamente")
    mes = models.IntegerField(choices=OPCIONES_MES, blank=True, null=True, help_text="Mensualidad únicamente")

    def __str__(self):
        return f"Pago {self.id} - {self.concepto}"


