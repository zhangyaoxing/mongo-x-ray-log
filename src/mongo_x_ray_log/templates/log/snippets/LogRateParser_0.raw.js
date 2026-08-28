document.addEventListener('DOMContentLoaded', function() {
    const allTimesSet = new Set();
    data.forEach(entry => {
        entry.buckets.forEach(b => allTimesSet.add(b.time));
    });
    // Collect all unique timestamps (sorted) across all entries
    const allTimes = Array.from(allTimesSet).sort();

    // Build one dataset per entry (colors assigned automatically by Chart.js)
    const datasets = data.map((entry) => {
        const bucketMap = {
            count: 0
        };
        entry.buckets.forEach(b => {
            bucketMap.count += b.count;
            bucketMap[b.time] = b.count;
        });
        return {
            label: `[${entry.id}] ${entry.sample.msg}`,
            data: allTimes.map(t => bucketMap[t] || 0),
            fill: false,
            tension: 0.3,
            pointRadius: 2
        };
    });
    // Sort by total count (descending)
    datasets.sort((a, b) => b.data.reduce((sum, val) => sum + val, 0) - a.data.reduce((sum, val) => sum + val, 0));

    let wrapper = document.createElement('div');
    let canvas = document.createElement('canvas');
    wrapper.className = 'bar';
    canvas.className = 'bar';
    container.appendChild(wrapper);
    wrapper.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allTimes,
            datasets: datasets
        },
        options: {
            responsive: true,
            animation: { duration: ANIMATION_DURATION },
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
                x: {
                    title: { display: true, text: 'Time' }
                },
                y: {
                    beginAtZero: true,
                    title: { display: true, text: 'Count' }
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
