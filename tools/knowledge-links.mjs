import fs from 'node:fs';
import path from 'node:path';

export function buildBacklinks(root, files, overrides = new Map(), titles = new Map()) {
  const known = new Set(files);
  const inbound = new Map([...known].map(file => [file, new Set()]));
  const contents = new Map();
  for (const file of known) {
    const source = overrides.get(file) ?? fs.readFileSync(path.join(root, file), 'utf8');
    contents.set(file, source);
    let fence = null;
    const prose = source.split(/\r?\n/).filter(line => {
      const boundary = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
      if (boundary && (!fence || boundary[1][0] === fence.char && boundary[1].length >= fence.length && !boundary[2].trim())) {
        fence = fence ? null : { char: boundary[1][0], length: boundary[1].length }; return false;
      }
      return !fence;
    }).join('\n').replace(/`+[^`\n]*`+/g, '');
    for (const match of prose.matchAll(/\[[^\]\n]*\]\(((?:[^()\s]|\([^()\s]*\))*)\)/g)) {
      let href;
      try { href = decodeURIComponent(match[1].split('#')[0]); } catch { continue; }
      if (!href || /^[a-z]+:|^\/\//i.test(href)) continue;
      const target = path.posix.normalize(href.startsWith('/') ? href.slice(1) : path.posix.join(path.posix.dirname(file), href));
      if (target !== file && known.has(target)) inbound.get(target).add(file);
    }
  }
  const title = file => titles.get(file) || (contents.get(file).match(/^#{1,6}\s+(.+)$/m)?.[1] || path.posix.basename(file, '.md'))
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/<[^>]+>|\{#[^}]+\}/g, '').replace(/[*`]/g, '').trim();
  return Object.fromEntries([...inbound].sort(([a], [b]) => a.localeCompare(b)).map(([file, sources]) => [file, [...sources].sort().map(source => ({ path: source, title: title(source) }))]));
}

export function backlinkPage(root, catalog, outputs, link) {
  const candidates = new Set(['README.md', 'knowledge/index.md', 'knowledge/mindmap.md', 'study/defense.md', 'study/revision.md', ...catalog.courses.map(c => c.dashboard), ...outputs.keys()]);
  candidates.delete('knowledge/backlinks.md');
  const titles = new Map(catalog.courses.map(c => [c.dashboard, c.title]));
  for (const course of catalog.courses) for (const entries of Object.values(course.resources)) for (const entry of entries) {
    if (/\.md$/i.test(entry.path)) { candidates.add(entry.path); titles.set(entry.path, entry.label); }
  }
  const files = [...candidates].filter(file => outputs.has(file) || fs.existsSync(path.join(root, file)));
  const graph = buildBacklinks(root, files, outputs, titles);
  const from = 'knowledge/backlinks.md';
  const sources = target => (graph[target] || []).map(s => link(from, s.title.replaceAll('|', '\\|'), s.path)).join(' · ') || '暂未被其他页面引用';
  const courseRows = catalog.courses.map(c => `| ${link(from, c.title, c.dashboard)} | ${sources(c.dashboard)} |`).join('\n');
  const notes = [...titles].filter(([file]) => !catalog.courses.some(c => c.dashboard === file) && graph[file]?.length)
    .sort(([a], [b]) => graph[b].length - graph[a].length || a.localeCompare(b)).slice(0, 24);
  return `# 资料反向关联\n\n${link(from, '首页', 'README.md')} · ${link(from, '知识地图', 'knowledge/index.md')} · ${link(from, '复习脑图', 'knowledge/mindmap.md')}\n\n从一门课程或一份笔记，找到引用它的学期、复习路线与关联课程。资料更新后，引用入口随导航一起更新。\n\n## 课程引用\n\n| 课程 | 从哪里进入 |\n|---|---|\n${courseRows}\n\n## 常用笔记的引用\n\n| 笔记 | 哪些页面引用了它 |\n|---|---|\n${notes.map(([file, title]) => `| ${link(from, title, file)} | ${sources(file)} |`).join('\n')}\n`;
}
