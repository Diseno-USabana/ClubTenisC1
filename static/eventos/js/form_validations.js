document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    if (!form) return;

    form.addEventListener("submit", function (e) {
        const tipo = document.querySelector("input[name='tipo']")?.value || 'entrenamiento';
        const fecha = document.querySelector("input[name='fecha']");
        const hora = document.querySelector("input[name='hora']");
        const duracion = document.querySelector("input[name='duracion']");
        const capacidad = document.querySelector("input[name='capacidad']");
        const costo = document.querySelector("input[name='costo']");

        let errores = [];

        // Fecha
        if (!fecha.value) errores.push("La fecha es obligatoria.");

        // Hora
        if (!hora.value) {
            errores.push("La hora es obligatoria.");
        } else {
            const horaParts = hora.value.split(":");
            const horaInt = parseInt(horaParts[0]);
            if (tipo === 'entrenamiento' && (horaInt < 6 || horaInt >= 22)) {
                errores.push("Los entrenamientos deben estar entre las 6:00 y las 22:00.");
            } else if (tipo === 'torneo' && (horaInt < 6 || horaInt >= 22)) {
                errores.push("Los torneos deben estar entre las 6:00 y las 22:00.");
            }
        }

        // Duración
        const duracionVal = parseInt(duracion.value);
        if (isNaN(duracionVal) || duracionVal < 15 || duracionVal > 180) {
            errores.push("La duración debe estar entre 15 y 180 minutos.");
        }

        // Capacidad (solo para entrenamiento)
        if (tipo === 'entrenamiento' && capacidad) {
            const capVal = parseInt(capacidad.value);
            if (isNaN(capVal) || capVal < 1 || capVal > 12) {
                errores.push("La capacidad debe estar entre 1 y 12.");
            }
        }

        // Costo (solo para torneo)
        if (tipo === 'torneo' && costo) {
            const costoVal = parseInt(costo.value);
            if (isNaN(costoVal) || costoVal <= 0) {
                errores.push("El costo del torneo debe ser mayor a 0.");
            }
        }

        if (errores.length > 0) {
            e.preventDefault();
            alert("Corrige los siguientes errores:\n\n" + errores.join("\n"));
        }
    });
});
