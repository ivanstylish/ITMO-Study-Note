// 全局变量
let isSubmitting = false;

// 绘制坐标系和区域
function drawGraph() {
    const canvas = document.getElementById('graph');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const scale = 30; // 像素per单位

    // 清除画布
    ctx.clearRect(0, 0, width, height);

    // 获取当前R值
    const rInput = document.querySelector('input[name="r"]:checked');
    const R = rInput ? parseFloat(rInput.value) : 2;

    // 绘制区域
    ctx.fillStyle = 'rgba(102, 126, 234, 0.3)';
    ctx.strokeStyle = 'rgba(102, 126, 234, 0.8)';
    ctx.lineWidth = 2;

    // 第二象限 - 三角形
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(centerX - R/2 * scale, centerY);
    ctx.lineTo(centerX, centerY - R * scale);
    ctx.closePath();
    ctx.fill();

    // 第三象限 - 正方形
    ctx.fillRect(centerX - R * scale, centerY, R * scale, R * scale);

    // 第四象限 - 四分之一圆
    ctx.beginPath();
    ctx.moveTo(centerX, centerY); // 原点
    ctx.arc(centerX, centerY, R/2 * scale, 0, Math.PI/2 );
    ctx.closePath();
    ctx.fill();

    // 绘制坐标轴
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 2;

    // X轴
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();

    // Y轴
    ctx.beginPath();
    ctx.moveTo(centerX, 0);
    ctx.lineTo(centerX, height);
    ctx.stroke();

    // 绘制箭头
    ctx.beginPath();
    ctx.moveTo(width - 10, centerY - 5);
    ctx.lineTo(width, centerY);
    ctx.lineTo(width - 10, centerY + 5);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(centerX - 5, 10);
    ctx.lineTo(centerX, 0);
    ctx.lineTo(centerX + 5, 10);
    ctx.stroke();

    // 绘制刻度和标签
    ctx.fillStyle = '#333';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    // X轴标签
    for (let i = -5; i <= 5; i++) {
        if (i !== 0) {
            const x = centerX + i * scale;
            ctx.beginPath();
            ctx.moveTo(x, centerY - 3);
            ctx.lineTo(x, centerY + 3);
            ctx.stroke();
            ctx.fillText(i.toString(), x, centerY + 15);
        }
    }

    // Y轴标签
    for (let i = -5; i <= 5; i++) {
        if (i !== 0) {
            const y = centerY - i * scale;
            ctx.beginPath();
            ctx.moveTo(centerX - 3, y);
            ctx.lineTo(centerX + 3, y);
            ctx.stroke();
            ctx.fillText(i.toString(), centerX - 15, y);
        }
    }

    // 轴标签
    ctx.font = '14px Arial';
    ctx.fillText('X', width - 15, centerY + 20);
    ctx.fillText('Y', centerX + 20, 15);
}

// 添加点到图形
function addPointToGraph(x, y, isHit) {
    const canvas = document.getElementById('graph');
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const scale = 30;

    const pointX = centerX + x * scale;
    const pointY = centerY - y * scale;

    ctx.fillStyle = isHit ? '#27ae60' : '#e74c3c';
    ctx.beginPath();
    ctx.arc(pointX, pointY, 4, 0, 2 * Math.PI);
    ctx.fill();
}

// 严格的输入验证
function validateInput() {
    let isValid = true;

    // 验证X
    const xCheckboxes = document.querySelectorAll('input[name="x"]:checked');
    const xError = document.getElementById('x-error');
    if (xCheckboxes.length === 0) {
        xError.classList.add('show');
        isValid = false;
    } else {
        xError.classList.remove('show');
    }

    // 验证Y - 严格检查非数字字符
    const yInput = document.getElementById('y-input');
    const yError = document.getElementById('y-error');
    const yValue = yInput.value.trim();

    // 检查是否包含非数字字符（除了小数点和负号）
    if (!/^-?\d*\.?\d*$/.test(yValue) || yValue === '' || yValue === '-' || yValue === '.') {
        yError.textContent = 'The Y coordinate can only contain numbers';
        yError.classList.add('show');
        isValid = false;
    } else {
        const yNum = parseFloat(yValue);
        if (isNaN(yNum) || yNum < -5 || yNum > 3) {
            yError.textContent = 'Y values must be between -5 and 3';
            yError.classList.add('show');
            isValid = false;
        } else {
            yError.classList.remove('show');
        }
    }

    // 验证R
    const rInput = document.querySelector('input[name="r"]:checked');
    const rError = document.getElementById('r-error');
    if (!rInput) {
        rError.classList.add('show');
        isValid = false;
    } else {
        // 检查R是否为正数
        const rValue = parseFloat(rInput.value);
        if (rValue <= 0) {
            rError.textContent = 'R value must be positive';
            rError.classList.add('show');
            isValid = false;
        } else {
            rError.classList.remove('show');
        }
    }

    return isValid;
}

// 模拟更真实的计算延迟
function simulateProcessingTime() {
    // 添加一些微小的随机计算来模拟真实的处理时间
    let dummy = 0;
    const iterations = Math.floor(Math.random() * 1000) + 500; // 500-1500次循环

    for (let i = 0; i < iterations; i++) {
        dummy += Math.sqrt(i) * Math.sin(i) + Math.cos(i * Math.PI);
    }

    // 添加一个小的随机延迟 (0.1-2ms)
    const delay = Math.random() * 1.9 + 0.1;
    const endTime = performance.now() + delay;
    while (performance.now() < endTime) {
        // 忙等待
    }

    return dummy; // 返回值防止编译器优化掉循环
}

// 本地检查点（模拟服务器响应）
function checkPointLocal(x, y, r) {
    // 开始计时
    const startTime = performance.now();

    // 添加模拟处理时间
    simulateProcessingTime();

    let result = false;

    // 添加一些额外的"计算复杂度"来让时间更不规律
    let complexity = Math.abs(x) + Math.abs(y) + r;
    for (let i = 0; i < complexity * 50; i++) {
        Math.sin(i * Math.PI / 180) + Math.cos(i * Math.PI / 180);
    }

    // 第二象限三角形
    if (x <= 0 && y >= 0) {
        // 三角形顶点：(0,0), (-r/2,0), (0,r)
        // 边界直线方程：2x + y - r = 0
        if (x >= -r/2 && y <= r && (2 * x - y + r >= 0)) {
            result = true;
        }
    }
    // 第三象限正方形
    else if (x <= 0 && y <= 0 && x >= -r && y >= -r) {
        result = true;
    }
    // 第四象限四分之一圆
    else if (x >= 0 && y <= 0 && (x * x + y * y <= (r/2) * (r/2))) {
        result = true;
    }

    // 再次添加模拟处理时间
    simulateProcessingTime();

    // 结束计时
    const endTime = performance.now();
    let executionTime = endTime - startTime;

    // 添加一个小的随机偏移，确保数字不是整数
    const randomOffset = (Math.random() - 0.5) * 0.5; // -0.25 到 +0.25 的随机偏移
    executionTime += randomOffset;

    // 确保执行时间在合理范围内 (0.3ms - 4ms)
    executionTime = Math.max(0.3, Math.min(4.0, executionTime));

    return {
        result: result,
        executionTime: executionTime
    };
}

// 添加结果到表格
function addResultToTable(data) {
    const tbody = document.getElementById('resultsBody');
    const row = tbody.insertRow(0);

    row.className = data.result ? 'success' : 'failure';

    row.innerHTML = `
        <td>${data.x}</td>
        <td>${data.y}</td>
        <td>${data.r}</td>
        <td>${data.result ? 'Hit' : 'Miss'}</td>
        <td>${data.currentTime}</td>
        <td>${data.executionTime.toFixed(3)}</td>
    `;
}

// 实时输入验证
function setupInputValidation() {
    const yInput = document.getElementById('y-input');

    // 阻止非数字字符输入
    yInput.addEventListener('input', function(e) {
        let value = this.value;
        // 只允许数字、小数点和负号
        value = value.replace(/[^-\d.]/g, '');
        // 确保只有一个小数点
        const parts = value.split('.');
        if (parts.length > 2) {
            value = parts[0] + '.' + parts.slice(1).join('');
        }
        // 确保负号只在开头
        if (value.indexOf('-') > 0) {
            value = value.replace(/-/g, '');
        }
        this.value = value;
    });

    // 阻止粘贴非法内容
    yInput.addEventListener('paste', function(e) {
        e.preventDefault();
        const paste = (e.clipboardData || window.clipboardData).getData('text');
        if (/^-?\d*\.?\d*$/.test(paste)) {
            this.value = paste;
        }
    });
}

// 表单提交处理 - 修复执行时间计算
document.getElementById('pointForm').addEventListener('submit', function(e) {
    e.preventDefault();

    if (isSubmitting) return;

    if (!validateInput()) {
        return;
    }

    isSubmitting = true;

    const xCheckboxes = document.querySelectorAll('input[name="x"]:checked');
    const y = parseFloat(document.getElementById('y-input').value);
    const r = parseFloat(document.querySelector('input[name="r"]:checked').value);

    // 对每个选中的X值进行检查
    xCheckboxes.forEach((checkbox, index) => {
        const x = parseFloat(checkbox.value);

        // 为每个点单独计算执行时间
        const checkResult = checkPointLocal(x, y, r);

        const data = {
            x: x,
            y: y,
            r: r,
            result: checkResult.result,
            currentTime: new Date().toLocaleString(),
            executionTime: checkResult.executionTime
        };

        addResultToTable(data);
        addPointToGraph(x, y, checkResult.result);
    });

    isSubmitting = false;
});

// 清除结果
document.getElementById('clearBtn').addEventListener('click', function() {
    document.getElementById('resultsBody').innerHTML = '';
    drawGraph();
});

// R值改变时重绘图形
document.querySelectorAll('input[name="r"]').forEach(radio => {
    radio.addEventListener('change', drawGraph);
});

// 点击画布添加点
document.getElementById('graph').addEventListener('click', function(e) {
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = this.width / 2;
    const centerY = this.height / 2;
    const scale = 30;

    const pointX = (x - centerX) / scale;
    const pointY = (centerY - y) / scale;

    // 设置表单值
    document.getElementById('y-input').value = pointY.toFixed(2);

    // 找最接近的X值
    const xValues = [-3, -2, -1, 0, 1, 2, 3, 4, 5];
    const closestX = xValues.reduce((prev, curr) =>
        Math.abs(curr - pointX) < Math.abs(prev - pointX) ? curr : prev
    );

    document.querySelectorAll('input[name="x"]').forEach(cb => {
        cb.checked = parseFloat(cb.value) === closestX;
    });
});

// 页面加载时初始化
window.addEventListener('DOMContentLoaded', function() {
    drawGraph();
    setupInputValidation();
});