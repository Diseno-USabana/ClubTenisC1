document.addEventListener("DOMContentLoaded", function () {
    console.log("login.js loaded and executing.");

    var form = document.getElementById("authForm");
    if (!form) return;

    // Determinar si estamos en modo registro (buscando texto en el h2)
    var headingText = document.querySelector("h2").innerText.toLowerCase();
    var isRegistration = headingText.includes("únete") || headingText.includes("registro");
    console.log("Modo registro:", isRegistration);

    // Obtener el input de fecha de nacimiento y el contenedor del nivel de juego
    var fechaNacimiento = form.querySelector('input[name="fecha_nacimiento"]');
    var nivelContainer = document.getElementById("nivel-container");

    // Función para mostrar/ocultar el bloque de "Nivel" según la edad (calculada solo por año)
    function toggleNivelField() {
        console.log("Ejecutando toggleNivelField...");
        if (fechaNacimiento && nivelContainer) {
            var fechaVal = fechaNacimiento.value; // Se espera formato "YYYY-MM-DD"
            console.log("Valor de fecha_nacimiento:", fechaVal);
            if (fechaVal) {
                var parts = fechaVal.split("-");
                var birthYear = parseInt(parts[0], 10);
                var currentYear = new Date().getFullYear();
                var age = currentYear - birthYear;
                console.log("Edad calculada:", age);
                if (age >= 22) {
                    nivelContainer.style.display = "block";
                    console.log("Mostrando nivel-container");
                } else {
                    nivelContainer.style.display = "none";
                    console.log("Ocultando nivel-container");
                    var nivelField = nivelContainer.querySelector('select[name="nivel"]');
                    if (nivelField) {
                        nivelField.selectedIndex = 0;
                        console.log("Reiniciado nivel field");
                    }
                }
            } else {
                nivelContainer.style.display = "none";
                console.log("Sin valor en fecha_nacimiento, ocultando nivel-container");
            }
        }
    }
    
    if (isRegistration && fechaNacimiento && nivelContainer) {
        // Ejecutar al cargar la página y cuando se modifique la fecha
        toggleNivelField();
        fechaNacimiento.addEventListener("change", function () {
            console.log("Evento 'change' en fecha_nacimiento");
            toggleNivelField();
        });
        fechaNacimiento.addEventListener("input", function () {
            console.log("Evento 'input' en fecha_nacimiento");
            toggleNivelField();
        });
    }

    form.addEventListener("submit", function (e) {
        if (isRegistration) {
            var nombre = form.querySelector('input[name="nombre"]');
            var apellidos = form.querySelector('input[name="apellidos"]');
            var telefono = form.querySelector('input[name="telefono"]');
            var correo = form.querySelector('input[name="correo"]');
            var password = form.querySelector('input[name="password"]');
            var passwordConfirm = form.querySelector('input[name="password_confirm"]');
            var tipoDocumento = form.querySelector('[name="tipo_documento"]');
            var numDocumento = form.querySelector('input[name="num_documento"]');
            // fechaNacimiento ya está definida
            var nivel = form.querySelector('select[name="nivel"]'); // Puede existir o no

            // Verificar que los campos obligatorios estén llenos
            if (!nombre.value || !apellidos.value || !telefono.value || !correo.value ||
                !password.value || !passwordConfirm.value || !tipoDocumento.value ||
                !numDocumento.value || !fechaNacimiento.value) {
                e.preventDefault();
                alert("Por favor, complete todos los campos obligatorios.");
                return false;
            }

            // Validar formato de correo
            var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(correo.value)) {
                e.preventDefault();
                alert("Por favor, ingrese un correo electrónico válido.");
                return false;
            }

            // Validar que teléfono y número de documento sean solo números
            var numberPattern = /^[0-9]+$/;
            if (!numberPattern.test(telefono.value)) {
                e.preventDefault();
                alert("El teléfono debe contener solo números.");
                return false;
            }
            if (!numberPattern.test(numDocumento.value)) {
                e.preventDefault();
                alert("El número de documento debe contener solo números.");
                return false;
            }

            // Validar que las contraseñas coincidan
            if (password.value !== passwordConfirm.value) {
                e.preventDefault();
                alert("Las contraseñas no coinciden.");
                return false;
            }

            // Validar que la fecha de nacimiento es válida
            var dob = new Date(fechaNacimiento.value);
            if (isNaN(dob.getTime())) {
                e.preventDefault();
                alert("Ingrese una fecha de nacimiento válida.");
                return false;
            }

            // Calcular la edad usando solo el año
            var birthYear = parseInt(fechaNacimiento.value.split("-")[0], 10);
            var currentYear = new Date().getFullYear();
            var age = currentYear - birthYear;
            console.log("Edad en submit:", age);
            // Si es adulto (22 o más), el campo "nivel" es obligatorio
            if (age >= 22) {
                if (!nivel || !nivel.value) {
                    e.preventDefault();
                    alert("Debe seleccionar su nivel de juego para adultos.");
                    return false;
                }
            }
        }
    });
});
