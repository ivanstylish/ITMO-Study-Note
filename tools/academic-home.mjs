import { courseStatus } from './course-status.mjs';

export const homeStart='<!-- kb:home:start -->';
export const homeEnd='<!-- kb:home:end -->';
export function academicYears(catalog) {
  return ['大一','大二','大三','大四'].map((title,index)=>({
    number:index+1,title,period:`${2024+index}–${2025+index}`,
    semesters:[index*2+1,index*2+2].map(number=>({
      number,record:catalog.semesters.find(s=>s.number===number),
      courses:catalog.courses.filter(c=>c.semesters.includes(number))
    }))
  }));
}
export function homeContent(catalog,link) {
  const from='README.md';
  const current=Math.max(...catalog.semesters.map(s=>s.number));
  return academicYears(catalog).map(year=>`## ${year.title} · ${year.period} <a id="year-${year.number}"></a>\n\n${year.semesters.map(s=>{
    const title=`第 ${s.number} 学期${s.record?' · '+s.record.title:''}`;
    const summary=`<details${s.number===current?' open':''}>\n<summary>${title} · ${s.courses.length?s.courses.length+' 门课程':'尚未收录'}</summary>`;
    if(!s.courses.length) return `${summary}\n\n本学期课程资料尚未收录。\n\n</details>`;
    return `${summary}\n\n${link(from,'本学期总览',`academic/semester-${String(s.number).padStart(2,'0')}.md`)}\n\n| 课程 | Русское название | 状态 |\n|---|---|---|\n${s.courses.map(c=>`| ${link(from,c.title,c.dashboard)} | ${c.ru} | ${courseStatus(c,s.number)} |`).join('\n')}\n\n</details>`;
  }).join('\n\n')}`).join('\n\n');
}
export function composeHome(source,catalog,link) {
  if(source.split(homeStart).length!==2 || source.split(homeEnd).length!==2 || source.indexOf(homeEnd)<source.indexOf(homeStart)) throw new Error('首页缺少唯一的学年导航标记');
  return source.slice(0,source.indexOf(homeStart)+homeStart.length)+'\n\n'+homeContent(catalog,link)+'\n\n'+source.slice(source.indexOf(homeEnd));
}
