document.addEventListener('DOMContentLoaded', function() {
    const labels = data.map(d => d.time);
    const ipSet = new Set();
    data.forEach(d => Object.keys(d.byIp).forEach(ip => ipSet.add(ip)));
    const ips = Array.from(ipSet);

    const datasets_byip = [];
    ips.forEach(ip => {
        // created
        datasets_byip.push({
            label: ip + ' created',
            data: data.map(d => d.byIp[ip]?.created || 0),
            stack: "Stack 0"
        });
        // ended
        datasets_byip.push({
            label: ip + ' ended',
            data: data.map(d => -(d.byIp[ip]?.ended || 0)),
            stack: "Stack 0"
        });
    });

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const displayLegend = datasets_byip.length <= MAX_LEGENDS;
    const chart2 = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets_byip.map(ds => ({
                label: ds.label,
                data: ds.data,
                type: 'bar',
                stack: ds.stack
            }))
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Connections Created/Ended by IP Over Time'
                },
                legend: {
                    position: 'top',
                    display: displayLegend,
                    labels: {
                        usePointStyle: true,
                        generateLabels: genDefaultLegendLabels
                    }
                },
                zoom: ZOOM_OPTIONS
            },
            responsive: true,
            animation: {
                duration: ANIMATION_DURATION
            },
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: { display: true, text: 'Connections' }
                }
            }
        }
    });
    charts.push(chart2);

    let resetButton = null;
    for (let el = container; el; el = el.previousElementSibling) {
        if (el.tagName === 'INPUT' && el.id.indexOf('reset_') === 0) {
            resetButton = el;
            break;
        }
    }
    if (resetButton) {
        resetButton.addEventListener('click', function () {
            chart2.resetZoom();
        });
    }
});
