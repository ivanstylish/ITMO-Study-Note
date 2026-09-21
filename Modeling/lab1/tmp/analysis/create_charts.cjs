"use strict";

const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const OUT = "D:\\Study-Note\\Modeling\\lab1\\tmp\\analysis\\variant115";
// 先运行 analyze_variant115.py 得到 results.json，再运行本文件生成六张 PNG。
// 这里读取已有统计结果；图像绘制不重新抽样，不改变模型参数。
const data = JSON.parse(fs.readFileSync(path.join(OUT, "results.json"), "utf8"));

const W = 1200;
const H = 600;
const M = { l: 105, r: 45, t: 72, b: 82 };
const IW = W - M.l - M.r;
const IH = H - M.t - M.b;
const esc = (s) => String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
const fmt = (v, d = 0) => Number(v).toFixed(d).replace(".", ",");

function base(title, xLabel, yLabel) {
  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`,
    `<rect width="100%" height="100%" fill="#FFFFFF"/>`,
    `<style>text{font-family:Arial,'DejaVu Sans',sans-serif;fill:#1F2937}.title{font-size:27px;font-weight:700}.axis{font-size:18px}.tick{font-size:15px}.legend{font-size:16px}</style>`,
    `<text x="${W / 2}" y="39" text-anchor="middle" class="title">${esc(title)}</text>`,
    `<line x1="${M.l}" y1="${M.t + IH}" x2="${M.l + IW}" y2="${M.t + IH}" stroke="#374151" stroke-width="1.5"/>`,
    `<line x1="${M.l}" y1="${M.t}" x2="${M.l}" y2="${M.t + IH}" stroke="#374151" stroke-width="1.5"/>`,
    `<text x="${M.l + IW / 2}" y="${H - 20}" text-anchor="middle" class="axis">${esc(xLabel)}</text>`,
    `<text x="25" y="${M.t + IH / 2}" text-anchor="middle" class="axis" transform="rotate(-90 25 ${M.t + IH / 2})">${esc(yLabel)}</text>`,
  ];
}

// 将数据范围线性映射到画布坐标：像素位置=起点+(值-min)/(max-min)×长度。
// SVG 的 y 坐标向下增大，故纵轴映射需要反向。
function xScale(v, min, max) { return M.l + (v - min) / (max - min) * IW; }
function yScale(v, min, max) { return M.t + IH - (v - min) / (max - min) * IH; }

function addXTicks(svg, min, max, count, digits = 0) {
  for (let i = 0; i <= count; i++) {
    const v = min + (max - min) * i / count;
    const x = xScale(v, min, max);
    svg.push(`<line x1="${x}" y1="${M.t}" x2="${x}" y2="${M.t + IH}" stroke="#E5E7EB"/>`);
    svg.push(`<text x="${x}" y="${M.t + IH + 28}" text-anchor="middle" class="tick">${fmt(v, digits)}</text>`);
  }
}

function addYTicks(svg, min, max, count, digits = 0) {
  for (let i = 0; i <= count; i++) {
    const v = min + (max - min) * i / count;
    const y = yScale(v, min, max);
    svg.push(`<line x1="${M.l}" y1="${y}" x2="${M.l + IW}" y2="${y}" stroke="#D1D5DB"/>`);
    svg.push(`<text x="${M.l - 15}" y="${y + 5}" text-anchor="end" class="tick">${fmt(v, digits)}</text>`);
  }
}

function polyline(values, xMin, xMax, yMin, yMax, color, width = 2) {
  const pts = values.map((v, i) => {
    const xVal = xMin + (xMax - xMin) * i / (values.length - 1);
    return `${xScale(xVal, xMin, xMax).toFixed(1)},${yScale(v, yMin, yMax).toFixed(1)}`;
  }).join(" ");
  return `<polyline fill="none" stroke="${color}" stroke-width="${width}" points="${pts}"/>`;
}

async function save(name, svg) {
  svg.push("</svg>");
  const xml = svg.join("\n");
  await sharp(Buffer.from(xml)).png().toFile(path.join(OUT, name));
}

async function sequenceChart(values, title, name, color) {
  // 横轴保留观测顺序，不能先排序；用来识别趋势、周期和偶发峰值。
  // 当前实验固定 300 个观测，纵轴上界向上取整到 50 的倍数。
  const yMax = Math.ceil(Math.max(...values) / 50) * 50;
  const svg = base(title, "Номер наблюдения", "Значение");
  addXTicks(svg, 1, 300, 6, 0);
  addYTicks(svg, 0, yMax, 6, 0);
  svg.push(polyline(values, 1, 300, 0, yMax, color, 2));
  await save(name, svg);
}

async function acfChart(values, title, name, color) {
  // 连接 1 至 10 阶自相关；浅蓝区为 ±1.96/√300 的近似参考带。
  // 参考带只用于单个滞后的粗略判断，不能据此证明所有观测完全独立。
  const yMin = -0.20, yMax = 0.20;
  const svg = base(title, "Сдвиг", "Коэффициент автокорреляции");
  const upper = data.acf_95_bound;
  const y1 = yScale(upper, yMin, yMax), y2 = yScale(-upper, yMin, yMax);
  svg.push(`<rect x="${M.l}" y="${y1}" width="${IW}" height="${y2 - y1}" fill="#DCECF7" opacity="0.9"/>`);
  addXTicks(svg, 1, 10, 9, 0);
  addYTicks(svg, yMin, yMax, 4, 2);
  svg.push(`<line x1="${M.l}" y1="${yScale(0, yMin, yMax)}" x2="${M.l + IW}" y2="${yScale(0, yMin, yMax)}" stroke="#374151" stroke-width="1.5"/>`);
  svg.push(polyline(values, 1, 10, yMin, yMax, color, 3));
  values.forEach((v, i) => svg.push(`<circle cx="${xScale(i + 1, 1, 10)}" cy="${yScale(v, yMin, yMax)}" r="5" fill="${color}"/>`));
  svg.push(`<rect x="${M.l + IW - 340}" y="${M.t + 15}" width="19" height="13" fill="#DCECF7"/>`);
  svg.push(`<text x="${M.l + IW - 313}" y="${M.t + 27}" class="legend">95%-я граница ±1,96/√n</text>`);
  await save(name, svg);
}

function histogram(values, edges) {
  // 每个观测落入一个 [左边界, 右边界) 区间；最后一个区间额外包含右端点。
  // 返回频数，不是密度；后续比较理论密度时还需按样本量和组距归一化。
  const counts = Array(edges.length - 1).fill(0);
  values.forEach((v) => {
    let i = edges.findIndex((e, idx) => idx < edges.length - 1 && v >= e && v < edges[idx + 1]);
    if (v === edges[edges.length - 1]) i = counts.length - 1;
    if (i >= 0) counts[i]++;
  });
  return counts;
}

async function histogramChart(values, edges, title, name) {
  // 原始频数直方图：每根柱子的高度为区间内观测个数，全部频数之和为 300。
  const counts = histogram(values, edges);
  const yMax = Math.ceil(Math.max(...counts) / 50) * 50;
  const min = edges[0], max = edges.at(-1);
  const svg = base(title, "Значение", "Частота");
  addXTicks(svg, min, max, 6, 0);
  addYTicks(svg, 0, yMax, 5, 0);
  counts.forEach((c, i) => {
    const x1 = xScale(edges[i], min, max), x2 = xScale(edges[i + 1], min, max);
    const y = yScale(c, 0, yMax);
    svg.push(`<rect x="${x1 + 1}" y="${y}" width="${Math.max(1, x2 - x1 - 2)}" height="${M.t + IH - y}" fill="#3D6FB4" stroke="#FFFFFF"/>`);
  });
  await save(name, svg);
}

async function comparisonChart(original, generated, params, name) {
  // 两组数据使用相同分组边界才能直接比较；范围覆盖两者的最大观测。
  // 此处从 0 起分 18 组，因此边界与原始序列单独绘图时可能不同。
  const min = 0;
  const max = Math.ceil(Math.max(...original, ...generated) / 50) * 50;
  const edges = Array.from({length: 19}, (_, i) => min + (max - min) * i / 18);
  const width = edges[1] - edges[0];
  // 密度柱高 f_j=c_j/(n*h)：柱高×组距为该组相对频率，全部柱面积之和为 1。
  // 归一化后才能将经验直方图与理论概率密度放在同一纵轴上。
  const co = histogram(original, edges).map(c => c / original.length / width);
  const cg = histogram(generated, edges).map(c => c / generated.length / width);
  const q = params.q, t1 = params.t1, t2 = params.t2;
  const grid = Array.from({length: 500}, (_, i) => max * i / 499);
  // H₂ 密度 f(x)=q/t1·exp(-x/t1)+(1-q)/t2·exp(-x/t2)，x≥0。
  // t1、t2 是分量均值，指数分布的速率参数分别为 1/t1、1/t2。
  const dens = grid.map(x => q / t1 * Math.exp(-x / t1) + (1 - q) / t2 * Math.exp(-x / t2));
  const yMax = Math.max(...co, ...cg, ...dens) * 1.12;
  const svg = base("Сравнение распределений", "Значение", "Плотность");
  addXTicks(svg, min, max, 6, 0);
  addYTicks(svg, 0, yMax, 5, 3);
  co.forEach((c, i) => {
    const x1 = xScale(edges[i], min, max), x2 = xScale(edges[i + 1], min, max);
    const y = yScale(c, 0, yMax);
    svg.push(`<rect x="${x1 + 1}" y="${y}" width="${Math.max(1, x2 - x1 - 2)}" height="${M.t + IH - y}" fill="#8FB3D9" opacity="0.70"/>`);
  });
  // 生成样本采用阶梯线显示分组密度，原始样本用柱形，理论密度用平滑折线。
  const stepPoints = [];
  cg.forEach((c, i) => {
    const x1 = xScale(edges[i], min, max), x2 = xScale(edges[i + 1], min, max), y = yScale(c, 0, yMax);
    if (i === 0) stepPoints.push(`${x1},${yScale(0, 0, yMax)}`, `${x1},${y}`);
    stepPoints.push(`${x2},${y}`);
    if (i < cg.length - 1) stepPoints.push(`${x2},${yScale(cg[i + 1], 0, yMax)}`);
  });
  svg.push(`<polyline fill="none" stroke="#C95A43" stroke-width="3" points="${stepPoints.join(" ")}"/>`);
  const densPts = dens.map((v, i) => `${xScale(grid[i], min, max)},${yScale(v, 0, yMax)}`).join(" ");
  svg.push(`<polyline fill="none" stroke="#1B6B4A" stroke-width="4" points="${densPts}"/>`);
  const lx = M.l + IW - 300, ly = M.t + 18;
  svg.push(`<rect x="${lx}" y="${ly}" width="20" height="13" fill="#8FB3D9" opacity="0.7"/><text x="${lx + 30}" y="${ly + 12}" class="legend">Исходная ЧП</text>`);
  svg.push(`<line x1="${lx}" y1="${ly + 34}" x2="${lx + 20}" y2="${ly + 34}" stroke="#C95A43" stroke-width="3"/><text x="${lx + 30}" y="${ly + 40}" class="legend">Сгенерированная ЧП</text>`);
  svg.push(`<line x1="${lx}" y1="${ly + 64}" x2="${lx + 20}" y2="${ly + 64}" stroke="#1B6B4A" stroke-width="4"/><text x="${lx + 30}" y="${ly + 70}" class="legend">Плотность H₂</text>`);
  await save(name, svg);
}

(async () => {
  // 输出顺序：原序列、原自相关、原频数直方图、生成序列、生成自相关、密度比较。
  await sequenceChart(data.original, "График исходной числовой последовательности", "01_original_sequence.png", "#2E5EAA");
  await acfChart(data.original_acf, "Автокорреляция исходной ЧП", "02_original_acf.png", "#2E5EAA");
  await histogramChart(data.original, data.histogram.edges, "Гистограмма распределения частот исходной ЧП", "03_original_histogram.png");
  await sequenceChart(data.generated, "График сгенерированной числовой последовательности", "04_generated_sequence.png", "#C95A43");
  await acfChart(data.generated_acf, "Автокорреляция сгенерированной ЧП", "05_generated_acf.png", "#C95A43");
  await comparisonChart(data.original, data.generated, data.hyperexponential, "06_distribution_comparison.png");
})();
