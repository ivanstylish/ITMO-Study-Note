const fs = require('fs');
const path = require('path');
const sharp = require('C:/Users/26771/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const dir = __dirname;
const data = JSON.parse(fs.readFileSync(path.join(dir, 'queue_values.json'), 'utf8'));
const W = 1600, H = 940;
const plot = { left: 150, right: 1500, top: 125, bottom: 735 };
const X = v => plot.left + (v - .1) / .9 * (plot.right - plot.left);
const Y = v => plot.bottom - v / 3 * (plot.bottom - plot.top);
const num = v => v.toFixed(1).replace('.', ',');
const svg = [`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`,
  '<rect width="1600" height="940" fill="white"/>',
  '<g font-family="Times New Roman" fill="#111">',
  '<text x="800" y="65" text-anchor="middle" font-size="38">Средняя суммарная длина очередей</text>'];
for (let i=0; i<=6; i++) {
  const v = i / 2, y = Y(v);
  svg.push(`<line x1="${plot.left}" x2="${plot.right}" y1="${y}" y2="${y}" stroke="#dedede" stroke-width="1.5"/>`);
  svg.push(`<text x="${plot.left-24}" y="${y+11}" text-anchor="end" font-size="31">${Number.isInteger(v) ? v : num(v)}</text>`);
}
for (let i=1; i<=10; i++) {
  const v = i / 10, x = X(v);
  svg.push(`<line x1="${x}" x2="${x}" y1="${plot.bottom}" y2="${plot.bottom+10}" stroke="#444" stroke-width="1.5"/>`);
  svg.push(`<text x="${x}" y="${plot.bottom+49}" text-anchor="middle" font-size="30">${num(v)}</text>`);
}
svg.push(`<path d="M${plot.left},${plot.top} V${plot.bottom} H${plot.right}" fill="none" stroke="#444" stroke-width="2"/>`);
svg.push(`<line x1="${X(.5)}" x2="${X(.5)}" y1="${plot.top}" y2="${plot.bottom}" stroke="#8d8d8d" stroke-width="2" stroke-dasharray="10 9"/>`);
svg.push(`<text x="${X(.5)+14}" y="${plot.top+35}" font-size="30">λ = 0,5</text>`);
for (const [name, color, offset, label] of [['system1','#245e8d',445,'Система 1'],['system2','#ad4b28',880,'Система 2']]) {
  const d = data.map((r,i)=>`${i ? 'L' : 'M'}${X(r.lambda)},${Y(r[name])}`).join(' ');
  svg.push(`<path d="${d}" fill="none" stroke="${color}" stroke-width="4.5"/>`);
  for (const r of data) svg.push(`<circle cx="${X(r.lambda)}" cy="${Y(r[name])}" r="6.5" fill="${color}"/>`);
  svg.push(`<line x1="${offset}" x2="${offset+90}" y1="893" y2="893" stroke="${color}" stroke-width="5"/>`);
  svg.push(`<circle cx="${offset+45}" cy="893" r="6.5" fill="${color}"/>`);
  svg.push(`<text x="${offset+112}" y="904" font-size="32">${label}</text>`);
}
svg.push('<text x="825" y="839" text-anchor="middle" font-size="34">Интенсивность входного потока λ, с⁻¹</text>');
svg.push('<text x="48" y="430" text-anchor="middle" transform="rotate(-90 48 430)" font-size="34">Lq, заявок</text>');
svg.push('</g></svg>');
const source = svg.join('\n');
fs.writeFileSync(path.join(dir,'queue_comparison.svg'), source);
sharp(Buffer.from(source)).png().toFile(path.join(dir,'queue_comparison.png'))
  .then(()=>console.log('Created one criterion plot using actual WinMark output values.'))
  .catch(e=>{console.error(e);process.exitCode=1;});
