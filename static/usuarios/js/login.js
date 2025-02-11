// proyecto/static/usuarios/js/login.js
document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("authForm");
    if (!form) return;
    
    form.addEventListener("submit", function(e) {
        // Solo se ejecuta la validación si es registro
        var headingText = document.querySelector("h2").innerText.toLowerCase();
        if (headingText.includes("registro")) {
            // Obtener campos
            var nombre = form.querySelector('input[name="nombre"]');
            var apellidos = form.querySelector('input[name="apellidos"]');
            var telefono = form.querySelector('input[name="telefono"]');
            var correo = form.querySelector('input[name="correo"]');
            var password = form.querySelector('input[name="password"]');
            var passwordConfirm = form.querySelector('input[name="password_confirm"]');
            var tipoDocumento = form.querySelector('[name="tipo_documento"]');
            var numDocumento = form.querySelector('input[name="num_documento"]');
            var fechaNacimiento = form.querySelector('input[name="fecha_nacimiento"]');
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
            
            // Calcular edad para saber si se requiere el nivel de juego
            var today = new Date();
            var birthDate = new Date(fechaNacimiento.value);
            var age = today.getFullYear() - birthDate.getFullYear();
            var m = today.getMonth() - birthDate.getMonth();
            if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
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
