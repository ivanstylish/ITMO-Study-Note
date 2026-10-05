import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import MarkdownIt from 'markdown-it';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'navigation/catalog.json'), 'utf8'));
const parser = new MarkdownIt({ html: false });
const anchorParser = new MarkdownIt({ html: true });
const files = new Set(['README.md', ...catalog.courses.map(c => c.dashboard)]);
const visit = dir => {
  if (!fs.existsSync(path.join(root, dir))) return;
  for (const entry of fs.readdirSync(path.join(root, dir), { withFileTypes: true })) {
    const file = path.posix.join(dir, entry.name);
    if (entry.isDirectory()) visit(file);
    else if (entry.name.endsWith('.md')) files.add(file);
  }
};
for (const dir of ['navigation', 'academic', 'knowledge', 'study']) visit(dir);
for (const c of catalog.courses) {
  for (const entry of c.resources.resources || []) {
    if (/\/(?:quick-review|cheatsheet)\.md$/.test(entry.path)) files.add(entry.path);
  }
}
// Only the newly authored snapshot overview is maintained here. Imported historical
// README/project notes retain their source wording and may mention unavailable paths.
const snapshots = ['WebProgramming/Lab2', 'WebProgramming/Lab3/local-source', 'WebProgramming/Lab3/opi-variant', 'WebProgramming/Lab4/local-source', 'ComputationalMath/Lab1/local-variant', 'ProgrammingLanguage/work8', 'AADS/local-lab1', 'InformationSystem/Lab1/local-variant'];
if (fs.existsSync(path.join(root, 'ProgrammingLanguage/local-variants'))) {
  for (const d of fs.readdirSync(path.join(root, 'ProgrammingLanguage/local-variants'))) snapshots.push('ProgrammingLanguage/local-variants/' + d);
}
for (const d of snapshots) if (fs.existsSync(path.join(root, d, 'README.md'))) files.add(d + '/README.md');
// Check only our inserted navigation block, leaving legacy body links outside
// this maintenance scope. Original course readmes remain the familiar entry.
const bridgeSources = new Map();
for (const course of catalog.courses) {
  const dir = course.directory === 'Math' || course.directory.startsWith('Math/') ? 'Math' : course.directory;
  const name = fs.readdirSync(path.join(root, dir)).find(n => n.toLowerCase() === 'readme.md');
  if (!name) continue;
  const file = path.posix.join(dir, name);
  const source = fs.readFileSync(path.join(root, file), 'utf8');
  const match = source.match(/<!-- kb:navigation:start -->([\s\S]*?)<!-- kb:navigation:end -->/);
  if (match) { files.add(file); bridgeSources.set(file, match[1]); }
}
const errors = [];
let links = 0;
const anchorsCache = new Map();
function anchors(file) {
  if (anchorsCache.has(file)) return anchorsCache.get(file);
  const source = fs.readFileSync(file, 'utf8');
  const result = new Set();
  const tokens = anchorParser.parse(source, {});
  for (const token of tokens) {
    const html = token.type === 'html_block' ? [token] : (token.children || []).filter(child => child.type === 'html_inline');
    for (const part of html) for (const match of part.content.matchAll(/<a\s+[^>]*(?:id|name)=["']([^"']+)["'][^>]*>/g)) result.add(match[1]);
  }
  const slugs = new Set();
  for (let i = 0; i < tokens.length; i++) if (tokens[i].type === 'heading_open') {
    const inline = tokens[i + 1];
    let title = (inline.children || []).filter(t => ['text', 'code_inline', 'image'].includes(t.type)).map(t => t.content).join('');
    title = title.replace(/\{#([^}]+)\}/g, (_, id) => { result.add(id); return ''; });
    title = title.trim().toLowerCase().replace(/[^\p{L}\p{N}\p{M}\s_-]/gu, '').replace(/ /g, '-');
    let slug = title, suffix = 0;
    while (slugs.has(slug)) slug = `${title}-${++suffix}`;
    slugs.add(slug);
    result.add(slug);
  }
  anchorsCache.set(file, result);
  return result;
}
function validate(from, href) {
  if (/^(?:https?:|mailto:|tel:|data:|app:|codex:|\/\/)/i.test(href)) return;
  links++;
  const [rawFile, rawAnchor] = href.split('#');
  let file;
  try { file = decodeURIComponent(rawFile.split('?')[0]); } catch { errors.push(`${from}: URL 编码无效`); return; }
  if (/^[A-Za-z]:[\\/]/.test(file)) { errors.push(`${from}: 存在本机绝对路径`); return; }
  const target = file ? path.resolve(root, file.startsWith('/') ? '.' + file : path.posix.dirname(from) + '/' + file) : path.resolve(root, from);
  const relative = path.relative(root, target);
  if (path.isAbsolute(relative) || relative === '..' || relative.startsWith('..' + path.sep)) { errors.push(`${from}: 链接超出仓库范围`); return; }
  if (!fs.existsSync(target)) { errors.push(`${from}: 目标不存在 → ${file}`); return; }
  if (rawAnchor && path.extname(target).toLowerCase() === '.md') {
    let anchor;
    try { anchor = decodeURIComponent(rawAnchor); } catch { errors.push(`${from}: 锚点编码无效`); return; }
    if (!anchors(target).has(anchor)) errors.push(`${from}: 锚点不存在 → ${file}#${anchor}`);
  }
}
for (const file of files) {
  const absolute = path.join(root, file);
  if (!fs.existsSync(absolute)) { errors.push(`维护页面不存在：${file}`); continue; }
  const source = bridgeSources.get(file) ?? fs.readFileSync(absolute, 'utf8');
  for (const token of parser.parse(source, {})) for (const inline of token.children || []) {
    if (inline.type === 'link_open') validate(file, inline.attrGet('href'));
    if (inline.type === 'image') validate(file, inline.attrGet('src'));
  }
  if (source.includes('](file:') || source.includes('](C:') || source.includes('](F:')) errors.push(`${file}: 本机文件链接不可公开访问`);
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`已检查 ${files.size} 个维护页面、${links} 个本地链接与锚点。历史笔记正文的断链不在本检查范围。`);
