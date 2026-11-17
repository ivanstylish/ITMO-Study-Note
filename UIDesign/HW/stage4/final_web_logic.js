// Explicit routes prevent the old current+1 fallback from sending users into unrelated scenarios.
function routeFor(t,from=current){
 t=t.trim();
 const planRag=[7,11],planT=[14,18,22,68,73,78,79,80],planPaste=[52,56],planClip=[61,65];
 if(/Анализируем…|Сохраняем…/.test(t))return null;
 if(t==='Отмена')return from===42?41:1;
 if(/^(К импорту|Новая обработка|Начать заново)$/.test(t))return 1;
 if(/Выбрать другой|Другой файл|Заменить файл/.test(t))return 2;
 if(t==='К исходному тексту')return from===59?4:3;
 if(t==='К плану')return 27;
 if(t==='К анализу')return planPaste.includes(from)?51:planClip.includes(from)?60:planT.includes(from)?13:6;
 if(t==='К диалогу')return from===51?50:from===60?59:from===13?12:5;
 if(t==='Посмотреть план')return ({6:7,13:14,51:52,60:61})[from]||null;
 if(t==='Отклонить сохранение')return 32;
 if(t==='Отклонить план')return planRag.includes(from)?28:planT.includes(from)?29:planPaste.includes(from)?34:planClip.includes(from)?35:[27,33].includes(from)?37:null;
 if(t==='Сравнить фрагменты')return 33;
 if(t==='К рабочей области')return ({28:5,29:12,34:50,35:59})[from]||1;
 if(t==='Разрешить сохранение')return ({7:10,14:17,22:17,52:55,61:64,68:69,73:74,79:69,80:81})[from]||null;
 if(t==='Анализировать')return ({5:9,12:16,19:25,20:26,21:24,50:54,59:63})[from]||null;
 if(t==='Повторить анализ')return 31;
 if(/^Открыть обработку/.test(t))return 39;
 if(t==='Импортировать')return from===4?59:50;
 if(t==='Открыть в истории')return ({8:39,15:40,53:57,62:66,70:71,75:76})[from]||38;
 if(t==='К списку обработок')return ({57:58,66:67,71:72,76:77})[from]||38;
 if(t==='Открыть историю')return 38;
 if(t==='Открыть рабочую область')return ({39:6,40:13,57:51,66:60,71:13,76:13})[from]||5;
 if(t==='Вернуться к плану')return 22;
 if(t==='Восстановить версию')return 42;
 if(t==='Подтвердить замену')return 43;
 return undefined;
}
function planToggle(from,index){
 if([7,11].includes(from))return from===7?11:7;
 if([52,56].includes(from))return from===52?56:52;
 if([61,65].includes(from))return from===61?65:61;
 if([14,22].includes(from))return index===0?73:68;
 if([18,78].includes(from))return index===0?68:73;
 if([68,79].includes(from))return index===0?78:14;
 if([73,80].includes(from))return index===0?14:78;
 return null;
}
function sourceHistory(p){
 const lines=p.lines.filter(l=>l.b[0]>=260);
 const ids=lines.filter(l=>/^#\d{3}$/.test(l.t));
 const detail={'038':41,'040':36,'041':40,'042':39,'043':57,'044':66,'045':71,'046':76};
 return '<section class="card history-card"><table class="table"><thead><tr><th>Обработка</th><th>Источник</th><th>Дата</th><th>Состояние</th><th></th></tr></thead><tbody>'+ids.map(id=>{
   const y=id.b[1],near=lines.filter(l=>l.b[1]>=y&&l.b[1]<y+70);
   const title=near.find(l=>l.b[0]<600&&l!==id)?.t||id.t;
   const source=near.find(l=>l.b[0]>=650&&l.b[0]<820)?.t||'';
   const date=near.find(l=>/\d{2}\.\d{2}\.\d{4}/.test(l.t))?.t||'';
   const state=near.find(l=>/^(Завершено|Ошибка записи)$/.test(l.t))?.t||'';
   return '<tr data-go="'+detail[id.t.slice(1)]+'"><td><span class="mono">'+esc(id.t)+'</span><div class="item-name">'+esc(title)+'</div></td><td class="muted">'+esc(source)+'</td><td class="mono">'+esc(date)+'</td><td><span class="badge '+(state==='Ошибка записи'?'error':'')+'">'+esc(state)+'</span></td><td>'+ico('arrow')+'</td></tr>';
 }).join('')+'</tbody></table></section>';
}
genericView=function(p){
 if(p.title==='История')return sourceHistory(p);
 const hasSteps=p.lines.some(l=>l.t==='Импорт'&&l.b[0]>260),min=hasSteps?235:145;
 const content=p.lines.filter(l=>l.b[0]>=260&&l.b[1]>=min&&l.b[1]<710).sort((a,b)=>a.b[1]-b.b[1]||a.b[0]-b.b[0]);
 const rows=[];
 for(const line of content){let row=rows.find(r=>Math.abs(r.y-line.b[1])<=10);if(!row){row={y:line.b[1],lines:[]};rows.push(row)}row.lines.push(line)}
 let fileIndex=0;
 const body=rows.map(row=>{
   const ordered=row.lines.sort((a,b)=>a.b[0]-b.b[0]);
   const file=ordered.find(l=>/^inbox\/.+\.md$/.test(l.t));
   const toggle=file?planToggle(p.id,fileIndex++):null;
   const check=toggle?'<input type="checkbox" class="check" data-proto-to="'+toggle+'" aria-label="'+esc(file.t)+'" '+(ordered.some(l=>l.t==='✓')?'checked':'')+'>':'';
   const cells=ordered.filter(l=>l.t!=='✓').map(l=>'<span class="source-cell '+(l.s>=16?'source-heading':/^(Исключено|\+ Создание|Конфликтов нет|Импортирован)$/.test(l.t)?'source-status':'')+'">'+esc(l.t)+'</span>').join('');
   return '<div class="source-row '+(ordered.filter(l=>l.t!=='✓').length===1?'single':'')+'">'+check+cells+'</div>';
 }).join('');
 const bottom=p.lines.filter(l=>l.b[0]>=260&&l.b[1]>715).sort((a,b)=>a.b[0]-b.b[0]);
 const warning=/ошибк|Конфликт|Не удалось/.test(p.title);
 return '<section class="card source-card '+(warning?'source-warning':'')+'"><div class="source-rows">'+body+'</div></section>'+(bottom.length?'<div class="actions">'+bottom.map((l,i)=>{
   const target=routeFor(l.t,p.id);return '<button class="btn '+(i===bottom.length-1&&bottom.length>1?'primary':'')+'" '+(target?'data-go="'+target+'"':'disabled')+'>'+esc(l.t)+'</button>';
 }).join('')+'</div>':'');
};
let selectedModel='Автоматически';
const originalRender=render;
render=function(){
 originalRender();
 if([6,13,51,60].includes(current)){
   const card=document.querySelector('#screen-content .card');
   if(card){card.insertAdjacentHTML('afterbegin','<div class="model-choice"><span>Модель</span><select aria-label="Модель ответа" data-model-selector><option>Автоматически</option><option>Claude Sonnet</option></select></div>');const select=card.querySelector('select');select.value=selectedModel;select.onchange=()=>selectedModel=select.value;}
 }
 document.querySelectorAll('[data-go]').forEach(el=>{
   if(el.closest('.nav')||el.classList.contains('brand')||el.closest('.side-recent')||el.closest('.file-option')||el.closest('tr')||el.classList.contains('neighbor'))return;
   const target=routeFor(el.textContent,current);
   if(target===undefined)return;
   if(target===null){el.removeAttribute('data-go');el.disabled=true;return;}
   el.dataset.go=target;
 });
 document.querySelectorAll('.check').forEach((c,i)=>{
   const target=Number(c.dataset.protoTo)||planToggle(current,i);if(!target)return;
   c.dataset.protoTo=target;c.onchange=()=>go(target);
 });
 // The native graph uses click destinations; free dragging remains available here.
 document.querySelectorAll('.graph-node[data-node]').forEach(el=>el.dataset.protoTo=el.dataset.node);
 const submit=document.querySelector('.actions .primary');
 if(submit&&[11,18,56,65,78].includes(current)){submit.disabled=true;submit.removeAttribute('data-go');}
};
destination=function(t){const route=routeFor(t,current);return route===undefined?null:route;};
render();
