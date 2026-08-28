document.addEventListener('DOMContentLoaded', function() {
    var nsSlowMs = {};
    data.forEach(d => {
        Object.entries(d.byNs).forEach(([ns, val]) => {
            nsSlowMs[ns] = (nsSlowMs[ns] || 0) + (val.total_slow_ms || 0);
        });
    });

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    wrapper.className = 'pie100';
    canvas.className = 'pie100';
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const chart3 = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(nsSlowMs),
            datasets: [{
                data: Object.values(nsSlowMs)
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Slow MS by Namespace'
                }
            }
        }
    });
    charts.push(chart3);
});
