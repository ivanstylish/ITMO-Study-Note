import React, { useEffect, useRef } from 'react';

const GraphComponent = ({ r, results, onMapClick }) => {
    const canvasRef = useRef(null);

    const CANVAS_SIZE = 400;
    const CENTER = CANVAS_SIZE / 2;
    const PPU = 35;

    const draw = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, CANVAS_SIZE, CANVAS_SIZE);

        const valR = parseFloat(r);
        if (isNaN(valR) || valR <= 0) return;

        const rPx = valR * PPU;

        ctx.fillStyle = 'rgba(33,82,243,0.5)';
        ctx.strokeStyle = '#1e4ce5';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(CENTER, CENTER);
        ctx.lineTo(CENTER + rPx, CENTER);
        ctx.lineTo(CENTER, CENTER - rPx);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.rect(CENTER - rPx / 2, CENTER, rPx / 2, rPx);
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(CENTER, CENTER, rPx, 0, Math.PI / 2, false); // 从左到上
        ctx.lineTo(CENTER, CENTER);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(10, CENTER);
        ctx.lineTo(CANVAS_SIZE - 10, CENTER);
        ctx.moveTo(CENTER, 10);
        ctx.lineTo(CENTER, CANVAS_SIZE - 10);
        ctx.stroke();

        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.moveTo(CANVAS_SIZE - 10, CENTER);
        ctx.lineTo(CANVAS_SIZE - 15, CENTER - 5);
        ctx.lineTo(CANVAS_SIZE - 15, CENTER + 5);
        ctx.closePath();
        ctx.fill();

        ctx.beginPath();
        ctx.moveTo(CENTER, 10);
        ctx.lineTo(CENTER - 5, 15);
        ctx.lineTo(CENTER + 5, 15);
        ctx.closePath();
        ctx.fill();

        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText("X", CANVAS_SIZE - 20, CENTER - 15);
        ctx.fillText("Y", CENTER + 15, 20);

        ctx.font = '12px Arial';
        ctx.lineWidth = 1;


        ctx.beginPath();
        ctx.moveTo(CENTER + rPx, CENTER - 5);
        ctx.lineTo(CENTER + rPx, CENTER + 5);
        ctx.stroke();
        ctx.fillText('R', CENTER + rPx, CENTER + 18);

        ctx.beginPath();
        ctx.moveTo(CENTER - rPx, CENTER - 5);
        ctx.lineTo(CENTER - rPx, CENTER + 5);
        ctx.stroke();
        ctx.fillText('-R', CENTER - rPx, CENTER + 18);

        ctx.beginPath(); ctx.moveTo(CENTER + rPx/2, CENTER - 5);
        ctx.lineTo(CENTER + rPx/2, CENTER + 5);
        ctx.stroke();
        ctx.fillText('R/2', CENTER + rPx/2, CENTER + 18);

        ctx.beginPath();
        ctx.moveTo(CENTER - rPx/2, CENTER - 5);
        ctx.lineTo(CENTER - rPx/2, CENTER + 5);
        ctx.stroke();
        ctx.fillText('-R/2', CENTER - rPx/2, CENTER + 18);

        ctx.beginPath();
        ctx.moveTo(CENTER - 5, CENTER - rPx);
        ctx.lineTo(CENTER + 5, CENTER - rPx);
        ctx.stroke();
        ctx.fillText('R', CENTER - 18, CENTER - rPx);

        ctx.beginPath();
        ctx.moveTo(CENTER - 5, CENTER + rPx);
        ctx.lineTo(CENTER + 5, CENTER + rPx);
        ctx.stroke();
        ctx.fillText('-R', CENTER - 22, CENTER + rPx);

        ctx.beginPath();
        ctx.moveTo(CENTER - 5, CENTER - rPx/2);
        ctx.lineTo(CENTER + 5, CENTER - rPx/2); ctx.stroke();
        ctx.fillText('R/2', CENTER - 22, CENTER - rPx/2);

        ctx.beginPath();
        ctx.moveTo(CENTER - 5, CENTER + rPx/2);
        ctx.lineTo(CENTER + 5, CENTER + rPx/2);
        ctx.stroke();
        ctx.fillText('-R/2', CENTER - 26, CENTER + rPx/2);

        if (results && results.length > 0) {
            results.forEach(point => {
                if (
                    typeof point.x !== 'number' ||
                    typeof point.y !== 'number' ||
                    typeof point.r !== 'number' ||
                    point.r <= 0
                ) return;

                const scale = valR / point.r;
                const displayX = point.x * scale;
                const displayY = point.y * scale;

                const pX = CENTER + displayX * PPU;
                const pY = CENTER - displayY * PPU;

                if (pX >= 0 && pX <= CANVAS_SIZE && pY >= 0 && pY <= CANVAS_SIZE) {
                    ctx.beginPath();
                    ctx.arc(pX, pY, 5, 0, Math.PI * 2);
                    ctx.fillStyle = point.hit ? '#2E7D32' : '#C62828';
                    ctx.fill();
                    ctx.strokeStyle = '#fff';
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
            });
        }
    };

    useEffect(() => {
        draw();
    }, [r, results]);

    const handleClick = (e) => {
        const valR = parseFloat(r);
        if (isNaN(valR) || valR <= 0) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        const mathX = (clickX - CENTER) / PPU;
        const mathY = (CENTER - clickY) / PPU;

        onMapClick(parseFloat(mathX.toFixed(2)), parseFloat(mathY.toFixed(2)));
    };

    return (
        <canvas
            ref={canvasRef}
            width={CANVAS_SIZE}
            height={CANVAS_SIZE}
            onClick={handleClick}
            style={{
                border: '2px solid #E53935',
                borderRadius: '8px',
                cursor: r > 0 ? 'crosshair' : 'not-allowed',
                background: '#fff',
                maxWidth: '100%',
                height: 'auto'
            }}
        />
    );
};

export default GraphComponent;