document.addEventListener('DOMContentLoaded', function() {
    var labels = [];
    var created = [];
    var ended = [];
    var total = [];
    data.forEach(d => {
        labels.push(d.time);
        created.push(d.created);
        ended.push(-d.ended);
        total.push(d.total);
    });

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const chart1 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Connections Created',
                    data: created,
                    type: 'bar',
                    stack: 'Stack 0',
                    backgroundColor: 'rgba(54, 162, 235, 0.7)'
                },
                {
                    label: 'Connections Ended',
                    data: ended,
                    type: 'bar',
                    stack: 'Stack 0',
                    backgroundColor: 'rgba(255, 99, 132, 0.7)'
                },
                {
                    label: 'Total Connections',
                    data: total,
                    type: 'line',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    fill: false,
                    yAxisID: 'y1',
                    tension: 0.3,
                    pointRadius: 2
                }
            ]
        },
        options: {
            responsive: true,
            animation: {
                duration: ANIMATION_DURATION
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Connection Create/Ended Rate Over Time'
                },
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        generateLabels: genDefaultLegendLabels
                    }
                },
                zoom: ZOOM_OPTIONS
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Connections per minute' }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    title: { display: true, text: 'Total Connections' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
    charts.push(chart1);

    let resetButton = null;
    for (let el = container; el; el = el.previousElementSibling) {
        if (el.tagName === 'INPUT' && el.id.indexOf('reset_') === 0) {
            resetButton = el;
            break;
        }
    }
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            chart1.resetZoom();
        });
    }
});
