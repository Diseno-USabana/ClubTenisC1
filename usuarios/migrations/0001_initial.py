# Generated by Django 5.1.3 on 2025-02-08 03:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(blank=True, choices=[('admin', 'Admin'), ('entrenador', 'Entrenador'), ('miembro', 'Miembro')], max_length=20, null=True)),
                ('nombre', models.CharField(blank=True, max_length=10, null=True)),
                ('apellidos', models.CharField(blank=True, max_length=100, null=True)),
                ('correo', models.CharField(blank=True, max_length=20, null=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('password', models.CharField(max_length=128)),
                ('tipo_documento', models.CharField(blank=True, choices=[('CC', 'CC'), ('RC', 'RC'), ('CE', 'CE')], max_length=10, null=True)),
                ('num_documento', models.CharField(blank=True, max_length=20, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('estado', models.CharField(blank=True, choices=[('activo', 'activo'), ('eliminado', 'eliminado'), ('retirado', 'retirado')], max_length=20, null=True)),
                ('matricula', models.BooleanField(blank=True, default=False, null=True)),
                ('id_categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.categoria')),
            ],
        ),
    ]
