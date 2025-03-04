


function editUser(id, name, email, role, password) {

    document.getElementById('editUserId').value = id;
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;
    document.getElementById('editPassword').value = password;
    document.getElementById('editRole').value = role;

    document.getElementById('editUserForm').style.display = 'block';
}





document.addEventListener("DOMContentLoaded", () => {
    const now = new Date();
    

    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    document.getElementById("date").value = `${day}/${month}/${year}`;
    

    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    document.getElementById("time").value = `${hours}:${minutes}`;
});


let formToSubmit = null;

function openConfirmModal(userName, form) {
    document.getElementById("confirmMessage").innerText = `¿Estás seguro de que deseas eliminar a ${userName}?`;
    document.getElementById("confirmModal").style.display = "flex";
    formToSubmit = form; // Guarda el formulario para enviarlo después
    return false; // Evita el envío inmediato del formulario
}

document.getElementById("confirmYes").addEventListener("click", function() {
    if (formToSubmit) formToSubmit.submit();
});

function closeConfirmModal() {
    document.getElementById("confirmModal").style.display = "none";
}