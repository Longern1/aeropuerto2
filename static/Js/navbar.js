const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

// Abrir/cerrar el menú al hacer clic en el icono de hamburguesa
hamburger.addEventListener('click', (e) => {
    e.stopPropagation(); // Evita que el clic se propague al documento
    navLinks.classList.toggle('active');
});

// Cerrar el menú si se hace clic fuera del navbar
document.addEventListener('click', (e) => {
    if (!navLinks.contains(e.target) && !hamburger.contains(e.target)) {
        navLinks.classList.remove('active');
    }
});
