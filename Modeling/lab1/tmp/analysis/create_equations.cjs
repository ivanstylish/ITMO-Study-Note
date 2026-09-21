"use strict";

// 公式图片辅助脚本：将 LaTeX 经 MathJax 转为 SVG，再输出 PNG。
// 本文件负责公式的视觉展示；真实数据计算位于 analyze_variant115.py。

const path = require("path");
const sharp = require("sharp");

const { mathjax } = require("mathjax-full/js/mathjax.js");
const { TeX } = require("mathjax-full/js/input/tex.js");
const { SVG } = require("mathjax-full/js/output/svg.js");
const { liteAdaptor } = require("mathjax-full/js/adaptors/liteAdaptor.js");
const { RegisterHTMLHandler } = require("mathjax-full/js/handlers/html.js");
const { AllPackages } = require("mathjax-full/js/input/tex/AllPackages.js");

const outDir = "D:\\Study-Note\\Modeling\\lab1\\tmp\\analysis\\variant115";
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const tex = new TeX({ packages: AllPackages });
const svgOut = new SVG({ fontCache: "local" });
const doc = mathjax.document("", { InputJax: tex, OutputJax: svgOut });

function toSvg(latex) {
  // display=true 按独立公式排版；提取 SVG 图像供 sharp 栅格化。
  const html = adaptor.outerHTML(doc.convert(latex, { display: true }));
  const a = html.indexOf("<svg");
  const b = html.indexOf("</svg>");
  let svg = html.slice(a, b + 6).replace(/<\?xml[^>]*>/g, "");
  if (!/xmlns="http:\/\/www\.w3\.org\/2000\/svg"/.test(svg)) {
    svg = svg.replace(/<svg /, '<svg xmlns="http://www.w3.org/2000/svg" ');
  }
  svg = svg.replace(/currentColor/g, "#000000");
  return Buffer.from(svg);
}

async function make(name, latex, targetWidth) {
  // 300 DPI 渲染后统一图片宽度；此过程不执行公式中的统计计算。
  await sharp(toSvg(latex), { density: 300 })
    .resize({ width: targetWidth, withoutEnlargement: false })
    .png()
    .toFile(path.join(outDir, name));
}

(async () => {
  // eq_stats：均值、无偏方差（n-1 分母）、标准差及变异系数。
  // eq_ci_dev：正态近似置信半宽、完整区间、相对 n=300 的偏差。
  // eq_acf：两个平移截取序列分别减各自均值，与 np.corrcoef 的实现一致。
  // eq_hyper_params：H₂ 矩匹配参数；显示的 q≤上界包括 t2=0 的退化边界，
  // 实际计算为保证两个指数分量均值都大于零，选择严格小于上界的 q。
  // eq_generator：U1 选择分量，U2 通过指数分布的逆函数生成观测值。
  // eq_corr：原始和生成的完整序列之间的 Pearson 相关。
  await make("eq_stats.png", String.raw`\bar{x}_n=\frac{1}{n}\sum_{i=1}^{n}x_i,\qquad s_n^2=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x}_n)^2,\qquad s_n=\sqrt{s_n^2},\qquad v_n=\frac{s_n}{\bar{x}_n}`, 1900);
  await make("eq_ci_dev.png", String.raw`\varepsilon_p=t_p\frac{s_n}{\sqrt{n}},\qquad I_p=[\bar{x}_n-\varepsilon_p;\,\bar{x}_n+\varepsilon_p],\qquad \Delta A_n=\frac{A_n-A_{300}}{A_{300}}\cdot100\%`, 1900);
  await make("eq_acf.png", String.raw`r_k=\frac{\sum_{i=1}^{n-k}(x_i-\bar{x}_{1:n-k})(x_{i+k}-\bar{x}_{1+k:n})}{\sqrt{\sum_{i=1}^{n-k}(x_i-\bar{x}_{1:n-k})^2\sum_{i=1}^{n-k}(x_{i+k}-\bar{x}_{1+k:n})^2}}`, 1650);
  await make("eq_hyper_params.png", String.raw`q\leq\frac{2}{1+v^2},\qquad t_1=\left[1+\sqrt{\frac{1-q}{2q}(v^2-1)}\right]t,\qquad t_2=\left[1-\sqrt{\frac{q}{2(1-q)}(v^2-1)}\right]t`, 1900);
  await make("eq_generator.png", String.raw`X=\begin{cases}-t_1\ln(1-U_2),&U_1<q,\\-t_2\ln(1-U_2),&U_1\geq q,\end{cases}\qquad U_1,U_2\sim U(0,1)`, 1500);
  await make("eq_corr.png", String.raw`r_{xy}=\frac{\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2\sum_{i=1}^{n}(y_i-\bar{y})^2}}`, 1250);
})();
