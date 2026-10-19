import { academicYears } from './academic-home.mjs';
import { courseStatus, courseStatusSummary, labStatus } from './course-status.mjs';
import { manualContent, resourceLink, resourceDetails } from './course-readme.mjs';

export function navigationPages(catalog,outputs,link) {
  const pages=new Map();
  const category=(from,c,key,label)=>c.resources[key]?.length?link(from,label,c.dashboard+'#'+key):'—';
  const exams=(from,c)=>[category(from,c,'exam','内容'),category(from,c,'answers','答案')].filter(v=>v!=='—').join(' · ')||'—';
  const columns=(from,c)=>`${category(from,c,'labs',String(c.resources.labs.length)+' 项')} | ${category(from,c,'assignments',String(c.resources.assignments.length)+' 项')} | ${exams(from,c)}`;
  for(const semester of catalog.semesters) {
    const from=`academic/semester-${String(semester.number).padStart(2,'0')}.md`;
    const courses=catalog.courses.filter(c=>c.semesters.includes(semester.number));
    const adjacent=[link(from,'四年课程首页','README.md'),link(from,'全部学期','navigation/index.md')];
    for(const [n,title] of [[semester.number-1,'上一学期'],[semester.number+1,'下一学期']]) if(catalog.semesters.some(s=>s.number===n)) adjacent.push(link(from,title,`academic/semester-${String(n).padStart(2,'0')}.md`));
    pages.set(from,`# 第 ${semester.number} 学期 · ${semester.title}\n\n${adjacent.join(' · ')}\n\n${semester.period} · ${courses.length} 门课程已收录资料。\n\n| 课程 | 考核 | 状态 | 全部实验 | 学期作业 | 考试 |\n|---|---|---|---|---|---|\n${courses.map(c=>`| ${link(from,c.title,c.dashboard)} | ${c.assessments?.[semester.number]||'见课程资料'} | ${courseStatus(c,semester.number)} | ${columns(from,c)} |`).join('\n')}`);
  }
  const overview='navigation/index.md';
  pages.set(overview,`# 学期导航 · Учебные семестры\n\n${link(overview,'四年课程首页','README.md')} · ${link(overview,'全部课程','navigation/courses.md')} · ${link(overview,'复习脑图','knowledge/mindmap.md')}\n\n${academicYears(catalog).map(year=>`## ${year.title} · ${year.period}\n\n| 学期 | 课程资料 |\n|---|---|\n${year.semesters.map(s=>`| ${s.record?link(overview,`第 ${s.number} 学期 · ${s.record.title}`,`academic/semester-${String(s.number).padStart(2,'0')}.md`):`第 ${s.number} 学期`} | ${s.courses.length?`${s.courses.length} 门课程`:'尚未收录'} |`).join('\n')}`).join('\n\n')}\n\n跨学期课程共用同一份课程 README；实验、作业、考试内容和答案按类别查阅。`);
  const all='navigation/courses.md';
  const table=courses=>`| 课程 | 学期 | 状态 | 全部实验 | 学期作业 | 考试 |\n|---|---|---|---|---|---|\n${courses.map(c=>`| ${link(all,c.title,c.dashboard)} | ${c.semesters.join('、')} | ${courseStatusSummary(c)} | ${columns(all,c)} |`).join('\n')}`;
  pages.set(all,`# 课程总览 · Курсы\n\n${link(all,'四年课程首页','README.md')} · ${link(all,'按学期浏览','navigation/index.md')} · ${link(all,'知识地图','knowledge/index.md')}\n\n${catalog.courses.length} 门课程各有一份 README，按实验、讲座教材、学期作业、考试内容与答案查阅。\n\n## 当前学期\n\n${table(catalog.courses.filter(c=>c.semesters.includes(5)))}\n\n## 归档课程\n\n${table(catalog.courses.filter(c=>c.semesters.every(n=>n<5)))}\n\n## 补充学习\n\n${link(all,'Java 基础','Java/Note.md')} · ${link(all,'Java 专题','Java/subtopi.md')} · ${link(all,'Go 源码','Go')} · ${link(all,'预科数学语言','MathsLanguage/keyknowledge.md')} · ${link(all,'Helios','helios.md')}`);
  const labs='navigation/labs.md';
  pages.set(labs,`# 全部实验与学期作业\n\n${link(labs,'四年课程首页','README.md')} · ${link(labs,'答辩指南','study/defense.md')} · ${link(labs,'全部课程','navigation/courses.md')}\n\n✓ 已通过 / ○ 待通过 / — 未标记。各课程展示全部已收录或已明确列出的实验；学期作业单列。\n\n${catalog.courses.filter(c=>c.resources.labs.length||c.resources.assignments.length).map(c=>{
    const manual=manualContent(outputs.get(c.dashboard),c.dashboard);
    return `## ${c.title}\n\n${link(labs,'课程入口',c.dashboard)} · ${courseStatusSummary(c)}\n\n${['labs','assignments'].filter(k=>c.resources[k].length).map(k=>`### ${k==='labs'?'全部实验':'学期作业'}\n\n| ${k==='labs'?'实验':'作业'} | 状态 | 资料与说明 |\n|---|---|---|\n${c.resources[k].map(e=>`| ${resourceLink(labs,e,link)} | ${labStatus(c,e,manual)} | ${resourceDetails(labs,e,link)} |`).join('\n')}`).join('\n\n')}`;
  }).join('\n\n')}`);
  return pages;
}
