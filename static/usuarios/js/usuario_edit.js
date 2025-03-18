// usuarios/js/usuario_edit.js
document.addEventListener('DOMContentLoaded', function () {
    const roleSelect = document.querySelector('#id_rol');
    const adminFields = document.getElementById('admin-fields');
    const entrenadorFields = document.getElementById('entrenador-fields');
    const miembroFields = document.getElementById('miembro-fields');

    function updateFormFields() {
        const selectedRole = roleSelect.value;
        // Ocultar todos los bloques inicialmente
        if (adminFields) adminFields.style.display = 'none';
        if (entrenadorFields) entrenadorFields.style.display = 'none';
        if (miembroFields) miembroFields.style.display = 'none';

        // Mostrar el bloque correspondiente
        if (selectedRole === 'admin') {
            if (adminFields) adminFields.style.display = 'block';
        } else if (selectedRole === 'entrenador') {
            if (entrenadorFields) entrenadorFields.style.display = 'block';
        } else if (selectedRole === 'miembro') {
            if (miembroFields) miembroFields.style.display = 'block';
        }
    }

    if (roleSelect) {
        roleSelect.addEventListener('change', updateFormFields);
        // Ejecutar al cargar para mostrar el bloque correcto
        updateFormFields();
    }
});
