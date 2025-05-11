from django.db import models
from usuarios.models import Usuario
from django.core.exceptions import ValidationError
from datetime import date

class Pago(models.Model):
    CONCEPTOS = [
        ("matricula", "Matrícula"),
        ("mensualidad", "Mensualidad"),
        ("torneo", "Torneo"),
    ]

    MESES = [(i, nombre) for i, nombre in enumerate([
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ], 1)]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    concepto = models.CharField(max_length=20, choices=CONCEPTOS)
    fecha = models.DateField(default=date.today)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    anio = models.IntegerField(blank=True, null=True)
    mes = models.IntegerField(choices=MESES, blank=True, null=True)

    def clean(self):
        # Solo mensualidad requiere mes y año
        if self.concepto == "mensualidad" and (not self.anio or not self.mes):
            raise ValidationError("Mensualidad requiere mes y año.")
        if self.concepto != "mensualidad" and (self.anio or self.mes):
            raise ValidationError("Mes y año solo se permiten para mensualidades.")

    def __str__(self):
        return f"{self.usuario} - {self.concepto} - {self.fecha}"
