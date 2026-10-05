document.addEventListener('DOMContentLoaded', function() {
    const svg = document.getElementById('svg');
    const checkBtn = document.getElementById('checkBtn');
    const clearBtn = document.getElementById('clearBtn');
    const yInput = document.getElementById('y');
    const savedJson = document.getElementById('savedPointsJson');
    const rValueSpan = document.getElementById('rValue');
    let selectedR = null;

    const pixelsPerUnit = 40;
    const center = { x: 150, y: 150 };

    function setError(selector, message) {
        const element = document.querySelector(selector);
        const container = element.tagName === 'INPUT' ? element.parentNode : element;
        const existing = container.querySelector('.error-message');
        if (existing) existing.remove();

        if (message) {
            const error = document.createElement('div');
            error.className = 'error-message';
            error.textContent = message;
            container.appendChild(error);

            if (container.tagName === 'INPUT') {
                container.classList.add('error');
            }
        } else {
            if (container.tagName === 'INPUT') {
                container.classList.remove('error');
            }
        }
    }

    function drawAxisMarks(r) {
        const axisMarks = document.getElementById('axisMarks');
        axisMarks.innerHTML = '';
        if (!r) return;

        const marks = [
            {
                val: r, label: 'R'
            },
            {
                val: r/2, label: 'R/2'
            },
            {
                val: -r/2, label: '-R/2'
            },
            {
                val: -r, label: '-R'
            }
        ];

        marks.forEach(m => {
            const xPos = center.x + m.val * pixelsPerUnit;
            axisMarks.innerHTML += `
                <line x1="${xPos}" y1="145" x2="${xPos}" y2="155" stroke="#000720"/>
                <text x="${xPos - 10}" y="140" font-size="12">${m.label}</text>
            `;

            const yPos = center.y - m.val * pixelsPerUnit;
            axisMarks.innerHTML += `
                <line x1="145" y1="${yPos}" x2="155" y2="${yPos}" stroke="#000720"/>
                <text x="160" y="${yPos + 5}" font-size="12">${m.label}</text>
            `;
        });
    }

    function drawShapes(r) {
        const shapes = document.getElementById('shapes');
        shapes.innerHTML = '';
        if (!r) return;

        const halfR = r / 2;
        const style = 'fill="blue" fill-opacity="0.4" stroke="navy" stroke-width="2"';

        shapes.innerHTML += `<rect x="${center.x}" y="${center.y - r * pixelsPerUnit}" 
            width="${halfR * pixelsPerUnit}" height="${r * pixelsPerUnit}" ${style}/>`;

        shapes.innerHTML += `<polygon points="${center.x},${center.y} ${center.x - halfR * pixelsPerUnit},${center.y} ${center.x},${center.y - r * pixelsPerUnit}" ${style}/>`;

        const radius = halfR * pixelsPerUnit;
        shapes.innerHTML += `<path d="M ${center.x} ${center.y} L ${center.x + radius} ${center.y} A ${radius} ${radius} 0 0 1 ${center.x} ${center.y + radius} Z" ${style}/>`;
    }


    document.querySelectorAll('.r-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.r-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            selectedR = parseFloat(this.dataset.r);
            rValueSpan.textContent = selectedR;
            setError('.field:has(.r-buttons)', null);
            drawAxisMarks(selectedR);
            drawShapes(selectedR);
            drawSavedPoints();
        });
    });

    yInput.addEventListener('input', () => setError('#y', null));
    document.querySelectorAll('input[name="x"]').forEach(cb => {
        cb.addEventListener('change', () => {
            if (document.querySelectorAll('input[name="x"]:checked').length > 0) {
                setError('.field:has(.x-grid)', null);
            }
        });
    });

    checkBtn?.addEventListener('click', function(e) {
        e.preventDefault();

        const xValues = Array.from(document.querySelectorAll('input[name="x"]:checked')).map(cb => parseFloat(cb.value));
        const yStr = yInput.value.trim();
        const y = parseFloat(yStr.replace(',', '.'));

        let valid = true;

        if (xValues.length === 0) {
            setError('.field:has(.x-grid)', 'Please at least select a X coordinate');
            valid = false;
        }

        if (!yStr) {
            setError('#y', 'Please enter Y coordinate');
            valid = false;
        } else if (isNaN(y)) {
            setError('#y', 'Y must be number');
            valid = false;
        } else if (y <= -5 || y >= 5) {
            setError('#y', 'Y must be in [-5,5]');
            valid = false;
        }

        if (!selectedR) {
            setError('.field:has(.r-buttons)', 'Please select R radio');
            valid = false;
        }

        if (!valid) return;

        submitMultiplePoints(xValues, y, selectedR);
    });

    clearBtn?.addEventListener('click', function(e) {
        e.preventDefault();
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'app';
        form.innerHTML = '<input type="hidden" name="clear" value="true">';
        document.body.appendChild(form);
        form.submit();
    });

    svg.addEventListener('click', function(evt) {
        if (!selectedR) {
            setError('.field:has(.r-buttons)', 'Please select R radio first');
            return;
        }

        const rect = svg.getBoundingClientRect();
        const mathX = (evt.clientX - rect.left - center.x) / pixelsPerUnit;
        const mathY = (center.y - (evt.clientY - rect.top)) / pixelsPerUnit;
        const isHit = checkHit(mathX, mathY, selectedR);

        drawPoint(evt.clientX - rect.left, evt.clientY - rect.top, isHit, mathX, mathY, selectedR);
        submitForm(mathX.toFixed(3), mathY.toFixed(3), selectedR);
    });

    function submitMultiplePoints(xValues, y, r) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'app';
        xValues.forEach(x => form.innerHTML += `<input type="hidden" name="x" value="${x}">`);
        form.innerHTML += `<input type="hidden" name="y" value="${y}">
                          <input type="hidden" name="r" value="${r}">`;
        document.body.appendChild(form);
        form.submit();
    }

    function submitForm(x, y, r) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = 'app';
        form.innerHTML = `<input type="hidden" name="x" value="${x}">
                         <input type="hidden" name="y" value="${y}">
                         <input type="hidden" name="r" value="${r}">`;
        document.body.appendChild(form);
        form.submit();
    }

    function drawSavedPoints() {
        svg.querySelectorAll('circle').forEach(c => c.remove());
        if (!selectedR) return;

        try {
            const points = JSON.parse(savedJson.value || '[]');
            points.forEach(p => {
                const scale = selectedR / p.r;

                const scaledX = p.x * scale;
                const scaledY = p.y * scale;

                const cx = center.x + scaledX * pixelsPerUnit;
                const cy = center.y - scaledY * pixelsPerUnit;

                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', cx);
                circle.setAttribute('cy', cy);
                circle.setAttribute('r', 5);
                circle.className = 'history-point';
                circle.setAttribute('fill', p.hit ? '#4ade80' : '#f87171');
                circle.setAttribute('stroke', '#333');
                circle.setAttribute('stroke-width', '2');
                circle.innerHTML = `<title>X: ${p.x}, Y: ${p.y}, R: ${p.r}, Hit: ${p.hit ? 'YES' : 'NO'}</title>`;
                svg.appendChild(circle);
            });
        } catch(e) {
            console.error('Failed to parse history points:', e);
        }
    }

    function checkHit(x, y, r) {
        if (x >= 0 && x <= r/2 && y >= 0 && y <= r)
            return true;
        if (x >= -r/2 && x <= 0 && y >= 0 && y <= 2*x + r)
            return true;
        if (x >= 0 && x <= r/2 && y <= 0 && y >= -r/2 && x*x + y*y <= (r/2)*(r/2))
            return true;
        return false;
    }

    function drawPoint(cx, cy, isHit, mathX, mathY, r) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', cx);
        circle.setAttribute('cy', cy);
        circle.setAttribute('r', 6);
        circle.className = 'history-point';
        circle.setAttribute('fill', isHit ? '#22c55e' : '#ef4444');
        circle.setAttribute('stroke', '#000');
        circle.setAttribute('stroke-width', '2');
        circle.innerHTML = `<title>X: ${mathX.toFixed(3)}, Y: ${mathY.toFixed(3)}, R: ${r}, Hit: ${isHit ? 'YES' : 'NO'}</title>`;
        svg.appendChild(circle);
    }

    drawAxisMarks(selectedR);
    drawShapes(selectedR);
    drawSavedPoints();
});