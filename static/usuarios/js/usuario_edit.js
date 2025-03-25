document.addEventListener("DOMContentLoaded", function () {
    console.log("Script usuario_edit.js cargado y ejecutándose...");

    const rolSelect = document.getElementById("id_rol");
    if (!rolSelect) {
        console.error("No se encontró el select de rol (id_rol).");
        return;
    }

    // Si no hay valor, forzamos un valor por defecto (por ejemplo, "admin")
    if (!rolSelect.value) {
        rolSelect.value = "admin";
    }

    const adminFields = document.getElementById("admin-fields");
    const entrenadorFields = document.getElementById("entrenador-fields");
    const miembroFields = document.getElementById("miembro-fields");
    const nivelField = document.getElementById("nivel-field");
    const fechaNacimiento = document.getElementById("id_fecha_nacimiento");

    function updateFieldsVisibility() {
        const selectedRole = rolSelect.value;
        console.log("Rol seleccionado:", selectedRole);

        // Ocultar todos los bloques
        if (adminFields) adminFields.style.display = "none";
        if (entrenadorFields) entrenadorFields.style.display = "none";
        if (miembroFields) miembroFields.style.display = "none";
        if (nivelField) nivelField.style.display = "none"; // oculto por defecto

        if (selectedRole === "admin" && adminFields) {
            adminFields.style.display = "block";
            console.log("Mostrando campos para admin");
        } else if (selectedRole === "entrenador" && entrenadorFields) {
            entrenadorFields.style.display = "block";
            console.log("Mostrando campos para entrenador");
        } else if (selectedRole === "miembro" && miembroFields) {
            miembroFields.style.display = "block";
            console.log("Mostrando campos para miembro");
            if (fechaNacimiento && fechaNacimiento.value) {
                const parts = fechaNacimiento.value.split("-");
                if (parts.length > 0) {
                    const birthYear = parseInt(parts[0], 10);
                    const currentYear = new Date().getFullYear();
                    const age = currentYear - birthYear;
                    console.log("Edad calculada:", age);
                    if (age > 21 && nivelField) {
                        nivelField.style.display = "block";
                        console.log("Mostrando campo de nivel");
                    } else if (nivelField) {
                        nivelField.style.display = "none";
                        console.log("Ocultando campo de nivel");
                    }
                }
            }
        }
    }

    updateFieldsVisibility();

    rolSelect.addEventListener("change", function () {
        console.log("Cambio detectado en rol:", rolSelect.value);
        updateFieldsVisibility();
    });

    if (fechaNacimiento) {
        fechaNacimiento.addEventListener("change", function () {
            if (rolSelect.value === "miembro") {
                const parts = fechaNacimiento.value.split("-");
                if (parts.length > 0) {
                    const birthYear = parseInt(parts[0], 10);
                    const currentYear = new Date().getFullYear();
                    const age = currentYear - birthYear;
                    console.log("Cambio en fecha. Edad calculada:", age);
                    if (age > 21 && nivelField) {
                        nivelField.style.display = "block";
                        console.log("Mostrando campo de nivel (por fecha)");
                    } else if (nivelField) {
                        nivelField.style.display = "none";
                        console.log("Ocultando campo de nivel (por fecha)");
                    }
                }
            }
        });
    }
});
