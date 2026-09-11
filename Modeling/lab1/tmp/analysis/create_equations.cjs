"use strict";

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
  await sharp(toSvg(latex), { density: 300 })
    .resize({ width: targetWidth, withoutEnlargement: false })
    .png()
    .toFile(path.join(outDir, name));
}

(async () => {
  await make("eq_stats.png", String.raw`\bar{x}_n=\frac{1}{n}\sum_{i=1}^{n}x_i,\qquad s_n^2=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar{x}_n)^2,\qquad s_n=\sqrt{s_n^2},\qquad v_n=\frac{s_n}{\bar{x}_n}`, 1900);
  await make("eq_ci_dev.png", String.raw`\varepsilon_p=t_p\frac{s_n}{\sqrt{n}},\qquad I_p=[\bar{x}_n-\varepsilon_p;\,\bar{x}_n+\varepsilon_p],\qquad \Delta A_n=\frac{A_n-A_{300}}{A_{300}}\cdot100\%`, 1900);
  await make("eq_acf.png", String.raw`r_k=\frac{\sum_{i=1}^{n-k}(x_i-\bar{x}_{1:n-k})(x_{i+k}-\bar{x}_{1+k:n})}{\sqrt{\sum_{i=1}^{n-k}(x_i-\bar{x}_{1:n-k})^2\sum_{i=1}^{n-k}(x_{i+k}-\bar{x}_{1+k:n})^2}}`, 1650);
  await make("eq_hyper_params.png", String.raw`q\leq\frac{2}{1+v^2},\qquad t_1=\left[1+\sqrt{\frac{1-q}{2q}(v^2-1)}\right]t,\qquad t_2=\left[1-\sqrt{\frac{q}{2(1-q)}(v^2-1)}\right]t`, 1900);
  await make("eq_generator.png", String.raw`X=\begin{cases}-t_1\ln(1-U_2),&U_1<q,\\-t_2\ln(1-U_2),&U_1\geq q,\end{cases}\qquad U_1,U_2\sim U(0,1)`, 1500);
  await make("eq_corr.png", String.raw`r_{xy}=\frac{\sum_{i=1}^{n}(x_i-\bar{x})(y_i-\bar{y})}{\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2\sum_{i=1}^{n}(y_i-\bar{y})^2}}`, 1250);
})();
