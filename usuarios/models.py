# usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    EMAIL_FIELD = "correo"
    # Opciones para cada campo con valores limitados
    ROL_CHOICES = [
        ('admin', 'Admin'),
        ('entrenador', 'Entrenador'),
        ('miembro', 'Miembro'),
    ]
    TIPO_DOCUMENTO_CHOICES = [
        ('TI', 'TI'),
        ('CC', 'CC'),
        ('RC', 'RC'),
        ('CE', 'CE'),
    ]
    ESTADO_CHOICES = [
        ('activo', 'activo'),
        ('eliminado', 'eliminado'),
        ('retirado', 'retirado'),
    ]
    MATRICULA_CHOICES = [
        ('inscrito', 'inscrito'),
        ('matriculado', 'matriculado'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, blank=True, null=True)
    nombre = models.CharField(max_length=10, blank=True, null=True)
    apellidos = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    tipo_documento = models.CharField(max_length=10, blank=True, null=True, choices=TIPO_DOCUMENTO_CHOICES)
    num_documento = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, blank=True, null=True)
    matricula = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"
