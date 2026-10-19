import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { composeReadme, courseSections, manualContent } from './course-readme.mjs';
import { composeHome, academicYears, homeStart, homeEnd } from './academic-home.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'navigation/catalog.json'),'utf8'));
const link=(from,label,target)=>`[${label}](${path.posix.relative(path.posix.dirname(from),target).split('/').map(encodeURIComponent).join('/')})`;
const fixture={title:'测试课程',ru:'Курс',dashboard:'Course/readme.md',semesters:[5],status:'unmarked',note:'课程说明',resources:{
  labs:[{label:'Lab 1',path:'Course/lab1'},{label:'Lab 2',note:'资料尚未收录。',status:'pending'},{label:'Lab 3',path:'Course/lab3'}],
  theory:[],assignments:[{label:'课程项目',path:'Course/project'}],exam:[],answers:[]
}};
const compose=(source,c=fixture)=>composeReadme(source,c,courseSections,link,()=>'',[]);

test('all labs stay visible across passed, pending and unmarked states',()=>{
  const c=structuredClone(fixture); c.resources.labs[0].status='passed';
  const out=compose('# 原笔记\n',c);
  assert.match(out,/\[Lab 1\]\(lab1\) \| ✓ 已通过/);
  assert.match(out,/\| Lab 2 \| ○ 待通过 \| 资料尚未收录/);
  assert.match(out,/\[Lab 3\]\(lab3\) \| — 未标记/);
  for(const key of ['labs','theory','assignments','exam','answers']) assert.equal(out.split(`id="${key}"`).length,2);
});
test('editing a state persists, including labs without files and non-lab assignments',()=>{
  let out=compose('# 原笔记\n');
  out=out.replace('[Lab 1](lab1) | — 未标记','[Lab 1](lab1) | ✓ 已通过')
    .replace('Lab 2 | ○ 待通过','Lab 2 | ✓ 已通过')
    .replace('[课程项目](project) | — 未标记','[课程项目](project) | ○ 待通过');
  assert.equal(compose(out),out);
  assert.equal(manualContent(out,fixture.dashboard).resourceStates.get('Course/project'),'○ 待通过');
});
test('handwritten prose and code examples survive without becoming status records',()=>{
  const note='## 我的解释\n\n保留这段说明。\n\n```md\n| [Lab 1](lab1) | ✓ 已通过 |\n```\n';
  const out=compose('# 原标题\n\n'+note);
  assert.ok(out.endsWith(note));
  assert.match(out,/\[Lab 1\]\(lab1\) \| — 未标记/);
  assert.equal(compose(out),out);
});
test('four years include only recorded courses and retain uncollected semesters',()=>{
  const source=`自定义说明\n${homeStart}\n${homeEnd}\n自定义尾注\n`;
  const out=composeHome(source,catalog,link);
  assert.equal((out.match(/^## 大[一二三四]/gm)||[]).length,4);
  assert.equal((out.match(/^### /gm)||[]).length,8);
  assert.equal(academicYears(catalog).flatMap(y=>y.semesters).slice(5).every(s=>s.courses.length===0),true);
  assert.ok(out.startsWith('自定义说明\n'));
  assert.ok(out.endsWith('自定义尾注\n'));
  assert.equal(composeHome(out,catalog,link),out);
});
test('a same-number lab in another course cannot change this course status',()=>{
  const out=compose('# 原笔记\n')+'\n## 延伸阅读\n\n| [Lab 2](../Other/lab2.md) | ✓ 已通过 |\n';
  assert.match(compose(out),/\| Lab 2 \| ○ 待通过/);
});
test('navigation-marker examples in fenced code are preserved',()=>{
  const example='## 维护示例\n\n```md\n<!-- kb:course-resources:start -->\n示例内容\n<!-- kb:course-resources:end -->\n<!-- kb:anchor:labs -->\n<a id="labs"></a>\n```\n';
  const out=compose('# 原笔记\n\n'+example);
  assert.ok(out.endsWith(example));
  assert.equal(compose(out),out);
});
test('all real courses regenerate without duplication or state loss',()=>{
  for(const c of catalog.courses) {
    const input=fs.readFileSync(path.join(root,c.dashboard),'utf8');
    const once=compose(input,c);
    assert.equal(compose(once,c),once,c.id);
    const labs=once.split('## 全部实验')[1].split('\n## ')[0];
    for(const entry of c.resources.labs) assert.ok(labs.includes(entry.label),`${c.id}: ${entry.label}`);
  }
});
