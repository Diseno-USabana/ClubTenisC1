// proyecto/static/usuarios/js/login.js
document.addEventListener("DOMContentLoaded", function() {
    var form = document.getElementById("authForm");
    if (!form) return;
    
    form.addEventListener("submit", function(e) {
        // Solo se realizan las validaciones si se trata del registro
        var headingText = document.querySelector("h2").innerText.toLowerCase();
        if (headingText.includes("registro")) {
            // Obtener los campos del formulario
            var nombre = form.querySelector('input[name="nombre"]');
            var apellidos = form.querySelector('input[name="apellidos"]');
            var telefono = form.querySelector('input[name="telefono"]');
            var correo = form.querySelector('input[name="correo"]');
            var password = form.querySelector('input[name="password"]');
            var passwordConfirm = form.querySelector('input[name="password_confirm"]');
            var tipoDocumento = form.querySelector('[name="tipo_documento"]');
            var numDocumento = form.querySelector('input[name="num_documento"]');
            var fechaNacimiento = form.querySelector('input[name="fecha_nacimiento"]');

            // Validar que todos los campos estén llenos
            if (!nombre.value || !apellidos.value || !telefono.value || !correo.value ||
                !password.value || !passwordConfirm.value || !tipoDocumento.value ||
                !numDocumento.value || !fechaNacimiento.value) {
                e.preventDefault();
                alert("Por favor, complete todos los campos.");
                return false;
            }

            // Validar correo con formato correcto
            var emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(correo.value)) {
                e.preventDefault();
                alert("Por favor, ingrese un correo electrónico válido.");
                return false;
            }

            // Validar que teléfono y número de documento contengan solo números
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
        }
    });
});
