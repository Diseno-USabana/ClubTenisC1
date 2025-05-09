document.addEventListener('DOMContentLoaded', function () {
    const lista = document.getElementById('sortable-list');
    const inputHidden = document.getElementById('ordenIdsInput');

    new Sortable(lista, {
        animation: 150,
        onEnd: function () {
            const ids = Array.from(lista.children).map(li => li.dataset.id);
            inputHidden.value = ids.join(',');
        }
    });

    // Inicializar el valor al cargar
    const ids = Array.from(lista.children).map(li => li.dataset.id);
    inputHidden.value = ids.join(',');
});
