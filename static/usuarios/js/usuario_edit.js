document.addEventListener("DOMContentLoaded", function () {
    console.log("Updated1");
    const rolSelect = document.getElementById("id_rol");
    const fechaNacimiento = document.getElementById("id_fecha_nacimiento");

    function updateFieldsVisibility() {
        if (!rolSelect) return;
        const selectedRole = rolSelect.value;

        // Oculta todos los campos
        document.querySelectorAll(".campo").forEach(el => {
            el.style.display = "none";
        });

        // Muestra solo los campos cuyo data-roles incluye EXACTAMENTE el rol seleccionado
        document.querySelectorAll(".campo").forEach(el => {
            const roles = el.getAttribute("data-roles");
            if (roles && roles.split(",").map(r => r.trim()).includes(selectedRole)) {
                el.style.display = "block";
            }
        });

        // Mostrar campo "nivel" solo si el usuario es miembro y mayor de 21
        if (selectedRole === "miembro" && fechaNacimiento && fechaNacimiento.value) {
            const birthYear = parseInt(fechaNacimiento.value.split("-")[0], 10);
            const age = new Date().getFullYear() - birthYear;
            const nivelEl = document.getElementById("field-nivel");
            if (nivelEl) {
                nivelEl.style.display = age > 21 ? "block" : "none";
            }
        }
    }

    // Escucha cambios en el selector de rol
    if (rolSelect) {
        rolSelect.addEventListener("change", updateFieldsVisibility);
    }

    // Escucha cambios en la fecha de nacimiento
    if (fechaNacimiento) {
        fechaNacimiento.addEventListener("change", updateFieldsVisibility);
    }

    // Ejecutar después del render para evitar errores en carga con validaciones
    setTimeout(updateFieldsVisibility, 0);
});
