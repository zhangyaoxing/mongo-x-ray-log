document.addEventListener('DOMContentLoaded', function() {
    var bar_labels = [];
    var count = [];
    var avg_slow_ms = [];
    data.forEach(d => {
        bar_labels.push(d.time);
        count.push(d.count);
        avg_slow_ms.push(d.total_slow_ms / d.count);
    });

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    wrapper.className = 'bar';
    canvas.className = 'bar';
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bar_labels,
            datasets: [
                {
                    label: 'Slow Count',
                    data: count,
                    type: 'bar',
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    yAxisID: 'y'
                },
                {
                    label: 'Avg Slow (ms)',
                    data: avg_slow_ms,
                    type: 'line',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
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
                    title: { display: true, text: 'Count' }
                },
                y1: {
                    beginAtZero: true,
                    position: 'right',
                    title: { display: true, text: 'Avg Slow (ms)' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });
    charts.push(chart);

    let resetButton = null;
    for (let el = container; el; el = el.previousElementSibling) {
        if (el.tagName === 'INPUT' && el.id.indexOf('reset_') === 0) {
            resetButton = el;
            break;
        }
    }
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            chart.resetZoom();
        });
    }
});
