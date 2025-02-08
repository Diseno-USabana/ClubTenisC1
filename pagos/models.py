# pagos/models.py
from django.db import models

class Pago(models.Model):
    estado = models.CharField(max_length=50)
    concepto = models.CharField(max_length=255)
    fecha = models.CharField(max_length=20)  # Se usa CharField según la especificación (puedes considerar DateField si lo prefieres)
    monto = models.IntegerField()

    def __str__(self):
        return f"Pago {self.id} - {self.concepto} ({self.estado})"
