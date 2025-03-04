
function filterVehicles() {
    var input = document.getElementById("searchInput");
    var filter = input.value.trim().toUpperCase();
    var container = document.getElementById("vehicleContainer");
    var cards = container.getElementsByClassName("vehicle-card");

    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var placaElement = card.querySelector(".data-placa");
        var reservaElement = card.querySelector(".data-reserva");

        var placa = placaElement ? placaElement.textContent.trim().toUpperCase() : "";
        var reserva = reservaElement ? reservaElement.textContent.trim().toUpperCase() : "";

        if (placa.startsWith(filter) || reserva.startsWith(filter)) { 
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}





// Función para abrir el modal de detalles
function openModal(vehicleId) {
    var modal = document.getElementById('vehicleModal-' + vehicleId);
    modal.style.display = "flex"; // Muestra el modal
    modal.style.opacity = 1; // Aplica la transición de desvanecimiento
}

// Función para cerrar el modal
function closeModal(vehicleId) {
    var modal = document.getElementById('vehicleModal-' + vehicleId);
    modal.style.opacity = 0; // Aplica la transición de desvanecimiento
    setTimeout(function() {
        modal.style.display = "none"; // Oculta el modal después de la animación
    }, 300);
}

// Cerrar el modal si se hace clic fuera del área de detalles
window.addEventListener('click', function(event) {
    var modals = document.querySelectorAll('.vehicle-modal');
    modals.forEach(function(modal) {
        if (event.target === modal) {
            var vehicleId = modal.id.split('-')[1]; // Extrae el ID del vehículo
            closeModal(vehicleId); // Cierra el modal
        }
    });
});
