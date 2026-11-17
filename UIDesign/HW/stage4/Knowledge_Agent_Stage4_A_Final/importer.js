figma.showUI(__html__, {width:420,height:570,themeColors:true});
let available=[],fonts=new Map(),styles=new Map(),components=new Map(),modelSet=null,modelDefault=null;
let page,library,colorCollection,libraryX=0,libraryY=0,libraryRow=0;
const colorVariables=new Map();
const counts={text:0,vector:0,components:0,links:0,timers:0};
const settingComponents=new Map();
async function settingChoice(d,parent,map){
 const textData=[];function collect(n){if(n.kind==='text')textData.push(n);for(const c of n.children||[])collect(c)}collect(d);
 if(textData.length!==1)return build(d,parent,map);
 const original=textData[0],value=original.text;
 const alternatives={'Personal_Vault':'Research_Vault','D:/Notes/Personal_Vault':'D:/Notes/Research_Vault','inbox/':'notes/','data/knowledge-agent.sqlite':'data/research.sqlite','.knowledge-agent/backups/':'backups/','Claude Sonnet':'Автоматически','Настроен':'Не настроен','Включён':'Выключен','text-embedding-3-small':'text-embedding-3-large','Перед записью':'По запросу','Требуется':'Не требуется','Выключена':'Включена','С резервной копией':'Всегда спрашивать','1 200 токенов':'2 400 токенов','120 токенов':'240 токенов','До 2 попыток':'До 3 попыток'};
 const alternate=alternatives[value];if(!alternate)return build(d,parent,map);
 let component=settingComponents.get(value);
 if(!component){
  const variants=[],width=Math.max(d.w,150),height=Math.max(d.h,original.lineHeight);
  for(const label of [value,alternate]){
   const c=figma.createComponent();c.name='Value='+label;c.resize(width,height);c.x=variants.length*(width+24);c.y=0;c.fills=[];c.clipsContent=false;
   const t=await makeText({...original,text:label,x:0,y:(height-original.lineHeight)/2,w:width,h:original.lineHeight},c);t.textAutoResize='HEIGHT';t.resize(width,Math.max(original.lineHeight,18));t.textAlignHorizontal='RIGHT';variants.push(c);
  }
  const set=figma.combineAsVariants(variants,library);set.name='Setting / '+value;set.description='Preset value choices for the native prototype; no system configuration is changed.';placeInLibrary(set);
  for(let i=0;i<2;i++)await variants[i].setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:variants[1-i].id,navigation:'CHANGE_TO',transition:null,preserveScrollPosition:false}]}]);
  component=variants[0];settingComponents.set(value,component);
 }
 const instance=component.createInstance();parent.appendChild(instance);instance.x=d.x;instance.y=d.y;map.set(d.domId,instance);return instance;
}
function weight(style){const s=style.toLowerCase().replace(/\s/g,'');if(s.includes('black')||s.includes('heavy'))return 900;if(s.includes('extrabold'))return 800;if(s.includes('semibold')||s.includes('demi'))return 600;if(s.includes('bold'))return 700;if(s.includes('medium'))return 500;if(s.includes('extralight'))return 200;if(s.includes('light'))return 300;if(s.includes('thin'))return 100;return 400;}
function face(family,w=400){
 const list=available.filter(f=>f.fontName.family.toLowerCase()===family.toLowerCase()&&!/italic/i.test(f.fontName.style));
 list.sort((a,b)=>Math.abs(weight(a.fontName.style)-w)-Math.abs(weight(b.fontName.style)-w)||weight(a.fontName.style)-weight(b.fontName.style));
 return list[0]?.fontName;
}
function familyOf(d){return /Georgia/i.test(d.font)?'Georgia':/Courier/i.test(d.font)?'Courier New':'Segoe UI';}
function paints(c){
 if(!c||c.a===0)return [];
 const rgb={r:c.r,g:c.g,b:c.b},key=[c.r,c.g,c.b].map(n=>Math.round(n*255)).join('-');
 let variable=colorVariables.get(key);
 if(!variable){variable=figma.variables.createVariable('Garden A / '+key,colorCollection,'COLOR');variable.scopes=['FRAME_FILL','SHAPE_FILL','TEXT_FILL','STROKE_COLOR'];variable.setValueForMode(colorCollection.defaultModeId,rgb);colorVariables.set(key,variable);}
 return [figma.variables.setBoundVariableForPaint({type:'SOLID',color:rgb,opacity:c.a===undefined?1:c.a},'color',variable)];
}
const color=(hex)=>({r:parseInt(hex.slice(1,3),16)/255,g:parseInt(hex.slice(3,5),16)/255,b:parseInt(hex.slice(5,7),16)/255,a:1});
function placeInLibrary(n){
 if(libraryX+n.width>4800){libraryX=0;libraryY+=libraryRow+48;libraryRow=0;}
 library.appendChild(n);n.x=libraryX;n.y=libraryY;libraryX+=n.width+48;libraryRow=Math.max(libraryRow,n.height);
}
function componentKey(d){return JSON.stringify({...d,x:0,y:0},(k,v)=>k==='domId'?undefined:v);}
function configureLayout(n,d){
 const l=d.layout||{},fileRow=d.name==='file-option',fileHead=d.name==='file-table-head';
 if(!fileRow&&!fileHead&&!['flex','inline-flex'].includes(l.display))return false;
 n.layoutMode=l.direction==='column'?'VERTICAL':'HORIZONTAL';
 n.primaryAxisSizingMode=n.counterAxisSizingMode='FIXED';
 n.primaryAxisAlignItems=l.justify==='space-between'?'SPACE_BETWEEN':l.justify==='center'?'CENTER':'MIN';
 n.counterAxisAlignItems=l.align==='center'?'CENTER':l.align==='flex-end'?'MAX':'MIN';
 n.itemSpacing=l.gap||0;
 const p=l.padding||[0,0,0,0];[n.paddingTop,n.paddingRight,n.paddingBottom,n.paddingLeft]=p;
 if(fileRow||fileHead){n.layoutMode='HORIZONTAL';n.primaryAxisAlignItems='MIN';n.counterAxisAlignItems='CENTER';n.itemSpacing=24;}
 return true;
}
function applyBorders(n,b){
 if(!b||!['top','right','bottom','left'].some(k=>b[k]>0)){n.strokes=[];return;}
 n.strokes=paints(b.color);n.strokeAlign='INSIDE';
 const sides=['top','right','bottom','left'].map(k=>b[k]||0);
 if(sides.every(v=>v===sides[0]))n.strokeWeight=sides[0];
 else [n.strokeTopWeight,n.strokeRightWeight,n.strokeBottomWeight,n.strokeLeftWeight]=sides;
}
async function makeText(d,parent){
 const font=face(familyOf(d),d.weight);if(!font)throw Error('Figma 中没有字体 '+familyOf(d));
 const key=JSON.stringify([font,d.fontSize,d.lineHeight,d.letterSpacing]);
 let style=styles.get(key);
 if(!style){style=figma.createTextStyle();style.name='Garden A / '+font.family+' / '+d.fontSize+' / '+font.style+' / '+Math.round(d.lineHeight*10)/10;style.fontName=font;style.fontSize=d.fontSize;style.lineHeight={unit:'PIXELS',value:Math.max(d.fontSize,d.lineHeight)};style.letterSpacing={unit:'PIXELS',value:d.letterSpacing||0};styles.set(key,style);}
 const text=figma.createText();parent.appendChild(text);text.name=d.name||d.text.slice(0,50);text.fontName=font;await text.setTextStyleIdAsync(style.id);text.characters=d.text;text.fills=paints(d.color);
 const multiline=d.text.includes('\n')||d.h>d.lineHeight*1.6;
 if(multiline){text.textAutoResize='HEIGHT';text.resize(Math.max(1,d.w+1.5),Math.max(1,d.h));}else text.textAutoResize='WIDTH_AND_HEIGHT';
 text.textAlignHorizontal=d.align==='right'||d.align==='end'?'RIGHT':d.align==='center'?'CENTER':'LEFT';
 text.x=d.x;text.y=d.y;counts.text++;return text;
}
async function modelSelector(d,parent,map){
 if(!modelSet){
  const width=Math.max(180,d.w),height=Math.max(40,d.h),variants=[];
  async function label(value,container,x,y){const t=await makeText({kind:'text',name:value,text:value,font:'Segoe UI',fontSize:13,weight:400,lineHeight:20,letterSpacing:0,color:color('#232621'),align:'left',x,y,w:width-28,h:20},container);return t;}
  for(const name of ['Auto','Claude','OpenAuto','OpenClaude']){
   const isOpen=name.startsWith('Open');
   const c=figma.createComponent();c.name='State='+name;c.resize(width,height);c.x=variants.length*(width+40);c.y=0;c.fills=paints(color('#ffffff'));c.strokes=paints(color('#dfe5d9'));c.strokeWeight=1;c.strokeAlign='INSIDE';c.cornerRadius=11;c.clipsContent=false;
   await label(name.includes('Claude')?'Claude Sonnet':'Автоматически',c,13,(height-20)/2);
   await label('▾',c,width-23,(height-20)/2);
   if(isOpen){
    const menu=figma.createFrame();c.appendChild(menu);menu.name='Model options';menu.resize(width,88);menu.x=0;menu.y=height+4;menu.fills=paints(color('#ffffff'));menu.strokes=paints(color('#dfe5d9'));menu.strokeWeight=1;menu.strokeAlign='INSIDE';menu.cornerRadius=11;menu.clipsContent=true;
    for(let i=0;i<2;i++){const option=figma.createFrame();menu.appendChild(option);option.name=i?'Choose Claude Sonnet':'Choose automatic';option.resize(width,44);option.x=0;option.y=i*44;option.fills=paints(color(i?'#ffffff':'#f0f7ed'));await label(i?'Claude Sonnet':'Автоматически',option,13,12);}
   }
   variants.push(c);
  }
  modelSet=figma.combineAsVariants(variants,library);modelSet.name='Model selector';modelSet.description='Two editable choices, opened and selected through native prototype variants.';modelSet.resize(modelSet.width,height+92);placeInLibrary(modelSet);modelDefault=variants[0];
  const reaction=to=>[{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:to.id,navigation:'CHANGE_TO',transition:null,preserveScrollPosition:false}]}];
  await variants[0].setReactionsAsync(reaction(variants[2]));await variants[1].setReactionsAsync(reaction(variants[3]));
  for(let i=2;i<4;i++){await variants[i].setReactionsAsync(reaction(variants[i-2]));const options=variants[i].findAll(n=>n.type==='FRAME'&&n.name.startsWith('Choose '));await options[0].setReactionsAsync(reaction(variants[0]));await options[1].setReactionsAsync(reaction(variants[1]));}
 }
 const instance=modelDefault.createInstance();parent.appendChild(instance);instance.x=d.x;instance.y=d.y;map.set(d.domId,instance);return instance;
}
async function build(d,parent,map){
 if(d.kind==='text')return makeText(d,parent);
 if(d.modelSelector)return modelSelector(d,parent,map);
 if(d.reusable){
  const key=componentKey(d);let component=components.get(key);
  if(!component){component=figma.createComponent();component.name='UI / '+d.name;library.appendChild(component);await populate(component,d,new Map());placeInLibrary(component);components.set(key,component);counts.components++;}
  const instance=component.createInstance();parent.appendChild(instance);instance.x=d.x;instance.y=d.y;map.set(d.domId,instance);return instance;
 }
 if(d.kind==='svg'){
  const vector=figma.createNodeFromSvg(d.svg);parent.appendChild(vector);vector.name='Icon / '+d.name;vector.resize(Math.max(.1,d.w),Math.max(.1,d.h));vector.x=d.x;vector.y=d.y;map.set(d.domId,vector);counts.vector++;return vector;
 }
 const frame=figma.createFrame();parent.appendChild(frame);frame.name=d.name;await populate(frame,d,map);frame.x=d.x;frame.y=d.y;map.set(d.domId,frame);return frame;
}
async function populate(n,d,map){
 n.resize(Math.max(.1,d.w),Math.max(.1,d.h));n.fills=paints(d.fill);n.opacity=d.opacity===undefined?1:d.opacity;n.cornerRadius=Math.max(0,Math.min(d.radius||0,d.w/2,d.h/2));n.clipsContent=!!d.clips;applyBorders(n,d.border);
 if(d.checkbox){
  n.cornerRadius=3;n.strokes=paints(color('#71935b'));n.strokeWeight=1;n.strokeAlign='INSIDE';n.fills=paints(color(d.checked?'#34745c':'#ffffff'));
  if(d.checked){const mark=figma.createNodeFromSvg('<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18"><path d="m4 9 3 3 7-7" fill="none" stroke="white" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>');n.appendChild(mark);mark.name='Checked';mark.resize(d.w,d.h);}
  return;
 }
 if(d.dots){let paths='';for(let x=9;x<d.w;x+=19)for(let y=9;y<d.h;y+=19)paths+=`M${x-.6} ${y}a.6 .6 0 1 0 1.2 0a.6 .6 0 1 0-1.2 0 `;const grid=figma.createNodeFromSvg(`<svg xmlns="http://www.w3.org/2000/svg" width="${d.w}" height="${d.h}" viewBox="0 0 ${d.w} ${d.h}"><path d="${paths}" fill="#c8d0bd"/></svg>`);n.appendChild(grid);grid.name='Editable canvas grid';}
 const auto=configureLayout(n,d);
 // Model menus must paint above the answer while keeping their measured position.
 const children=[...(d.children||[])].sort((a,b)=>Number(a.name==='model-choice')-Number(b.name==='model-choice'));
 for(let i=0;i<children.length;i++){const child=children[i];const c=d.name==='setting-row'&&i===children.length-1?await settingChoice(child,n,map):await build(child,n,map);if(auto){c.layoutSizingHorizontal='FIXED';c.layoutSizingVertical='FIXED';if(child.position==='absolute')c.layoutPositioning='ABSOLUTE';}}
 if(d.name==='file-option'&&n.children.length===3)n.children[0].layoutSizingHorizontal='FILL';
 if(d.name==='file-table-head'){
  const spacer=figma.createFrame();n.appendChild(spacer);spacer.name='Action column';spacer.fills=[];spacer.resize(104,1);n.children[0].layoutSizingHorizontal='FILL';
 }
}
async function init(){
 available=await figma.listAvailableFontsAsync();
 const required=['Segoe UI','Georgia','Courier New'];
 const missing=required.filter(f=>!face(f));
 if(!missing.length){for(const family of required)for(const w of [400,600,700]){const f=face(family,w),key=JSON.stringify(f);if(!fonts.has(key)){await figma.loadFontAsync(f);fonts.set(key,f);}}}
 figma.ui.postMessage({type:'ready',missing,fonts:required});
}
figma.ui.onmessage=async message=>{
 if(message.type==='repairOutput'){try{const result=await repairOutputText(figma.currentPage);figma.ui.postMessage({type:'outputRepaired',...result});}catch(error){figma.ui.postMessage({type:'error',text:String(error.message||error)});}return;}
 if(message.type==='centerButtons'){try{const result=await centerOptionButtons(figma.currentPage);figma.ui.postMessage({type:'buttonsCentered',...result});}catch(error){figma.ui.postMessage({type:'error',text:String(error.message||error)});}return;}
 if(message.type==='applyA'){try{const p=figma.currentPage;const frames=currentFrames(p);if(!frames.has(1)||!frames.has(49))throw Error('请选择已经生成的 A Final 页面。');const result=await applyApprovedA(p,frames);figma.ui.postMessage({type:'appearanceApplied',...result});}catch(error){figma.ui.postMessage({type:'error',text:String(error.message||error)});}return;}
 if(message.type==='patch'){
  try{
   page=figma.currentPage;const frames=new Map(page.children.filter(n=>n.type==='FRAME'&&/^\d+ · /.test(n.name)).map(n=>[Number(n.name.split(' · ')[0]),n]));
   if(!frames.has(1)||!frames.has(49))throw Error('请先切换到已生成的 A Final 页面，再补交互。');
   library=page.children.find(n=>n.name==='Components / Garden A');if(!library)throw Error('当前页没有 A Final 组件库。');
   colorCollection=figma.variables.createVariableCollection('Garden A / interaction repair');colorVariables.clear();settingComponents.clear();libraryX=0;libraryY=library.height+48;libraryRow=0;
   let links=0;
   for(const scene of SCENES){const frame=frames.get(scene.id);if(!frame)continue;
    for(const old of frame.children.filter(n=>n.name==='Prototype click targets / locked for editing'))old.remove();
    const layer=figma.createFrame();frame.appendChild(layer);layer.name='Prototype click targets / locked for editing';layer.resize(1363,scene.height);layer.fills=[];layer.clipsContent=false;
    for(const action of scene.actions){const target=frames.get(action.to);if(!target||target===frame)continue;if(target.parent!==page||target.type!=='FRAME')throw Error('导航目标不是当前页的顶层画面：'+action.to);const hot=figma.createRectangle();layer.appendChild(hot);hot.name=action.label;hot.resize(action.w,action.h);hot.x=action.x;hot.y=action.y;hot.fills=[{type:'SOLID',color:{r:1,g:1,b:1},opacity:.001}];hot.strokes=[];await hot.setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:target.id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);links++;}
    layer.locked=true;
   }
   const sourceRows=[];function rows(d){if(d.name==='setting-row')sourceRows.push(d);for(const c of d.children||[])rows(c)}rows(SCENES.find(s=>s.id===49).tree);
   const existingRows=frames.get(49).findAll(n=>n.type==='FRAME'&&n.name==='setting-row');let settings=0;
   if(existingRows.length!==sourceRows.length)throw Error('按钮点击区域已补好；设置页结构与此版本不一致，未修改设置。');
   for(let i=0;i<existingRows.length;i++){const row=existingRows[i],old=row.children[row.children.length-1];if(old.type==='INSTANCE')continue;const d=sourceRows[i].children[sourceRows[i].children.length-1];const replacement=await settingChoice(d,row,new Map());replacement.layoutSizingHorizontal='FIXED';replacement.layoutSizingVertical='FIXED';old.remove();settings++;}
   const restoredTimers=await restoreTimers(page,frames);library.resize(4800,Math.max(library.height,libraryY+libraryRow+48));page.selection=[frames.get(1)];figma.viewport.scrollAndZoomIntoView([frames.get(1)]);figma.ui.postMessage({type:'patched',links,settings,timers:restoredTimers});
  }catch(error){figma.ui.postMessage({type:'error',text:String(error.message||error)});}return;
 }
 if(message.type!=='import')return;
 try{
  if(['Segoe UI','Georgia','Courier New'].some(f=>!face(f)))throw Error('请使用已识别本机字体的 Figma 桌面版运行。');
  components=new Map();styles=new Map();colorVariables.clear();settingComponents.clear();modelSet=modelDefault=null;libraryX=libraryY=libraryRow=0;for(const k of Object.keys(counts))counts[k]=0;
  const current=figma.currentPage;
  const recoverEmpty=current&&current.name==='Knowledge Agent · A Final · Segoe UI'&&current.children.every(n=>n.type==='FRAME'&&['Application','Components / Garden A'].includes(n.name))&&!current.findAll(n=>n.type==='TEXT'&&n.characters.trim()).length;
  if(recoverEmpty){page=current;for(const child of [...page.children])child.remove();}
  else {page=figma.createPage();page.name='Knowledge Agent · A Final · Segoe UI';}
  await figma.setCurrentPageAsync(page);
  colorCollection=figma.variables.createVariableCollection('Garden A');
  library=figma.createFrame();page.appendChild(library);library.name='Components / Garden A';library.fills=[];library.clipsContent=false;library.resize(4800,100);library.x=0;library.y=Math.ceil(SCENES.length/4)*1100+160;
  const frames=new Map(),maps=new Map();
  for(let i=0;i<SCENES.length;i++){
   const scene=SCENES[i],map=new Map();figma.ui.postMessage({type:'progress',text:`生成 ${i+1}/${SCENES.length}：${scene.name}`});
   const frame=await build({...scene.tree,x:(i%4)*1483,y:Math.floor(i/4)*1100},page,map);frame.name=String(scene.id).padStart(2,'0')+' · '+scene.name;frame.resize(1363,936);frame.clipsContent=true;frame.overflowDirection='VERTICAL';const sidebar=frame.children.find(n=>n.name==='sidebar');if(sidebar&&'scrollBehavior'in sidebar)sidebar.scrollBehavior='FIXED';frames.set(scene.id,frame);maps.set(scene.id,map);
  }
  const unresolved=[];
  for(const scene of SCENES){const map=maps.get(scene.id);const clickLayer=figma.createFrame();frames.get(scene.id).appendChild(clickLayer);clickLayer.name='Prototype click targets / locked for editing';clickLayer.resize(1363,scene.height);clickLayer.fills=[];clickLayer.clipsContent=false;
   for(const action of scene.actions){
    const node=map.get(action.domId),target=frames.get(action.to);
    if(target===frames.get(scene.id))continue;
    if(target&&(target.parent!==page||target.type!=='FRAME'))throw Error('导航目标不是当前页的顶层画面：'+action.to);
    if(!node||!target){unresolved.push({from:scene.id,label:action.label,to:action.to});continue;}
    await node.setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:target.id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);counts.links++;
    const hot=figma.createRectangle();clickLayer.appendChild(hot);hot.name=action.label;hot.resize(action.w,action.h);hot.x=action.x;hot.y=action.y;hot.fills=[{type:'SOLID',color:{r:1,g:1,b:1},opacity:.001}];hot.strokes=[];await hot.setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:target.id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);
   }
   clickLayer.locked=true;
   const next={9:6,10:8,16:13,17:15,23:15,54:51,55:53,63:60,64:62,69:70,74:75,81:70}[scene.id];
   if(next){await frames.get(scene.id).setReactionsAsync([{trigger:{type:'AFTER_TIMEOUT',timeout:1.9},actions:[{type:'NODE',destinationId:frames.get(next).id,navigation:'NAVIGATE',transition:null,preserveScrollPosition:false}]}]);counts.timers++;}
  }
  library.resize(4800,Math.max(100,libraryY+libraryRow+48));
  page.flowStartingPoints=[{nodeId:frames.get(1).id,name:'Главный сценарий'},{nodeId:frames.get(44).id,name:'Граф знаний'},{nodeId:frames.get(41).id,name:'Восстановление версии'}];
  await applyApprovedA(page,frames);await centerOptionButtons(page);await repairOutputText(page);
  const nodes=page.findAll(()=>true),types={};for(const n of nodes)types[n.type]=(types[n.type]||0)+1;
  const images=nodes.filter(n=>'fills'in n&&Array.isArray(n.fills)&&n.fills.some(p=>p.type==='IMAGE'));
  if(images.length||unresolved.length)throw Error('验证未通过：图片层 '+images.length+'，未连接操作 '+unresolved.length);
  page.selection=[frames.get(1)];figma.viewport.scrollAndZoomIntoView([frames.get(1)]);
  figma.ui.postMessage({type:'done',screens:SCENES.length,mainScreens:81,...counts,types,imageLayers:images.length,unresolved,frameIds:[...frames.values()].map(n=>n.id),createdNodeIds:nodes.map(n=>n.id)});
 }catch(error){figma.ui.postMessage({type:'error',text:String(error.message||error)});}
};
init().catch(error=>figma.ui.postMessage({type:'error',text:String(error.message||error)}));
