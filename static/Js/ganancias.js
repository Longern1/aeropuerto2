function cambiarFiltro() {
    let filtro = document.getElementById("filtro").value;
    let valorMes = document.getElementById("valorMes");
    let valorAnio = document.getElementById("valorAnio");

    if (filtro === "mes") {
        valorMes.style.display = "inline-block";
        valorAnio.style.display = "none";
        valorMes.value = "2025-01"; // Asegurar que el valor mínimo sea 2025
    } else {
        valorMes.style.display = "none";
        valorAnio.style.display = "inline-block";
        valorAnio.value = "2025"; // Asegurar que el valor mínimo sea 2025
    }
}