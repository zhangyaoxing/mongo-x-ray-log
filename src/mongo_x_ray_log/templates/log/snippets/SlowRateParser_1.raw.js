document.addEventListener('DOMContentLoaded', function() {
    var nsCount = {};
    data.forEach(d => {
        Object.entries(d.byNs).forEach(([ns, val]) => {
            nsCount[ns] = (nsCount[ns] || 0) + (val.count || 0);
        });
    });

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    wrapper.className = 'pie100';
    canvas.className = 'pie100';
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const chart2 = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(nsCount),
            datasets: [{
                data: Object.values(nsCount)
            }]
        },
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Slow Count by Namespace'
                }
            }
        }
    });
    charts.push(chart2);
});
