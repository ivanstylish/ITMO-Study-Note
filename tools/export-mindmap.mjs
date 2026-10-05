import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Transformer } from 'markmap-lib/no-plugins';
import { build } from 'esbuild';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = await fs.readFile(path.join(root, 'knowledge/mindmap.md'), 'utf8');
const start = source.indexOf('\n## ');
if (start < 0) throw new Error('复习脑图缺少大纲');
const transformer = new Transformer();
transformer.md.set({ html: false });
const tree = transformer.transform('# ITMO 学习知识库\n\n' + source.slice(start)).root;
const entry = `import { Markmap } from 'markmap-view';
const tree = ${JSON.stringify(tree)};
const svg = document.querySelector('svg');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const map = Markmap.create(svg, {initialExpandLevel:2,maxWidth:260,duration:reduced?0:180,color:n=>['#247b70','#5869b2','#a87125','#357ca7','#a65f87'][(n.state?.id||0)%5]}, structuredClone(tree));
const expand = async level => { await map.setData(structuredClone(tree), {initialExpandLevel:level}); await map.fit(); };
document.querySelector('[data-action=expand]').onclick = () => expand(-1);
document.querySelector('[data-action=collapse]').onclick = () => expand(1);
document.querySelector('[data-action=fit]').onclick = () => map.fit();
new ResizeObserver(() => map.fit()).observe(svg);
map.fit();
document.documentElement.dataset.ready='true';`;
const bundle = await build({ stdin: { contents: entry, resolveDir: root, sourcefile: 'mindmap-export.js' }, bundle: true, minify: true, platform: 'browser', format: 'iife', write: false, target: 'es2022', legalComments: 'inline' });
const script = bundle.outputFiles[0].text.replaceAll('</script', '<\\/script');
const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ITMO · 复习脑图</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f3f6f5;color:#25342f;font-family:"Segoe UI","Microsoft YaHei",system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:28px}header{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:20px;margin-bottom:20px}.eyebrow{font-size:11px;font-weight:700;letter-spacing:.18em;color:#247b70}h1{font-size:clamp(25px,4vw,36px);letter-spacing:-.04em;margin:8px 0}p{font-size:13px;line-height:1.9;color:#65756e;margin:0}nav{display:flex;flex-wrap:wrap;gap:8px}button{padding:10px 15px;border:1px solid #dbe5df;border-radius:9px;background:white;color:#324e43;font:inherit;font-size:13px;cursor:pointer}button:focus-visible,a:focus-visible{outline:3px solid #247b70;outline-offset:3px}.canvas{border:1px solid #dbe5df;border-radius:18px;overflow:hidden;background:white;box-shadow:0 12px 36px #2445350a}svg{display:block;width:100%;height:calc(100vh - 210px);min-height:450px}svg a{color:#247b70}.markmap-foreign{color:#25342f}footer{margin:12px 0;color:#65756e;font-size:12px}@media(max-width:640px){main{padding:18px}svg{height:65vh;min-height:430px}}@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style></head><body><main><header><div><span class="eyebrow">ITMO · LEARNING MAP</span><h1>复习脑图</h1><p>点击节点展开，拖动与滚轮缩放。第 1–4 学期课程与实验 ✓ 已通过。</p></div><nav aria-label="脑图视图"><button data-action="expand">展开全部</button><button data-action="collapse">收起层级</button><button data-action="fit">适应画布</button></nav></header><div class="canvas"><svg aria-label="课程复习脑图" role="img"></svg></div><footer>本文件可以直接在浏览器中打开。节点链接指向仓库资料，Markdown 原文可在 VS Code 中预览。</footer></main><script>${script}</script></body></html>\n`;
await fs.writeFile(path.join(root, 'knowledge/mindmap.html'), html);
console.log(`已导出 knowledge/mindmap.html（${Buffer.byteLength(html)} 字节）；脚本与样式内嵌，可离线打开。`);
