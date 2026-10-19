import path from 'node:path';
import { courseStatusSummary, labStatus } from './course-status.mjs';

export const overviewStart = '<!-- kb:course-overview:start -->';
export const overviewEnd = '<!-- kb:course-overview:end -->';
export const resourcesStart = '<!-- kb:course-resources:start -->';
export const resourcesEnd = '<!-- kb:course-resources:end -->';
export const courseSections = Object.freeze({ labs: '全部实验', theory: '讲座与教材', assignments: '学期作业', exam: '考试内容', answers: '考试答案与解答', defense: '实验答辩', resources: '补充资料与速查' });
const states = /✓ 已通过|○ 待通过|— 未标记/;
const links = source => [...source.matchAll(/\[([^\]\n]*)\]\(((?:[^()\s]|\([^()\s]*\))*)\)/g)];
export const labKey = text => text.replace(/[–—]/g, '-').match(/(?:lab(?:work)?|work|УИР|лаб(?:ораторная)?(?:\s+работа)?)\s*([0-9]+(?:[.-][0-9]+)?)/i)?.[1];
function target(file, href) {
  try {
    const clean=decodeURIComponent(href.split('#')[0]);
    if (!clean || /^[a-z]+:/i.test(clean)) return null;
    return path.posix.normalize(clean.startsWith('/') ? clean.slice(1) : path.posix.join(path.posix.dirname(file), clean)).replace(/\/$/,'');
  } catch { return null; }
}
function sourceLines(source) {
  let fence=null,offset=0;
  return source.split('\n').map(raw=>{
    const line=raw.replace(/\r$/,''),record={text:line,start:offset,end:offset+raw.length,prose:!fence};
    offset+=raw.length+1;
    const match=line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if(match) {
      if(!fence) { fence={char:match[1][0],length:match[1].length}; record.prose=false; }
      else if(match[1][0]===fence.char && match[1].length>=fence.length && !match[2].trim()) { fence=null; record.prose=false; }
    }
    return record;
  });
}
function prose(source) { return sourceLines(source).filter(line=>line.prose).map(line=>line.text); }
function blockBounds(source,start,end) {
  const lines=sourceLines(source).filter(line=>line.prose);
  const starts=lines.filter(line=>line.text.trim()===start),ends=lines.filter(line=>line.text.trim()===end);
  if(!starts.length && !ends.length) return null;
  if(starts.length!==1 || ends.length!==1 || ends[0].start<starts[0].start) throw new Error('课程 README 的导航标记异常，保留原文件');
  return {start:starts[0].start,end:ends[0].end};
}
function stripBlock(source,start,end) {
  const bounds=blockBounds(source,start,end);
  return bounds ? source.slice(0,bounds.start)+source.slice(bounds.end).replace(/^\r?\n(?:\r?\n)?/,'') : source;
}
export function manualContent(source,file) {
  const resourceStates=new Map(), statuses=new Map();
  const bounds=blockBounds(source,resourcesStart,resourcesEnd);
  const stateSource=bounds?source.slice(bounds.start,bounds.end):source;
  let labs=false;
  for(const line of prose(stateSource)) {
    if(/^#{1,6}\s/.test(line)) labs=/实验|\blabs?\b|labwork|лаборатор/i.test(line);
    const state=line.match(states)?.[0];
    if(!/^\|/.test(line) || !state) continue;
    const key=labKey(line.replace(/\[([^\]]+)\]\([^)]*\)/g,'$1'));
    const primary=links(line)[0];
    const fileTarget=primary && target(file,primary[2]);
    if(fileTarget?.startsWith(path.posix.dirname(file)+'/')) resourceStates.set(fileTarget,state);
    if(labs && key && !primary) statuses.set(key,state);
  }
  let text=stripBlock(source,overviewStart,overviewEnd);
  text=stripBlock(text,resourcesStart,resourcesEnd);
  text=stripBlock(text,'<!-- kb:navigation:start -->','<!-- kb:navigation:end -->');
  const lines=sourceLines(text);
  text=lines.filter((line,index)=>!(line.prose && (/^<!-- kb:anchor:[\w-]+ -->$/.test(line.text) || /^<a id="[\w-]+"><\/a>$/.test(line.text) && /^<!-- kb:anchor:[\w-]+ -->$/.test(lines[index-1]?.text)))).map(line=>line.text).join('\n').trimEnd();
  const targets=new Set(links(prose(text).join('\n')).map(m=>target(file,m[2])).filter(Boolean));
  return {text,statuses,resourceStates,targets};
}
export function resourceLink(from,entry,link) {
  return entry.path ? link(from,entry.label,entry.path) : entry.label;
}
export function resourceDetails(from,entry,link) {
  return [...(entry.links||[]).map(e=>resourceLink(from,e,link)),entry.note].filter(Boolean).join(' · ') || '—';
}
export function composeReadme(source,course,categories,link,semesterLinks,related) {
  const from=course.dashboard, manual=manualContent(source,from);
  const original=manual.text.replace(/^#{1,6}\s+[^\n]+(?:\n|$)/,'').trim();
  const intro=`# ${course.title} · ${course.ru}\n\n${overviewStart}\n\n${link(from,'主页','README.md')} · ${semesterLinks(from,course)} · ${link(from,'课程总览','navigation/courses.md')}\n\n**课程状态：${courseStatusSummary(course)}**\n\n${Object.entries(categories).filter(([k])=>['labs','theory','assignments','exam','answers'].includes(k) || course.resources[k]?.length).map(([k,title])=>`[${title}](#${k})`).join(' · ')}\n\n${course.note}\n\n${overviewEnd}`;
  const empty={labs:'尚未收录实验清单。',theory:'讲座与教材尚未收录。',assignments:'学期作业尚未收录。',exam:'考试范围与题目尚未收录。',answers:'考试答案尚未收录。'};
  const sections=[];
  for(const [key,title] of Object.entries(categories)) {
    const entries=course.resources[key]||[];
    if(!entries.length && !(key in empty)) continue;
    let section=`## ${title} <a id="${key}"></a>\n\n`;
    if(!entries.length) section+=empty[key];
    else if(key==='labs' || key==='assignments') {
      section+=`| ${key==='labs'?'实验':'作业'} | 状态 | 资料与说明 |\n|---|---|---|\n`;
      section+=entries.map(e=>`| ${resourceLink(from,e,link)} | ${labStatus(course,e,manual)} | ${resourceDetails(from,e,link)} |`).join('\n');
    } else {
      let lastGroup=null;
      section+=entries.map(e=>{
        const group=e.group && e.group!==lastGroup ? `\n### ${e.group}\n\n` : '';
        lastGroup=e.group;
        return `${group}- ${resourceLink(from,e,link)}${e.note?' · '+e.note:''}`;
      }).join('\n');
    }
    sections.push(section);
  }
  sections.push(`## 复习与关联\n\n${link(from,'考前复习','study/revision.md')} · ${link(from,'实验答辩','study/defense.md')} · ${link(from,'知识地图','knowledge/index.md')}${related.length?'\n\n关联课程：'+related.map(c=>link(from,c.title,c.dashboard)).join(' · '):''}`);
  return `${intro}\n\n${resourcesStart}\n\n${sections.join('\n\n')}\n\n${resourcesEnd}${original?'\n\n'+original:''}\n`;
}
