document.addEventListener('DOMContentLoaded', function () {
    const deleteButton = document.querySelector('.delete-btn');
    const modal = document.getElementById('deleteModal');
    const closeButton = document.querySelector('.close');
    const cancelButton = document.querySelector('.cancel-delete');


    deleteButton.addEventListener('click', function (event) {
        event.preventDefault();
        modal.style.display = 'block';
    });


    closeButton.addEventListener('click', function () {
        modal.style.display = 'none';
    });


    cancelButton.addEventListener('click', function () {
        modal.style.display = 'none';
    });


    window.addEventListener('click', function (event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
