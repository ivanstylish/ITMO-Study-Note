import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const notes = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const labs = path.dirname(notes);
const typst = path.join(labs, 'lab1-intro-ex/report-review-20261012/tools/typst-x86_64-pc-windows-msvc/typst.exe');
const tasks = [
  { project: 'intro', slug: '1', title: 'Введение в xv6: Pingpong, Dump и Dump2', number: ' № 1' },
  { project: 'shebang', slug: 'shebang', title: 'Поддержка Shebang в xv6', number: '' },
];
const selectedProject = process.argv[2];
if (selectedProject && !tasks.some(task => task.project === selectedProject)) {
  throw new Error('Usage: node build-reports.mjs [intro|shebang]');
}

function escape(text) {
  return text.replace(/[\u2010-\u2015\u2212]/g, '-').replace(/[\\#[\]*_$<>`@]/g, '\\$&');
}

function inline(text) {
  const token = /`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)/g;
  let result = '', cursor = 0;
  for (const match of text.matchAll(token)) {
    result += escape(text.slice(cursor, match.index));
    result += match[1] !== undefined
      ? `#raw(${JSON.stringify(match[1])}, block: false)`
      : `#link(${JSON.stringify(match[3])})[${escape(match[2])}]`;
    cursor = match.index + match[0].length;
  }
  return result + escape(text.slice(cursor));
}

function wrapCommand(line) {
  if (line.length <= 88) return line;
  const words = line.match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) ?? [line];
  const lines = [];
  let current = '';
  for (const word of words) {
    if (current && current.length + word.length + 1 > 84) {
      lines.push(`${current} \\`);
      current = `  ${word}`;
    } else current += `${current ? ' ' : ''}${word}`;
  }
  lines.push(current);
  return lines.join('\n');
}

function markdownToTypst(markdown, task) {
  const lines = markdown.replace(/\r\n/g, '\n').replace(/[\u2010-\u2015\u2212]/g, '-').split('\n');
  const output = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^# |^Студент:|^Преподаватель:/.test(line)) continue;
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const body = [];
      while (++i < lines.length && !lines[i].startsWith('```')) {
        body.push(lang === 'bash' ? wrapCommand(lines[i]) : lines[i]);
      }
      output.push(`#block(width: 100%, fill: luma(96%), inset: 8pt)[#raw(${JSON.stringify(body.join('\n'))}, block: true, lang: ${JSON.stringify(lang)})]`);
    } else if (line.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) {
        if (!/^\|[\s:|-]+\|$/.test(lines[i])) {
          rows.push(lines[i].slice(1, -1).split('|').map(cell => cell.trim()));
        }
        i++;
      }
      i--;
      const columns = rows[0].length === 2 ? '(36%, 64%)' : `(${rows[0].map(() => '1fr').join(', ')})`;
      const header = `table.header(${rows[0].map(cell => `[${inline(cell)}]`).join(', ')}),`;
      output.push(`#table(columns: ${columns}, ${header}\n${rows.slice(1).map(row => row.map((cell, column) => `[${column === 0 ? inline(cell).replace(/, #raw\(/g, ', #linebreak()#raw(') : inline(cell)}]`).join(', ') + ',').join('\n')}\n)`);
    } else if (/^#{2,3} /.test(line)) {
      const level = line.match(/^#+/)[0].length - 1;
      if (task.project === 'intro' && line === '## Ход работы') {
        let linkLine = i + 1;
        while (linkLine < lines.length && !lines[linkLine].trim()) linkLine++;
        if (lines[linkLine]?.startsWith('Ссылка на выполненную работу:')) {
          output.push(`#block(sticky: true)[\n= ${inline(line.replace(/^#+ /, ''))}\n\n${inline(lines[linkLine])}\n]`);
          i = linkLine;
          continue;
        }
      }
      output.push(`${'='.repeat(level)} ${inline(line.replace(/^#+ /, ''))}`);
    } else {
      const next = lines.slice(i + 1).find(candidate => candidate.trim());
      output.push(line.endsWith(':') && next?.startsWith('```')
        ? `#block(sticky: true)[${inline(line)}]`
        : inline(line));
    }
  }
  return output.join('\n');
}

function cover(task) {
  return `#set document(title: ${JSON.stringify(task.title)}, author: "Чжун Цзяцзюнь")
#set page(paper: "a4", margin: (top: 2.5cm, bottom: 2cm, left: 3cm, right: 1.5cm))
#set text(size: 12pt, lang: "ru")
#set par(justify: true)
#align(center)[Федеральное государственное автономное образовательное]
#align(center)[учреждение высшего образования]
#align(center)[«Национальный исследовательский университет ИТМО»]
#v(0.4cm)
#align(center)[Факультет программной инженерии и компьютерной техники]
#v(0.2cm)
#align(center)[Направление подготовки 09.03.04 «Программная инженерия» -]
#align(center)[Системное и прикладное программное обеспечение]
#v(2.5cm)
#align(center)[#text(size: 20pt, weight: "bold")[ОТЧЁТ]]
#align(center)[#text(size: 17pt, weight: "bold")[ПО ЛАБОРАТОРНОЙ РАБОТЕ${task.number}]]
#v(0.5cm)
#align(center)[#text(size: 15pt)[«${escape(task.title)}»]]
#v(1.8cm)
#align(right, block(width: 6.5cm)[
  #set par(justify: false, leading: 0.65em)
  *Выполнил:* \\
  студент группы P3310 \\
  Чжун Цзяцзюнь
  #v(0.6cm)
  *Проверил:* \\
  преподаватель \\
  Максимов Андрей Николаевич
])
#v(1fr)
#align(center)[2026 г.]
#pagebreak()
#set text(size: 11pt, lang: "ru")
#set par(justify: true, leading: 0.45em)
#set heading(numbering: "1.")
#set page(numbering: "1", number-align: center)
#set table(inset: 3.5pt, stroke: 0.4pt)
#show table: set text(size: 9.5pt)
#show raw: set text(size: 8pt)
`;
}

for (const task of tasks) {
  if (selectedProject && task.project !== selectedProject) continue;
  const repo = path.join(labs, `xv6-${task.project}`);
  const markdown = fs.readFileSync(path.join(repo, 'REPORT.md'), 'utf8');
  if (/[；;]/.test(markdown)) throw new Error(`Unexpected report punctuation: ${task.project}`);
  const source = path.join(repo, 'report.typ');
  const outdir = path.join(repo, 'output/pdf');
  fs.mkdirSync(outdir, { recursive: true });
  const output = path.join(outdir, `ЛР(${task.slug}) P3310 Чжун Цзяцзюнь.pdf`);
  fs.writeFileSync(source, cover(task) + markdownToTypst(markdown, task), 'utf8');
  const result = spawnSync(typst, ['compile', source, output], { encoding: 'utf8' });
  if (result.status !== 0) throw new Error(result.stderr || `Typst failed: ${task.project}`);
  console.log(output);
}
