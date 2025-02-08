# eventos/models.py
from django.db import models
from usuarios.models import Usuario, Categoria
from pagos.models import Pago

class Evento(models.Model):
    TIPO_CHOICES = [
        ('torneo', 'Torneo'),
        ('entrenamiento', 'Entrenamiento'),
    ]
    entrenador = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='eventos_creados'
    )
    # Para torneos, este campo será nulo.
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Null si es torneo"
    )
    nombre = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    capacidad = models.IntegerField(
        default=12,
        help_text="Default 12"
    )
    duracion = models.IntegerField(
        help_text="Duración en minutos"
    )
    tipo = models.CharField(
        max_length=20, 
        choices=TIPO_CHOICES
    )
    # Campo de costo solo para torneos; en entrenamientos se dejará en null.
    costo = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="Solo para torneos"
    )

    def __str__(self):
        return self.nombre

class AsistenciaEntrenamiento(models.Model):
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    entrenamiento = models.ForeignKey(
        Evento, 
        on_delete=models.CASCADE,
        related_name="asistencias_entrenamiento"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES
    )

    def __str__(self):
        return f"{self.usuario} - {self.entrenamiento} ({self.estado})"


class AsistenciaTorneo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    torneo = models.ForeignKey(
        Evento, 
        on_delete=models.CASCADE,
        related_name="asistencias_torneo"
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    pago = models.ForeignKey(
        Pago, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    puesto = models.IntegerField()

    def __str__(self):
        return f"{self.usuario} - {self.torneo} (Puesto: {self.puesto})"

