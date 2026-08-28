document.addEventListener('DOMContentLoaded', function() {
    const groupedDataDuration = {};
    const groupedDataScanned = {};
    const groupedDataScannedObj = {};
    data.forEach((item, i) => {
        const namespace = item.attr.ns || '(unknown)';
        if (!groupedDataDuration[namespace]) {
            groupedDataDuration[namespace] = [];
            groupedDataScanned[namespace] = [];
            groupedDataScannedObj[namespace] = [];
        }

        const timestamp = new Date(item.t);
        groupedDataDuration[namespace].push({
            index: i,
            x: timestamp.getTime(),
            y: item.attr.durationMillis,
            timeLabel: timestamp.toLocaleTimeString()
        });
        groupedDataScanned[namespace].push({
            index: i,
            x: timestamp.getTime(),
            y: item.attr.keysExamined || 0,
            timeLabel: timestamp.toLocaleTimeString()
        });
        groupedDataScannedObj[namespace].push({
            index: i,
            x: timestamp.getTime(),
            y: item.attr.docsExamined || 0,
            timeLabel: timestamp.toLocaleTimeString()
        });
    });

    const dssDuration = Object.keys(groupedDataDuration).map((namespace) => {
        const backgroundColor = generateRandomColor(0.8);
        const borderColor = generateRandomColor(1);

        return {
            label: namespace,
            data: groupedDataDuration[namespace],
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            borderWidth: 1,
            pointRadius: 4
        };
    });

    const dssScanned = Object.keys(groupedDataScanned).map((namespace) => {
        const backgroundColor = generateRandomColor(0.8);
        const borderColor = generateRandomColor(1);

        return {
            label: namespace,
            data: groupedDataScanned[namespace],
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            borderWidth: 1,
            pointRadius: 4
        };
    });

    const dssScannedObj = Object.keys(groupedDataScannedObj).map((namespace) => {
        const backgroundColor = generateRandomColor(0.8);
        const borderColor = generateRandomColor(1);

        return {
            label: namespace,
            data: groupedDataScannedObj[namespace],
            backgroundColor: backgroundColor,
            borderColor: borderColor,
            borderWidth: 1,
            pointRadius: 4
        };
    });

    let highlighted = -1;
    function onClick(event, activeElements) {
        if (activeElements.length > 0) {
            const datasetIndex = activeElements[0].datasetIndex;
            const dataIndex = activeElements[0].index;
            const dataset = this.data.datasets[datasetIndex];
            const dataPoint = dataset.data[dataIndex];
            const originalData = data[dataPoint.index];

            if (highlighted === dataPoint.index) {
                code.textContent = '// Click data points to review original log line...';
                highlighted = -1;
            } else {
                code.textContent = JSON.stringify(originalData, null, 2);
                highlighted = dataPoint.index;
            }
            delete code.dataset.highlighted;
            hljs.highlightElement(code);
            code.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Build the links, canvases and the sample viewer inside the container
    const links = document.createElement('div');
    const linkItems = [
        { text: 'Duration Chart', id: 'duration' },
        { text: 'Scanned Chart', id: 'scanned' },
        { text: 'Scanned Objects Chart', id: 'scannedObj' }
    ];
    linkItems.forEach((item, index) => {
        const link = document.createElement('a');
        link.href = '#' + item.id;
        link.textContent = item.text;
        if (index > 0) {
            links.appendChild(document.createTextNode(' | '));
        }
        links.appendChild(link);
    });
    container.appendChild(links);

    const wrappers = [];
    const canvases = [];
    linkItems.forEach(item => {
        const wrapper = document.createElement('div');
        const canvas = document.createElement('canvas');
        canvas.height = 200;
        wrapper.appendChild(canvas);
        container.appendChild(wrapper);
        wrappers.push(wrapper);
        canvases.push(canvas);
        canvas.id = 'canvas_' + item.id;
    });
    canvases[1].style.display = 'none';
    canvases[2].style.display = 'none';

    // Sample viewer
    const samplePre = document.createElement('pre');
    const code = document.createElement('code');
    code.className = 'language-json';
    samplePre.appendChild(code);
    container.appendChild(samplePre);
    hljs.highlightElement(code);

    const configDuration = {
        type: 'scatter',
        data: {
            datasets: dssDuration
        },
        options: {
            responsive: true,
            animation: {
                duration: ANIMATION_DURATION
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Slow Operations - Duration vs Time by Namespace'
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        generateLabels: genDefaultLegendLabels
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            const point = context[0].raw;
                            return new Date(point.x).toISOString();
                        },
                        label: function (context) {
                            const point = context.raw;
                            return [
                                `Namespace: ${context.dataset.label}`,
                                `Duration: ${point.y}ms`,
                                `Time: ${new Date(point.x).toISOString()}`
                            ];
                        }
                    }
                },
                zoom: ZOOM_OPTIONS
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        callback: function (t) {
                            const date = new Date(t);
                            const timeStr = date.toISOString().match(/(?<=T)[^\.Z]+/)[0];
                            return timeStr;
                        },
                        maxTicksLimit: 10
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Duration (milliseconds)'
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                mode: 'point',
                intersect: false
            },
            onClick: onClick
        }
    };
    const configScanned = {
        type: 'scatter',
        data: {
            datasets: dssScanned
        },
        options: {
            responsive: true,
            animation: {
                duration: ANIMATION_DURATION
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Slow Operations - Scanned vs Time by Namespace'
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        generateLabels: genDefaultLegendLabels
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            const point = context[0].raw;
                            return new Date(point.x).toISOString();
                        },
                        label: function (context) {
                            const point = context.raw;
                            return [
                                `Namespace: ${context.dataset.label}`,
                                `Scanned: ${point.y}`,
                                `Time: ${new Date(point.x).toISOString()}`
                            ];
                        }
                    }
                },
                zoom: ZOOM_OPTIONS
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        callback: function (t) {
                            const date = new Date(t);
                            const timeStr = date.toISOString().match(/(?<=T)[^\.Z]+/)[0];
                            return timeStr;
                        },
                        maxTicksLimit: 10
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Scanned Keys'
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                mode: 'point',
                intersect: false
            },
            onClick: onClick
        }
    };

    const configScannedObj = {
        type: 'scatter',
        data: {
            datasets: dssScannedObj
        },
        options: {
            responsive: true,
            animation: {
                duration: ANIMATION_DURATION
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Slow Operations - Scanned Objects vs Time by Namespace'
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        generateLabels: genDefaultLegendLabels
                    }
                },
                tooltip: {
                    callbacks: {
                        title: function (context) {
                            const point = context[0].raw;
                            return new Date(point.x).toISOString();
                        },
                        label: function (context) {
                            const point = context.raw;
                            return [
                                `Namespace: ${context.dataset.label}`,
                                `Scanned Obj: ${point.y}`,
                                `Time: ${new Date(point.x).toISOString()}`
                            ];
                        }
                    }
                },
                zoom: ZOOM_OPTIONS
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    ticks: {
                        callback: function (t) {
                            const date = new Date(t);
                            const timeStr = date.toISOString().match(/(?<=T)[^\.Z]+/)[0];
                            return timeStr;
                        },
                        maxTicksLimit: 10
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Scanned Objects'
                    },
                    beginAtZero: true
                }
            },
            interaction: {
                mode: 'point',
                intersect: false
            },
            onClick: onClick
        }
    };

    const chart1 = new Chart(canvases[0].getContext('2d'), configDuration);
    charts.push(chart1);
    const chart2 = new Chart(canvases[1].getContext('2d'), configScanned);
    charts.push(chart2);
    const chart3 = new Chart(canvases[2].getContext('2d'), configScannedObj);
    charts.push(chart3);

    const linkElements = links.getElementsByTagName('a');
    linkElements[0].classList.add('in-view');
    for (let i = 0; i < linkElements.length; i++) {
        const link = linkElements[i];
        link.addEventListener('click', function (event) {
            event.preventDefault();
            // Hide all canvases first
            for (let j = 0; j < linkElements.length; j++) {
                const canvas = canvases[j];
                canvas.style.display = "none";
                linkElements[j].classList.remove('in-view');
            }
            const index = Array.prototype.indexOf.call(linkElements, this);
            canvases[index].style.display = "block";
            this.classList.add('in-view');
        });
    }

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
            chart2.resetZoom();
            chart3.resetZoom();
        });
    }
});
