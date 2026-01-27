function crearGraficoInventario(nombres, stock) {
    const ctx = document.getElementById('graficoInventario').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: nombres,
            datasets: [{
                label: 'Stock Actual',
                data: stock,
                backgroundColor: stock.map(valor => valor < 5 ? '#e74c3c' : '#2ecc71'),
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Inventario de Productos'
                }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function crearGraficoVentas(clientes, subtotales) {
    const ctx = document.getElementById('graficoVentasClientes').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: clientes,
            datasets: [{
                label: 'Subtotal por Cliente',
                data: subtotales,
                backgroundColor: [
                    '#3498db', '#2ecc71', '#f1c40f', '#e67e22', '#9b59b6', '#e74c3c'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Distribución de Ventas por Cliente'
                }
            }
        }
    });
}

function crearGraficoVentasPorProducto(productosGrafico, subtotalesGrafico) {
    const ctx = document.getElementById("graficoVentas").getContext("2d");
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: productosGrafico,
            datasets: [{
                label: "Ventas por producto",
                data: subtotalesGrafico,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}
