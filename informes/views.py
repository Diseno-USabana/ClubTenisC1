# app/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Informe, Usuario
from .services import generar_informes_para_matriculados

def informes_view(request):
    if request.method == "POST":
        anio = request.POST.get("anio")
        mes = request.POST.get("mes")
        if not (anio and mes and anio.isdigit() and mes.isdigit()):
            messages.error(request, "Año y mes deben ser números.")
            return redirect("informes")
        mes_int = int(mes)
        if not (1 <= mes_int <= 12):
            messages.error(request, "Mes debe estar entre 1 y 12.")
            return redirect("informes")
        
        # Generar o actualizar los informes para usuarios matriculados
        generar_informes_para_matriculados(mes, anio)
        messages.success(request, f"Informes generados para {mes_int:02d}/{anio}.")
        return redirect("informes")
    
    # En GET, mostramos el formulario y la lista de informes filtrados (si se reciben parámetros)
    informes = Informe.objects.all().order_by("-anio", "-mes")
    # Opcional: podrías filtrar por usuario si recibes un parámetro en la URL
    return render(request, "informes.html", {"informes": informes})
