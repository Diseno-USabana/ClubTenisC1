document.addEventListener("DOMContentLoaded", function () {
  const conceptoSelect = document.getElementById("id_concepto");
  const montoInput = document.getElementById("id_monto");
  const anioField = document.getElementById("field-anio");
  const mesField = document.getElementById("field-mes");
  const anioInput = document.getElementById("id_anio");
  const mesInput = document.getElementById("id_mes");
  const fechaInput = document.getElementById("id_fecha");

  const alertContainer = document.createElement("div");
  alertContainer.className = "alert alert-danger mt-3";
  alertContainer.style.display = "none";
  document.querySelector("form").prepend(alertContainer);

  function showAlert(message) {
    alertContainer.textContent = message;
    alertContainer.style.display = "block";
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function updateFields() {
    const selectedConcept = conceptoSelect.value;

    if (selectedConcept === "mensualidad") {
      montoInput.value = 170000;
      anioField.style.display = "block";
      mesField.style.display = "block";
    } else if (selectedConcept === "torneo") {
      montoInput.value = "";
      anioField.style.display = "none";
      mesField.style.display = "none";
      anioInput.value = "";
      mesInput.value = "";
    } else if (selectedConcept === "matricula") {
      montoInput.value = 100000;
      anioField.style.display = "none";
      mesField.style.display = "none";
      anioInput.value = "";
      mesInput.value = "";
    }
  }

  if (conceptoSelect) {
    conceptoSelect.addEventListener("change", updateFields);
    updateFields();
  }

  const form = document.getElementById("usuarioForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      alertContainer.style.display = "none";
      const concepto = conceptoSelect.value;
      const monto = parseFloat(montoInput.value);
      const anio = parseInt(anioInput?.value);
      const mes = parseInt(mesInput?.value);
      const fecha = new Date(fechaInput.value);
      const hoy = new Date();

      if (!concepto) {
        e.preventDefault();
        showAlert("Debes seleccionar un concepto de pago.");
        return;
      }

      if (!fechaInput.value) {
        e.preventDefault();
        showAlert("Debes seleccionar una fecha de pago.");
        return;
      }

      if (fecha > hoy) {
        e.preventDefault();
        showAlert("La fecha no puede ser en el futuro.");
        return;
      }

      if (isNaN(monto) || monto <= 0) {
        e.preventDefault();
        showAlert("El monto debe ser un número válido y mayor a cero.");
        return;
      }

      if (monto > 1000000) {
        e.preventDefault();
        showAlert("El monto no puede exceder $1.000.000.");
        return;
      }

      if (concepto === "mensualidad") {
        if (monto !== 170000) {
          e.preventDefault();
          showAlert("El monto para mensualidad debe ser exactamente $170.000.");
          return;
        }
        if (!anio || !mes) {
          e.preventDefault();
          showAlert("Debes seleccionar año y mes para el pago de mensualidad.");
          return;
        }
        if (mes < 1 || mes > 12) {
          e.preventDefault();
          showAlert("El mes debe estar entre 1 y 12.");
          return;
        }
        const anioActual = hoy.getFullYear();
        if (anio < anioActual - 1 || anio > anioActual + 1) {
          e.preventDefault();
          showAlert("El año de pago debe estar dentro del rango válido (año actual ±1).");
          return;
        }
      }

      if (concepto === "matricula" && monto !== 100000) {
        e.preventDefault();
        showAlert("El monto para matrícula debe ser exactamente $100.000.");
        return;
      }

      if (concepto === "torneo") {
        if (monto <= 0) {
          e.preventDefault();
          showAlert("El monto para el torneo debe ser mayor a 0.");
          return;
        }
        if (monto < 10000) {
          e.preventDefault();
          showAlert("El monto para torneo debe ser al menos $10.000.");
          return;
        }
      }
    });
  }
});