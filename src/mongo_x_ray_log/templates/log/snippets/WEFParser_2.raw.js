document.addEventListener('DOMContentLoaded', function() {
    // Find the sample code block and the table that precede this container.
    // Note: addTableCopyButtons() may wrap the table in a table-copy-wrapper div.
    let sample = null;
    let table = null;
    for (let el = container.previousElementSibling; el; el = el.previousElementSibling) {
        if (!sample && el.tagName === 'PRE' && el.querySelector('code')) {
            sample = el.querySelector('code');
        }
        if (!table && (el.tagName === 'TABLE' || el.querySelector('table'))) {
            table = el.tagName === 'TABLE' ? el : el.querySelector('table');
        }
        if (sample && table) {
            break;
        }
    }
    if (!sample || !table) {
        return;
    }
    hljs.highlightElement(sample);
    const anchors = table.getElementsByTagName('a');
    let highlighted = -1;
    for (let i = 0; i < anchors.length; i++) {
        anchors[i].addEventListener('click', function (event) {
            event.preventDefault();
            const index = this.getAttribute('href').substring(1);
            const row = data[index];
            if (highlighted == index) {
                sample.textContent = "// Click error code to review sample log line...";
                highlighted = -1;
            } else {
                sample.textContent = JSON.stringify(row.sample, null, 2);
                if (row.ai_analysis) {
                    sample.textContent += "\n\n// AI Analysis: \n";
                    const analysis = row.ai_analysis.split(/(?<=[\n.!;])\W+/).map(line => "// " + line).join("\n");
                    sample.textContent += analysis;
                }
                highlighted = index;
            }
            delete sample.dataset.highlighted;
            hljs.highlightElement(sample);
            sample.scrollIntoView({
                behavior: "smooth"
            });
        });
    }
});
