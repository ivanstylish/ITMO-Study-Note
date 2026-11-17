const TIMER_TARGETS={9:6,10:8,16:13,17:15,23:15,54:51,55:53,63:60,64:62,69:70,74:75,81:70};
function currentFrames(p){return new Map(p.children.filter(n=>n.type==='FRAME'&&/^\d+ · /.test(n.name)).map(n=>[Number(n.name.split(' · ')[0]),n]));}
function validateTimers(p,frames){
 for(const [from,to] of Object.entries(TIMER_TARGETS)){
  const source=frames.get(+from),target=frames.get(to);
  if(!source||!target||source===target||source.parent!==p||target.parent!==p||target.type!=='FRAME')throw Error('自动跳转所需画面缺失或不在当前页：'+from+' → '+to);
 }
}
async function restoreTimers(p,frames){
 validateTimers(p,frames);let count=0;
 for(const [from,to] of Object.entries(TIMER_TARGETS)){
  const source=frames.get(+from),target=frames.get(to);
  const retained=source.reactions.filter(r=>r.trigger&&r.trigger.type!=='AFTER_TIMEOUT');
  await source.setReactionsAsync([...retained,{trigger:{type:'AFTER_TIMEOUT',timeout:1.9},actions:[{type:'NODE',destinationId:target.id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);
  if(!source.reactions.some(r=>r.trigger&&r.trigger.type==='AFTER_TIMEOUT'&&(r.actions||[r.action]).some(a=>a&&a.destinationId===target.id)))throw Error('自动跳转未写入：'+from);
  count++;
 }
 return count;
}
function approvedPaint(c){return c&&c.a!==0?[{type:'SOLID',color:{r:c.r,g:c.g,b:c.b},opacity:c.a===undefined?1:c.a}]:[];}
async function applyApprovedA(p,frames){
 validateTimers(p,frames);
 const touched=new Set(),mismatches=[],visitedComponents=new Set(),fontWarnings=[];
 const loaded=async f=>{const key=JSON.stringify(f);if(!fonts.has(key)){await figma.loadFontAsync(f);fonts.set(key,f);}};
 async function textAppearance(n,s){
  if(s.colorChanged&&s.color)n.fills=approvedPaint(s.color);
  if(s.weightChanged){
   const segments=n.getStyledTextSegments(['fontName']);
   for(const segment of segments){const target=face(segment.fontName.family,s.weight);if(!target){fontWarnings.push(n.id);continue;}await loaded(segment.fontName);await loaded(target);if(segments.length===1)n.fontName=target;else n.setRangeFontName(segment.start,segment.end,target);}
  }
  touched.add(n.id);
 }
 function svgAppearance(n,s){
  if(!s.svgColors||!Object.keys(s.svgColors).length)return;
  for(const child of [n,...('findAll'in n?n.findAll(()=>true):[])])for(const prop of ['fills','strokes']){
   if(!(prop in child)||!Array.isArray(child[prop]))continue;
   let changed=false;const next=child[prop].map(paint=>{
    if(paint.type!=='SOLID')return paint;const key=[paint.color.r,paint.color.g,paint.color.b].map(v=>Math.round(v*255)).join(',');const c=s.svgColors[key];if(!c)return paint;
    changed=true;const next={...paint,color:{r:c[0],g:c[1],b:c[2]}};if(next.boundVariables){next.boundVariables={...next.boundVariables};delete next.boundVariables.color;}return next;
   });if(changed){child[prop]=next;touched.add(child.id);}
  }
 }
 function firstText(s){if(s.kind==='text')return s;for(const c of s.children||[]){const found=firstText(c);if(found)return found;}return null;}
 async function apply(n,s,path){
  if(s.checkbox)return;
  if(s.kind==='text'){if(n.type==='TEXT')await textAppearance(n,s);else mismatches.push(path);return;}
  if(s.kind==='svg'){svgAppearance(n,s);return;}
  if(s.fillChanged&&s.fill&&'fills'in n&&Array.isArray(n.fills))n.fills=approvedPaint(s.fill);
  if(s.borderColorChanged&&s.border&&s.border.color&&['top','right','bottom','left'].some(k=>s.border[k]>0)&&'strokes'in n&&Array.isArray(n.strokes)&&n.strokes.length)n.strokes=approvedPaint(s.border.color);
  if(s.opacityChanged)n.opacity=s.opacity;
  touched.add(n.id);
  if(n.type==='INSTANCE'&&n.getMainComponentAsync){
   const main=await n.getMainComponentAsync();
   if(main&&main.name.startsWith('UI / ')&&!visitedComponents.has(main.id)){visitedComponents.add(main.id);await apply(main,s,path+'/main');}
  }
  if(s.modelSelector){const sample=firstText(s);if(sample)for(const t of n.findAll(c=>c.type==='TEXT'))await textAppearance(t,sample);return;}
  if(!('children'in n))return;
  const used=new Set();
  const ordered=[...(s.children||[])].sort((a,b)=>Number(a.name==='model-choice')-Number(b.name==='model-choice'));
  for(let i=0;i<ordered.length;i++){
   const child=ordered[i];let target=n.children.find(c=>!used.has(c.id)&&[child.name,'UI / '+child.name,'Icon / '+child.name].includes(c.name));
   if(!target&&(child.modelSelector||s.name==='setting-row'&&i===ordered.length-1))target=n.children[i];
   if(!target){mismatches.push(path+'/'+child.name);continue;}used.add(target.id);await apply(target,child,path+'/'+child.name);
  }
 }
 for(let i=0;i<APPROVED_STYLES.length;i++){
  const style=APPROVED_STYLES[i],frame=frames.get(style.id);if(!frame)continue;
  await apply(frame,style.tree,String(style.id));
  if(i%10===0)figma.ui.postMessage({type:'progress',text:'应用已确认的 A 配色与字重：'+(i+1)+'/'+APPROVED_STYLES.length});
 }
 // Preset choices have extra native variants that do not exist in the browser DOM.
 const lib=p.children.find(n=>n.name==='Components / Garden A');
 if(lib)for(const set of lib.children.filter(n=>n.type==='COMPONENT_SET'&&(n.name==='Model selector'||n.name.startsWith('Setting / ')))){
  for(const t of set.findAll(n=>n.type==='TEXT'))await textAppearance(t,{color:color('#202b1b'),colorChanged:true,weight:600,weightChanged:set.name.startsWith('Setting / ')});
  if(set.name==='Model selector')for(const n of set.findAll(n=>'strokes'in n&&Array.isArray(n.strokes)&&n.strokes.length)){n.strokes=approvedPaint(color('#b5c2aa'));touched.add(n.id);}
 }
 const timers=await restoreTimers(p,frames);
 return {styleNodes:touched.size,timers,mismatches,fontWarnings,frameCount:frames.size};
}
