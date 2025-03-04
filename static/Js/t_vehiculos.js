function openModal(vehiclePlate, currentState) {
    document.getElementById('vehicle_plate').value = vehiclePlate;
    document.getElementById('current_state').value = currentState;
    document.getElementById('questionnaireModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('questionnaireModal').style.display = 'none';
}