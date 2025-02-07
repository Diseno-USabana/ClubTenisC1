// Validación básica del formulario
document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    form.addEventListener('submit', function (e) {
        let valid = true;
        const correo = document.querySelector('input[name="correo"]');
        const telefono = document.querySelector('input[name="telefono"]');
        const num_documento = document.querySelector('input[name="num_documento"]');
        
        // Validación del correo electrónico
        if (!correo.value.match(/^[^@]+@[^@]+\.[^@]+$/)) {
            alert('Por favor, introduce un correo electrónico válido.');
            valid = false;
        }

        // Validación del teléfono (solo números)
        if (!telefono.value.match(/^\d+$/)) {
            alert('El teléfono solo debe contener números.');
            valid = false;
        }

        // Validación del número de documento (solo números)
        if (!num_documento.value.match(/^\d+$/)) {
            alert('El número de documento solo debe contener números.');
            valid = false;
        }

        if (!valid) {
            e.preventDefault(); // Detener la presentación del formulario si la validación falla
        }
    });
});
