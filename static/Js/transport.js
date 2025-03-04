
function openModal(vehicleId, placa) {
    const modal = document.getElementById(`confirmationModal${vehicleId}`);
    const message = document.getElementById(`confirmationMessage${vehicleId}`);


    message.textContent = `¿Estás seguro de que deseas seleccionar el vehículo con la matrícula ${placa}?`;


    modal.style.display = 'block';


    modal.addEventListener('click', function (event) {
        if (event.target === modal) {
            closeModal(vehicleId);
        }
    });


    window.addEventListener('scroll', () => closeModal(vehicleId), { once: true });
}


function closeModal(vehicleId) {
    const modal = document.getElementById(`confirmationModal${vehicleId}`);
    if (modal) {
        modal.style.display = 'none';
    }


    window.removeEventListener('scroll', () => closeModal(vehicleId));
}


function confirmAction(vehicleId) {
    const form = document.getElementById(`vehicleForm${vehicleId}`);
    if (form) {
        form.submit();
    }
    closeModal(vehicleId);
}



function buscarVuelo(numeroVuelo) {
    let url = `https://www.google.com/search?q=${encodeURIComponent(numeroVuelo + " estado de vuelo")}`;
    window.open(url, "_blank"); // Abrir en nueva pestaña
}



