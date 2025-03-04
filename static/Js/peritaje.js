function filterVehicles() {
    var input = document.getElementById("searchInput");
    var filter = input.value.trim().toUpperCase();
    var container = document.getElementById("vehicleContainer");
    var cards = container.getElementsByClassName("vehiculo-card"); // Corregido aquí

    for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var placaElement = card.querySelector(".data-placa");
        var reservaElement = card.querySelector(".data-reserva");

        var placa = placaElement ? placaElement.textContent.replace("Matricula:", "").trim().toUpperCase() : "";
        var reserva = reservaElement ? reservaElement.textContent.replace("Numero de reserva:", "").trim().toUpperCase() : "";

        if (placa.startsWith(filter) || reserva.startsWith(filter)) { 
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    }
}
