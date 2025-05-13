document.addEventListener("DOMContentLoaded", function () {
    const rolSelect = document.getElementById("id_rol");
    const fechaNacimiento = document.getElementById("id_fecha_nacimiento");
    const nivelField = document.getElementById("field-nivel");
    const categoriaSelect = document.getElementById("id_id_categoria");

    let edadOriginal = null;

    function calcularEdad(fechaStr) {
        if (!fechaStr) return null;
        const birthYear = parseInt(fechaStr.split("-")[0], 10);
        const age = new Date().getFullYear() - birthYear;
        return age;
    }

    function calcularCategoria(edad) {
        if (edad < 6) return "bola-roja";
        if (edad < 10) return "bola-naranja";
        if (edad < 12) return "bola-verde";
        if (edad < 14) return "sub-14";
        if (edad < 16) return "sub-16";
        if (edad <= 21) return "sub-21";
        return null;  // Adulto, debe elegir nivel
    }

    function updateFieldsVisibility() {
        if (!rolSelect) return;
        const selectedRole = rolSelect.value;

        document.querySelectorAll(".campo").forEach(el => {
            el.style.display = "none";
        });

        document.querySelectorAll(".campo").forEach(el => {
            const roles = el.getAttribute("data-roles");
            if (roles && roles.split(",").map(r => r.trim()).includes(selectedRole)) {
                el.style.display = "block";
            }
        });

        const edad = calcularEdad(fechaNacimiento?.value);
        if (selectedRole === "miembro" && edad !== null) {
            if (nivelField) nivelField.style.display = edad > 21 ? "block" : "none";
        }

        const categoriaField = document.getElementById("field-id_categoria");

        if (selectedRole === "miembro" && edad !== null) {
            if (nivelField) nivelField.style.display = edad > 21 ? "block" : "none";
            if (categoriaField) categoriaField.style.display = edad <= 21 ? "block" : "none";
        }

    }

    function verificarCambioEdad() {
        if (!fechaNacimiento || !categoriaSelect) return;
    
        const nuevaEdad = calcularEdad(fechaNacimiento.value);
        if (nuevaEdad === null || edadOriginal === null) return;
    
        const edadEraSub21  = edadOriginal <= 21;
        const edadAhoraAdulta = nuevaEdad > 21;
    
        // ① Creamos (o reutilizamos) el input oculto que dirá al backend si ya preguntamos
        let confirmInput = document.querySelector('input[name="confirmar_actualizacion_categoria"]');
        if (!confirmInput) {
            confirmInput = document.createElement("input");
            confirmInput.type  = "hidden";
            confirmInput.name  = "confirmar_actualizacion_categoria";
            confirmInput.value = "";                 // se rellenará más abajo
            document.getElementById("usuarioForm").appendChild(confirmInput);
        }
    
        // ② Si NO hay salto de menor → adulto, limpiamos la marca y salimos
        if (!(edadEraSub21 && edadAhoraAdulta)) {
            confirmInput.value = "";
            return;
        }
    
        // ③ Hay salto a adulto: preguntamos
        const categoriaSugerida = calcularCategoria(nuevaEdad);  // null para adultos
        const msg = categoriaSugerida
            ? `La edad ingresada sugiere la categoría "${categoriaSugerida}". ¿Deseas asignarla automáticamente?`
            : "El usuario ahora es mayor de 21 años. ¿Deseas actualizar su categoría al nivel seleccionado?";
    
        const confirmar = confirm(msg);
    
        if (confirmar) {
            confirmInput.value = "si";          // ✔️ el backend podrá validarlo
            // si hay categoría automática (< 22) la aplicamos aquí
            if (categoriaSugerida) {
                for (const opt of categoriaSelect.options) {
                    if (opt.text.toLowerCase() === categoriaSugerida) {
                        categoriaSelect.value = opt.value;
                        break;
                    }
                }
            }
        } else {
            confirmInput.value = "no";
        }
    }
    

    if (fechaNacimiento) {
        edadOriginal = calcularEdad(fechaNacimiento.value);
        fechaNacimiento.addEventListener("change", function () {
            const partes = fechaNacimiento.value.split("-");
            if (partes.length === 3) {
                const year = parseInt(partes[0], 10);
                if (year >= 1900 && year <= 2100) {
                    updateFieldsVisibility();
                    verificarCambioEdad();
                }
            }
        });
        
        
    }

    if (rolSelect) {
        rolSelect.addEventListener("change", updateFieldsVisibility);
    }

    setTimeout(updateFieldsVisibility, 0);

    // ---------------------------------------------
    // VALIDACIONES EN CREACIÓN (MODO ADMIN)
    // ---------------------------------------------
    const form = document.getElementById("usuarioForm");
    const isCreateMode = !window.location.pathname.includes("/edit/");

    if (form && isCreateMode) {
        form.addEventListener("submit", function (e) {
        const rol = document.getElementById("id_rol")?.value;

        // Siempre requeridos
        const nombre = document.getElementById("id_nombre")?.value.trim();
        const apellidos = document.getElementById("id_apellidos")?.value.trim();
        const correo = document.getElementById("id_correo")?.value.trim();
        const telefono = document.getElementById("id_telefono")?.value.trim();
        const password = document.getElementById("id_password")?.value;

        // Solo para miembro o entrenador
        const tipoDocumento = document.getElementById("id_tipo_documento")?.value;
        const numDocumento = document.getElementById("id_num_documento")?.value.trim();

        // Solo para miembro
        const fechaNacimiento = document.getElementById("id_fecha_nacimiento")?.value;
        const nivel = document.getElementById("id_nivel")?.value;

        const isMiembro = rol === "miembro";
        const isEntrenador = rol === "entrenador";
        const isAdmin = rol === "admin";

        // Validar campos comunes
        if (!nombre || !apellidos || !correo || !password) {
            e.preventDefault();
            alert("Por favor, complete los campos obligatorios.");
            return false;
        }

        // VALIDAR NOMBRE: Solo letras, espacios y acentos
        const nyaPattern = /^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\s]+$/;
        if (!nyaPattern.test(nombre)) {
            e.preventDefault();
            alert("El nombre solo puede contener letras y espacios.");
            return false;
        }
        if (!nyaPattern.test(apellidos)) {
            e.preventDefault();
            alert("Los apellidos solo pueden contener letras y espacios.");
            return false;
        }

        // Validar correo
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(correo)) {
            e.preventDefault();
            alert("Ingrese un correo electrónico válido.");
            return false;
        }


        // ───────── Validaciones adicionales para ENTRENADOR o MIEMBRO ─────────
        if (isMiembro || isEntrenador) {

            // Teléfono obligatorio y numérico
            if (!telefono) {
                e.preventDefault();
                alert("El teléfono es obligatorio para entrenadores y miembros.");
                return false;
            }
            
            const numberPattern = /^[0-9]+$/;
            if (!numberPattern.test(telefono)) {
                e.preventDefault();
                alert("El teléfono debe contener solo números.");
                return false;
            }

            // Documento obligatorio y numérico
            if (!tipoDocumento || !numDocumento) {
                e.preventDefault();
                alert("Debe completar tipo y número de documento.");
                return false;
            }
            if (!numberPattern.test(numDocumento)) {
                e.preventDefault();
                alert("El número de documento debe contener solo números.");
                return false;
            }
        }


        // Validaciones específicas para miembro
        if (isMiembro) {
            if (!fechaNacimiento) {
                e.preventDefault();
                alert("Debe ingresar la fecha de nacimiento.");
                return false;
            }

            const birthYear = parseInt(fechaNacimiento.split("-")[0], 10);
            const currentYear = new Date().getFullYear();
            const edad = currentYear - birthYear;

            if (isNaN(edad) || edad < 5 || edad > 116) {
                e.preventDefault();
                alert("La edad debe estar entre 5 y 116 años.");
                return false;
            }

            if (edad > 21 && !nivel) {
                e.preventDefault();
                alert("Debe seleccionar el nivel de juego para mayores de 21 años.");
                return false;
            }
        }
    });


    }

});
