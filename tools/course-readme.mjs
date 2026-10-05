import path from 'node:path';
import { courseStatusSummary, labStatus } from './course-status.mjs';

export const overviewStart = '<!-- kb:course-overview:start -->';
export const overviewEnd = '<!-- kb:course-overview:end -->';
export const resourcesStart = '<!-- kb:course-resources:start -->';
export const resourcesEnd = '<!-- kb:course-resources:end -->';

function stripBlock(source, start, end) {
  const starts = source.split(start).length - 1, ends = source.split(end).length - 1;
  if (!starts && !ends) return source;
  if (starts !== 1 || ends !== 1 || source.indexOf(end) < source.indexOf(start)) throw new Error('课程 README 的导航标记异常，保留原文件');
  const before = source.slice(0, source.indexOf(start));
  const after = source.slice(source.indexOf(end) + end.length).replace(/^\r?\n(?:\r?\n)?/, '');
  return before + after;
}
const headingKind = text => /实验|\blabs?\b|labwork|лаборатор|практик/i.test(text) ? 'labs'
  : /讲座|讲义|教材|理论|\blecture|\btheory|теория/i.test(text) ? 'theory'
  : /答辩|defense|защита/i.test(text) ? 'defense'
  : /考试|测试|\bexam|экзамен/i.test(text) ? 'exam' : null;
const labKey = text => text.replace(/[–—]/g, '-').match(/(?:lab(?:work)?|лаб(?:ораторная)?(?:\s+работа)?)\s*([0-9]+(?:[.-][0-9]+)?)/i)?.[1];
const visible = text => text.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1');
const markdownLinks = source => [...source.matchAll(/\[[^\]\n]*\]\(((?:[^()\s]|\([^()\s]*\))*)\)/g)];
function fenceBoundary(line, fence) {
  const match = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
  if (!match) return { fence, boundary: false };
  if (!fence) return { fence: { char: match[1][0], length: match[1].length }, boundary: true };
  if (match[1][0] === fence.char && match[1].length >= fence.length && !match[2].trim()) return { fence: null, boundary: true };
  return { fence, boundary: false };
}
function proseLines(source) {
  let fence = null;
  return source.split(/\r?\n/).filter(line => {
    const result = fenceBoundary(line, fence);
    fence = result.fence;
    return !result.boundary && !fence;
  });
}
function localTarget(file, href) {
  try {
    href = decodeURIComponent(href.split('#')[0]);
    if (!href || /^[a-z]+:/i.test(href)) return null;
    return path.posix.normalize(href.startsWith('/') ? href.slice(1) : path.posix.join(path.posix.dirname(file), href)).replace(/\/$/, '');
  } catch { return null; }
}

export function manualContent(source, file) {
  // The generator manages supplemental links, but the student's status column
  // is editable and must survive regeneration, even for non-Lab assignments.
  const resourceStates = new Map();
  const supplemental = source.includes(resourcesStart) ? source.slice(source.indexOf(resourcesStart), source.indexOf(resourcesEnd)) : '';
  for (const line of proseLines(supplemental)) {
    const state = line.match(/\|\s*(✓ 已通过|○ 待通过|— 未标记)\s*\|\s*$/)?.[1];
    if (!state) continue;
    for (const match of markdownLinks(line)) {
      const target = localTarget(file, match[1]);
      if (target) resourceStates.set(target, state);
    }
  }
  source = stripBlock(source, '<!-- kb:navigation:start -->', '<!-- kb:navigation:end -->');
  source = stripBlock(source, overviewStart, overviewEnd);
  source = stripBlock(source, resourcesStart, resourcesEnd);
  source = source.replace(/<!-- kb:anchor:(?:theory|labs|defense|exam|resources) -->\r?\n<a id="(?:theory|labs|defense|exam|resources)"><\/a>\r?\n/g, '');
  const statuses = new Map(), lines = source.split(/\r?\n/), output = [];
  let context = null, fence = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const boundary = fenceBoundary(line, fence);
    fence = boundary.fence;
    if (boundary.boundary) { output.push(line); continue; }
    if (fence) { output.push(line); continue; }
    const heading = line.match(/^#{1,6}\s+(.+)$/);
    if (heading) context = headingKind(heading[1]);
    const checkbox = line.match(/^\s*[-*]\s+\[([ xX])\]\s+(.+)$/);
    const kind = checkbox && (labKey(visible(checkbox[2])) ? 'labs' : context);
    // Convert only explicitly recorded lab and exam states. Lecture checkboxes
    // keep the author's learning semantics and grouping unchanged.
    if (checkbox && (kind === 'labs' || kind === 'exam')) {
      const rows = [];
      while (i < lines.length) {
        const row = lines[i].match(/^\s*[-*]\s+\[([ xX])\]\s+(.+)$/);
        if (!row) break;
        const label = row[2].trim(), state = /x/i.test(row[1]) ? '✓ 已通过' : '○ 待通过';
        if (kind === 'labs' && labKey(visible(label))) statuses.set(labKey(visible(label)), state);
        rows.push(`| ${label.replaceAll('|', '\\|')} | ${state} |`);
        i++;
      }
      i--;
      if (output.at(-1)?.trim()) output.push('');
      output.push(`| ${kind === 'labs' ? '实验' : '考核'} | 状态 |`, '|---|---|', ...rows, '');
      continue;
    }
    if (/^\|/.test(line) && /✓ 已通过|○ 待通过|— 未标记/.test(line)) {
      const key = labKey(visible(line));
      if (key) statuses.set(key, line.match(/✓ 已通过|○ 待通过|— 未标记/)[0]);
    }
    output.push(line);
  }
  const text = output.join('\n').trimEnd();
  const targets = new Set();
  for (const match of markdownLinks(proseLines(text).join('\n'))) {
    const target = localTarget(file, match[1]);
    if (target) targets.add(target);
  }
  return { text, statuses, targets, resourceStates };
}

export function composeReadme(source, course, categories, link, semesterLinks, related) {
  const from = course.dashboard;
  const manual = manualContent(source, from);
  const headings = new Map();
  let original = manual.text || `# ${course.title} · ${course.ru}`;
  // Existing checklist rows keep their PDF/report links and gain the matching
  // directory entry where it was previously available only in the dashboard.
  let rowFence = null;
  original = original.split('\n').map(line => {
    const boundary = fenceBoundary(line, rowFence); rowFence = boundary.fence;
    if (boundary.boundary || rowFence || !/^\|/.test(line) || !/✓ 已通过|○ 待通过|— 未标记/.test(line)) return line;
    const key = labKey(visible(line));
    const entry = (course.resources.labs || []).find(e => labKey(e.label) === key);
    if (!entry || !key) return line;
    const targets = markdownLinks(line).map(m => localTarget(from, m[1]));
    if (targets.includes(entry.path) || !targets.some(p => p?.startsWith(entry.path + '/'))) return line;
    return line.replace(/\s*\|\s*(✓ 已通过|○ 待通过|— 未标记)\s*\|\s*$/, ` · ${link(from, '实验目录', entry.path)} | $1 |`);
  }).join('\n');
  let fence = null;
  original = original.split('\n').map(line => {
    const boundary = fenceBoundary(line, fence); fence = boundary.fence;
    if (boundary.boundary) return line;
    if (fence) return line;
    const heading = line.match(/^#{2,6}\s+(.+)$/);
    const kind = heading && headingKind(heading[1]);
    if (!kind || headings.has(kind)) return line;
    headings.set(kind, true);
    return `<!-- kb:anchor:${kind} -->\n<a id="${kind}"></a>\n${line}`;
  }).join('\n');
  if (!headings.has('labs') && manual.statuses.size) {
    original = original.replace(/^(\| 实验 \| 状态 \|)$/m, `<!-- kb:anchor:labs -->\n<a id="labs"></a>\n### ${categories.labs}\n\n$1`);
    headings.set('labs', true);
  }
  const linkedManual = manualContent(original, from);
  const available = Object.keys(categories).filter(k => course.resources[k]?.length);
  const overview = `${overviewStart}\n\n${course.title} · ${course.ru}\n\n**课程状态：${courseStatusSummary(course)}**\n\n${link(from, '课程总览', 'navigation/courses.md')} · ${semesterLinks(from, course)} · ${link(from, '知识索引', 'knowledge/index.md')}\n\n${available.map(k => `[${categories[k]}](#${k})`).join(' · ')}\n\n${course.note}\n\n${overviewEnd}`;
  const firstHeading = original.match(/^#{1,6}\s+[^\n]+(?:\n|$)/m);
  const offset = firstHeading ? firstHeading.index + firstHeading[0].length : 0;
  original = original.slice(0, offset).trimEnd() + '\n\n' + overview + '\n\n' + original.slice(offset).replace(/^\n+/, '');
  let additions = '';
  for (const [key, title] of Object.entries(categories)) {
    const entries = course.resources[key] || [];
    let missing = entries.filter(e => !linkedManual.targets.has(e.path) && !(key === 'labs' && [...linkedManual.targets].some(p => p.startsWith(e.path + '/'))));
    if (!headings.has(key) && !entries.length) continue;
    if (!missing.length && headings.has(key)) continue;
    // A source may serve two purposes (e.g. Lab 7 and its defense questions).
    // Keep a useful category entry rather than rendering an empty heading.
    if (!missing.length) missing = entries;
    const anchor = headings.has(key) ? '' : ` <a id="${key}"></a>`;
    additions += `\n## ${headings.has(key) ? '补充：' : ''}${title}${anchor}\n\n`;
    if (key === 'labs') {
      additions += '| 实验 / 作业资料 | 状态 |\n|---|---|\n' + missing.map(e => `| ${link(from, e.label, e.path)} | ${labStatus(course, e, manual)} |`).join('\n') + '\n';
    } else additions += missing.map(e => `- ${link(from, e.label, e.path)}`).join('\n') + '\n';
  }
  additions += `\n## 复习与关联\n\n- ${link(from, '实验答辩入口', 'study/defense.md')} · ${link(from, '考前复习入口', 'study/revision.md')}\n`;
  if (related.length) additions += '- 关联课程：' + related.map(c => link(from, c.title, c.dashboard)).join(' · ') + '\n';
  return original.trimEnd() + `\n\n${resourcesStart}\n` + additions + `\n${resourcesEnd}\n`;
}
