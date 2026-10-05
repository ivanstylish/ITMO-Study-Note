import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'navigation/catalog.json'), 'utf8'));
const check = process.argv.includes('--check');
const start = '<!-- kb:navigation:start -->';
const end = '<!-- kb:navigation:end -->';
const planned = [];
const seen = new Set();
const problems = [];

for (const course of catalog.courses) {
  // Math retains its original shared entry, with its three new dashboards linked.
  const directory = course.directory.startsWith('Math/') || course.directory === 'Math' ? 'Math' : course.directory;
  if (seen.has(directory)) continue;
  seen.add(directory);
  const entry = fs.readdirSync(path.join(root, directory)).find(name => name.toLowerCase() === 'readme.md');
  if (!entry) continue;
  const file = path.posix.join(directory, entry);
  const targets = directory === 'Math' ? catalog.courses.filter(c => c.dashboard.startsWith('Math/')) : [course];
  const links = targets.map(c => {
    const target = path.posix.relative(directory, c.dashboard).split('/').map(encodeURIComponent).join('/');
    return `[${directory === 'Math' ? c.title : '课程首页 · 复习与答辩'}](${target})`;
  }).join(' · ');
  const block = `${start}\n${links}\n${end}`;
  const source = fs.readFileSync(path.join(root, file), 'utf8');
  const hasStart = source.includes(start), hasEnd = source.includes(end);
  if (hasStart !== hasEnd || source.split(start).length > 2 || source.split(end).length > 2) {
    problems.push(`导航标记异常，保留原文件：${file}`); continue;
  }
  let updated;
  if (hasStart) {
    const before = source.slice(0, source.indexOf(start));
    const after = source.slice(source.indexOf(end) + end.length);
    updated = before + block + (after.trim() ? after : '\n');
  } else {
    // Add a short navigation block; leave the original note byte-for-byte intact.
    // Handle optional frontmatter so a YAML block stays the first block in a file.
    const frontmatter = source.match(/^---\r?\n[\s\S]*?\r?\n---(?:\r?\n|$)/);
    const offset = frontmatter?.[0].length || 0;
    updated = source.slice(0, offset) + block + (source.slice(offset) ? '\n\n' + source.slice(offset) : '\n');
  }
  if (updated !== source) planned.push({file, updated});
}
if (problems.length) { console.error(problems.join('\n')); process.exit(1); }
if (check && planned.length) {
  console.error(planned.map(p => `课程 README 导航需要更新：${p.file}`).join('\n')); process.exit(1);
}
if (!check) for (const item of planned) fs.writeFileSync(path.join(root, item.file), item.updated);
console.log(`${check ? '已验证' : '已更新'}原课程 README 导航（${seen.size} 个课程目录；${planned.length} 处变更），原文保留。`);
