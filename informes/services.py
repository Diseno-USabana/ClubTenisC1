# app/services.py
from django.db.models import Count, Q
from .models import Informe, Usuario, Entrenamiento, AsistenciaEntrenamiento, Torneo, AsistenciaTorneo

def contar_clases_asignadas(usuario, mes, anio):
    return AsistenciaEntrenamiento.objects.filter(
        usuario=usuario,
        entrenamiento__fecha__startswith=f"{anio}-{mes}"
    ).count()

def contar_clases_asistidas(usuario, mes, anio):
    return AsistenciaEntrenamiento.objects.filter(
        usuario=usuario,
        entrenamiento__fecha__startswith=f"{anio}-{mes}",
        estado="presente"
    ).count()

def contar_torneos_asistidos(usuario, mes, anio):
    return AsistenciaTorneo.objects.filter(
        usuario=usuario,
        torneo__fecha__startswith=f"{anio}-{mes}"
    ).count()

def encontrar_top_3_torneos(usuario, mes, anio):
    asistencias = AsistenciaTorneo.objects.filter(
        usuario=usuario,
        torneo__fecha__startswith=f"{anio}-{mes}"
    ).order_by('puesto')[:3]
    # Retornamos una lista de dicts con nombre y puesto
    return [{"nombre": at.torneo.nombre, "puesto": at.puesto} for at in asistencias]

def generar_informe(usuario, mes, anio):
    clases_asignadas = contar_clases_asignadas(usuario, mes, anio)
    clases_asistidas = contar_clases_asistidas(usuario, mes, anio)
    torneos_asistidos = contar_torneos_asistidos(usuario, mes, anio)
    top_torneos = encontrar_top_3_torneos(usuario, mes, anio)
    
    informe = Informe.objects.create(
        usuario=usuario,
        mes=mes.zfill(2),
        anio=int(anio),
        clases_mes=clases_asignadas,
        clases_asistidas=clases_asistidas,
        torneos_asistidos=torneos_asistidos,
        top_torneos=top_torneos
    )
    return informe

def generar_informes_para_matriculados(mes, anio):
    usuarios = Usuario.objects.filter(estado='matriculado')
    informes = []
    for usuario in usuarios:
        informe, created = Informe.objects.update_or_create(
            usuario=usuario,
            mes=mes.zfill(2),
            anio=int(anio),
            defaults={
                'clases_mes': contar_clases_asignadas(usuario, mes, anio),
                'clases_asistidas': contar_clases_asistidas(usuario, mes, anio),
                'torneos_asistidos': contar_torneos_asistidos(usuario, mes, anio),
                'top_torneos': encontrar_top_3_torneos(usuario, mes, anio)
            }
        )
        informes.append(informe)
    return informes
