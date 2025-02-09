# usuarios/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    rol = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Admin'),
            ('entrenador', 'Entrenador'),
            ('miembro', 'Miembro'),
        ]
    )
    nombre = models.CharField(max_length=50, blank=True, null=True)
    apellidos = models.CharField(max_length=50, blank=True, null=True)
    correo = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=128)
    tipo_documento = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[
            ('TI', 'TI'),
            ('CC', 'CC'),
            ('RC', 'RC'),
            ('CE', 'CE'),
        ]
    )
    num_documento = models.CharField(max_length=20, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    id_categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'activo'),
            ('eliminado', 'eliminado'),
            ('retirado', 'retirado'),
        ],
        blank=True,
        null=True,
        default='activo'
    )
    matricula = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
