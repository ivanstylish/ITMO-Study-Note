const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const registry=new Map(),textStyles=new Map();let sequence=0,readyResolve,done,patched,appearance,centered,outputRepaired;
class Node {
 constructor(type){this.id=String(++sequence);this.type=type;this.name=type;this.children=[];this.x=this.y=0;this.width=this.height=100;this.fills=[];this.strokes=[];this.reactions=[];this.layoutMode='NONE';this.opacity=1;this.fontSize=14;this.lineHeight={unit:'PIXELS',value:21};registry.set(this.id,this);}
 appendChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}
 remove(){if(this.parent)this.parent.children=this.parent.children.filter(n=>n!==this);}
 resize(w,h){assert(Number.isFinite(w)&&Number.isFinite(h)&&w>0&&h>0,[this.name,w,h].join(' / '));this.width=w;this.height=h;}
 set layoutSizingHorizontal(value){assert(['FIXED','FILL','HUG'].includes(value));if(value==='FILL')assert(this.parent&&this.parent.layoutMode!=='NONE');this.horizontal=value;}
 set layoutSizingVertical(value){assert(['FIXED','FILL','HUG'].includes(value));this.vertical=value;}
 set textStyleId(id){throw new Error('Synchronous textStyleId is forbidden with dynamic-page');}
 async getMainComponentAsync(){return this.mainComponent||null;}
 getStyledTextSegments(){return [{start:0,end:this.characters.length,fontName:this.fontName}];}
 async setTextStyleIdAsync(id){const style=textStyles.get(id);assert(style);this.fontName=style.fontName;this.fontSize=style.fontSize;this.lineHeight=style.lineHeight;}
 set characters(value){assert(this.type==='TEXT');assert(loaded.has(JSON.stringify(this.fontName)),'Font must load before editing');this.text=value;if(['Button text measurement','Output text measurement'].includes(this.name)){this.width=Math.max(1,value.length*this.fontSize*.6);this.height=this.fontSize*1.5;}}
 get absoluteTransform(){let x=this.x,y=this.y,p=this.parent;while(p){x+=p.x;y+=p.y;p=p.parent;}return [[1,0,x],[0,1,y]];}
 get characters(){return this.text||'';}
 findAll(predicate){const result=[];for(const c of this.children){if(predicate(c))result.push(c);result.push(...c.findAll(predicate))}return result;}
 async setReactionsAsync(reactions){for(const r of reactions){assert(['ON_CLICK','AFTER_TIMEOUT'].includes(r.trigger.type));for(const a of r.actions){assert(registry.has(a.destinationId));assert(['NAVIGATE','CHANGE_TO'].includes(a.navigation));const target=registry.get(a.destinationId);if(a.navigation==='NAVIGATE'){let source=this;while(source.parent&&source.parent.type!=='PAGE')source=source.parent;assert.equal(target.type,'FRAME');assert(target.parent&&target.parent.type==='PAGE');assert.equal(target.parent,source.parent);assert.notEqual(target,source,'NAVIGATE cannot target the current top-level frame');}else{let owner=this;while(owner&&owner.type!=='COMPONENT')owner=owner.parent;assert(owner&&owner.parent&&owner.parent.type==='COMPONENT_SET');assert.equal(target.parent,owner.parent);assert.notEqual(owner,target);}}}this.reactions=reactions;}
 clone(asInstance=false){const copy=new Node(asInstance?'INSTANCE':this.type);for(const [k,v]of Object.entries(this)){if(['id','type','children','parent'].includes(k))continue;copy[k]=typeof v==='object'&&v!==null?structuredClone(v):v;}for(const child of this.children)copy.appendChild(child.clone());return copy;}
 createInstance(){assert(this.type==='COMPONENT');const copy=this.clone(true);copy.mainComponent=this;return copy;}
}
const loaded=new Set();
const fontNames=['Segoe UI','Georgia','Courier New'].flatMap(family=>['Regular','Semibold','Bold','Black'].map(style=>({fontName:{family,style}})));
const figma={
 showUI(){},ui:{postMessage(m){if(m.type==='ready')readyResolve(m);if(m.type==='patched')patched=m;if(m.type==='appearanceApplied')appearance=m;if(m.type==='buttonsCentered')centered=m;if(m.type==='outputRepaired')outputRepaired=m;if(m.type==='done'||m.type==='error')done=m;}},
 root:new Node('DOCUMENT'),currentPage:null,
 listAvailableFontsAsync:async()=>fontNames,
 loadFontAsync:async font=>{assert(fontNames.some(f=>JSON.stringify(f.fontName)===JSON.stringify(font)));loaded.add(JSON.stringify(font));},
 createPage(){const n=new Node('PAGE');this.root.appendChild(n);return n;},
 setCurrentPageAsync:async page=>{figma.currentPage=page;},
 createFrame:()=>new Node('FRAME'),createComponent:()=>new Node('COMPONENT'),createText:()=>new Node('TEXT'),createRectangle:()=>new Node('RECTANGLE'),
 createTextStyle(){const style={id:'style-'+(++sequence)};textStyles.set(style.id,style);return style;},
 createNodeFromSvg(svg){assert(svg.includes('viewBox='),'SVG requires its original coordinate system');assert(!svg.includes('<image'),'UI must not be rasterized');const frame=new Node('FRAME');const width=+(svg.match(/width="([\d.]+)"/)||[])[1],height=+(svg.match(/height="([\d.]+)"/)||[])[1];frame.resize(width,height);frame.appendChild(new Node('VECTOR'));return frame;},
 combineAsVariants(variants,parent){const n=new Node('COMPONENT_SET');n.resize(Math.max(...variants.map(v=>v.x+v.width)),Math.max(...variants.map(v=>v.y+v.height)));parent.appendChild(n);for(const v of variants)n.appendChild(v);return n;},
 variables:{
  createVariableCollection:()=>({id:'collection-'+(++sequence),defaultModeId:'default'}),
  createVariable(name,collection,type){assert.equal(type,'COLOR');return {id:'variable-'+(++sequence),name,collection,setValueForMode(mode,value){assert.equal(mode,'default');assert(Object.values(value).every(v=>v>=0&&v<=1));}};},
  setBoundVariableForPaint:(paint,field,variable)=>({...paint,boundVariables:{[field]:{type:'VARIABLE_ALIAS',id:variable.id}}})
 },viewport:{scrollAndZoomIntoView(){}},
};
async function main(){
 const ready=new Promise(r=>readyResolve=r),context=vm.createContext({figma,__html__:'',console});
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'scenes.json'),'utf8'));context.SCENES=data;context.APPROVED_STYLES=JSON.parse(fs.readFileSync(path.join(__dirname,'approved-a-styles.json'),'utf8'));
 vm.runInContext(fs.readFileSync(path.join(__dirname,'approved-a-patch.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'button-layout-patch.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'output-text-patch.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(__dirname,'importer.js'),'utf8'),context);
 const fonts=await ready;assert.equal(fonts.missing.length,0);
 const abandoned=figma.createPage();abandoned.name='Knowledge Agent · A Final · Segoe UI';const blank=new Node('FRAME');blank.name='Application';abandoned.appendChild(blank);figma.currentPage=abandoned;
 await figma.ui.onmessage({type:'import'});
 assert(done&&done.type==='done',JSON.stringify(done));
 assert.equal(done.screens,91);assert.equal(done.imageLayers,0);assert.equal(done.unresolved.length,0);assert.equal(done.timers,12);
 const expectedLinks=data.reduce((sum,s)=>sum+s.actions.filter(a=>a.to!==s.id).length,0);assert.equal(done.links,expectedLinks);
 const page=figma.currentPage,frames=page.children.filter(n=>/^\d+ · /.test(n.name));assert.equal(page.id,abandoned.id,'Recover the failed blank page instead of creating another');assert.equal(frames.length,91);
 for(const frame of frames){assert.equal(frame.width,1363);assert.equal(frame.height,936);assert.equal(frame.overflowDirection,'VERTICAL');}
 const actualText=page.findAll(n=>n.type==='TEXT');assert(actualText.length>3000);
 assert(actualText.every(t=>['Segoe UI','Georgia','Courier New'].includes(t.fontName.family)));
 const library=page.children.find(n=>n.name==='Components / Garden A');
 for(let i=0;i<library.children.length;i++)for(let j=i+1;j<library.children.length;j++){
  const a=library.children[i],b=library.children[j];
  assert(!(a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y),'Library components overlap');
 }
 const dropdown=library.children.find(n=>n.type==='COMPONENT_SET');assert(dropdown);assert.equal(dropdown.children.length,4);
 assert.equal(dropdown.children.filter(n=>n.reactions.length).length,4);
 assert(library.children.filter(n=>n.type==='COMPONENT_SET'&&n.name.startsWith('Setting / ')).length>=15,'Settings must expose real native prototype choices');
 assert.equal(page.findAll(n=>n.type==='RECTANGLE'&&n.reactions.length).length,done.links,'Every navigation needs a positioned prototype click target');
 assert(dropdown.children[3].children.some(n=>n.type==='TEXT'&&n.characters==='Claude Sonnet'));
 assert(dropdown.children.every(n=>n.height===dropdown.children[0].height),'Opening the menu must not move its auto-layout parent');
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'expected-content.json'),'utf8'));
 const norm=t=>t.replace(/\s+/g,'').toLowerCase();
 for(const frame of frames){const id=+frame.name.split(' · ')[0];if(id>81)continue;const text=norm(frame.findAll(n=>n.type==='TEXT').map(n=>n.characters).join(' '));assert(source[id].every(t=>text.includes(norm(t))),'Native output lost text on screen '+id);}
 const settingsFrame=frames.find(n=>n.name.startsWith('49 · '));for(const row of settingsFrame.findAll(n=>n.type==='FRAME'&&n.name==='setting-row'))row.children[row.children.length-1].type='FRAME';
 await figma.ui.onmessage({type:'patch'});assert(patched,'Patch operation must complete');assert.equal(patched.links,expectedLinks);assert.equal(patched.settings,17);assert.equal(page.findAll(n=>n.type==='RECTANGLE'&&n.reactions.length).length,expectedLinks,'Patch must replace, not duplicate, click targets');
 frames[0].fills=[{type:'SOLID',color:{r:247/255,g:248/255,b:246/255}}];const flowLabel=frames[0].findAll(n=>n.type==='TEXT'&&n.parent.name==='step-title')[0];assert(flowLabel);flowLabel.fontName={family:'Segoe UI',style:'Regular'};
 const beforeNodes=page.findAll(()=>true),idsBefore=beforeNodes.map(n=>n.id),textBefore=beforeNodes.filter(n=>n.type==='TEXT').map(n=>[n.id,n.characters,n.fontSize,n.fontName.family]);
 const geometryBefore=beforeNodes.filter(n=>n.type!=='TEXT').map(n=>[n.id,n.x,n.y,n.width,n.height]);
 const timingIds=new Set(Object.keys({9:6,10:8,16:13,17:15,23:15,54:51,55:53,63:60,64:62,69:70,74:75,81:70}).map(Number));
 for(const frame of frames)if(timingIds.has(+frame.name.split(' · ')[0]))frame.reactions=[];
 const paused=frames.find(n=>n.name.startsWith('09 · '));await paused.setReactionsAsync([{trigger:{type:'ON_CLICK'},actions:[{type:'NODE',destinationId:frames.find(n=>n.name.startsWith('07 · ')).id,navigation:'NAVIGATE'}]}]);
 const otherRootReactions=frames.map(n=>[n.id,JSON.stringify(n.reactions.filter(r=>r.trigger.type!=='AFTER_TIMEOUT'))]);
 const reactionsBefore=beforeNodes.filter(n=>!frames.some(f=>f===n&&timingIds.has(+f.name.split(' · ')[0]))).map(n=>[n.id,JSON.stringify(n.reactions)]);
 await figma.ui.onmessage({type:'applyA'});assert(appearance,JSON.stringify(done));assert.equal(appearance.timers,12);assert.equal(appearance.mismatches.length,0,JSON.stringify(appearance.mismatches.slice(0,10)));assert.equal(appearance.fontWarnings.length,0);
 assert.equal(flowLabel.fontName.style,'Bold','The approved process label must become bold');for(const [id,expected]of otherRootReactions)assert.equal(JSON.stringify(registry.get(id).reactions.filter(r=>r.trigger.type!=='AFTER_TIMEOUT')),expected);
 assert.deepEqual(page.findAll(()=>true).map(n=>n.id),idsBefore,'Appearance patch must not create or remove layers');
 assert.deepEqual(beforeNodes.filter(n=>n.type==='TEXT').map(n=>[n.id,n.characters,n.fontSize,n.fontName.family]),textBefore,'Preserve content, font size, and font family');
 assert.deepEqual(beforeNodes.filter(n=>n.type!=='TEXT').map(n=>[n.id,n.x,n.y,n.width,n.height]),geometryBefore,'Preserve all frame geometry');
 for(const [id,reactions]of reactionsBefore)assert.equal(JSON.stringify(registry.get(id).reactions),reactions,'Preserve unrelated interactions');
 const nine=frames.find(n=>n.name.startsWith('09 · ')),six=frames.find(n=>n.name.startsWith('06 · '));assert(nine.reactions.some(r=>r.trigger.type==='AFTER_TIMEOUT'&&r.trigger.timeout===1.9&&r.actions[0].destinationId===six.id));
 assert.equal(JSON.stringify(frames[0].fills[0].color),JSON.stringify({r:220/255,g:226/255,b:213/255}));
 const contentBeforeButtons=page.findAll(n=>n.type==='TEXT').map(n=>[n.id,norm(n.characters),n.fontSize,n.fontName.family]);
 const reactionsBeforeButtons=page.findAll(()=>true).map(n=>[n.id,JSON.stringify(n.reactions)]),idsBeforeButtons=page.findAll(()=>true).map(n=>n.id);
 await figma.ui.onmessage({type:'centerButtons'});assert(centered,JSON.stringify(done));assert(centered.buttons>150);assert.equal(centered.skipped.length,0);
 assert.deepEqual(page.findAll(()=>true).map(n=>n.id),idsBeforeButtons);assert.deepEqual(page.findAll(n=>n.type==='TEXT').map(n=>[n.id,norm(n.characters),n.fontSize,n.fontName.family]),contentBeforeButtons);
 for(const [id,reactions]of reactionsBeforeButtons)assert.equal(JSON.stringify(registry.get(id).reactions),reactions);
 for(const frame of frames)for(const button of frame.findAll(n=>['FRAME','INSTANCE'].includes(n.type)&&/^(?:UI \/ )?btn(?:\s|$)/.test(n.name))){assert.equal(button.primaryAxisAlignItems,'CENTER');assert.equal(button.counterAxisAlignItems,'CENTER');const label=button.children.find(n=>n.type==='TEXT');assert.equal(label.textAutoResize,'WIDTH_AND_HEIGHT');assert.equal(label.textAlignHorizontal,'CENTER');assert.equal(label.horizontal,'HUG');}
 const split=vm.runInContext("balanceOptionLines(['Подтвердить','замену','выбранной','версии'],s=>s.length,20)",context);assert.equal(split.length,2);assert.equal(split.join(' '),'Подтвердить замену выбранной версии');assert.equal(vm.runInContext("balanceOptionLines(['Открыть'],s=>s.length,3).length",context),1,'Never split a single word even when it exceeds the preferred width');
 const seven=frames.find(n=>n.name.startsWith('07 · ')),fourteen=frames.find(n=>n.name.startsWith('14 · '));
 const summaryLabels=[seven,fourteen].flatMap(f=>f.findAll(n=>n.type==='TEXT'&&n.parent.name==='li'&&n.parent.parent.name==='check-list'));
 assert.equal(summaryLabels.length,6);for(const n of summaryLabels){n.width=60;n.height=36;n.textAutoResize='HEIGHT';}
 const outputNodes=page.findAll(()=>true),outputIds=outputNodes.map(n=>n.id),outputReactions=outputNodes.map(n=>[n.id,JSON.stringify(n.reactions)]),outputContent=outputNodes.filter(n=>n.type==='TEXT').map(n=>[n.id,n.characters,n.fontSize,n.fontName.family,n.fontName.style]);
 const buttonsBefore=outputNodes.filter(n=>/^(?:UI \/ )?btn(?:\s|$)/.test(n.name)).map(n=>[n.id,n.x,n.y,n.width,n.height,JSON.stringify(n.fills)]);
 await figma.ui.onmessage({type:'repairOutput'});assert(outputRepaired,JSON.stringify(done));assert.equal(outputRepaired.frameCount,91);assert(outputRepaired.expandedText>=6);assert(outputRepaired.emptyOutputs>=7);assert.equal(outputRepaired.skipped.length,0);
 for(const n of summaryLabels){assert.equal(n.textAutoResize,'WIDTH_AND_HEIGHT');assert.equal(n.horizontal,'HUG');}
 assert.deepEqual(page.findAll(()=>true).map(n=>n.id),outputIds);assert.deepEqual(outputNodes.filter(n=>n.type==='TEXT').map(n=>[n.id,n.characters,n.fontSize,n.fontName.family,n.fontName.style]),outputContent);
 for(const [id,reactions]of outputReactions)assert.equal(JSON.stringify(registry.get(id).reactions),reactions);
 assert.deepEqual(outputNodes.filter(n=>/^(?:UI \/ )?btn(?:\s|$)/.test(n.name)).map(n=>[n.id,n.x,n.y,n.width,n.height,JSON.stringify(n.fills)]),buttonsBefore);
 const amber={r:128/255,g:96/255,b:21/255};for(const entry of outputRepaired.amber)assert.deepEqual(JSON.parse(JSON.stringify(registry.get(entry.id).fills[0].color)),amber);
 for(const n of outputNodes.filter(n=>n.type==='TEXT'&&/^Файл не создан\./.test(n.characters)))assert.notDeepEqual(JSON.parse(JSON.stringify(n.fills[0].color)),amber,'Actual errors must keep their existing color');
 const summary={status:'PASS',scope:'API simulation; real Figma rendering is not verified',screens:done.screens,clickConnections:done.links,timers:done.timers,imageLayers:0,unresolved:0,types:done.types,textStyles:textStyles.size,fontFamilies:[...new Set(actualText.map(t=>t.fontName.family))],modelSelectorVariants:4,libraryComponentsDoNotOverlap:true,approvedA:appearance,appearancePreservesStructure:true,stalledAnalysisTimerRepaired:true,buttonLayout:centered,outputText:{...outputRepaired,details:undefined,amber:undefined},outputContentAndInteractionsPreserved:true};
 fs.writeFileSync(path.join(__dirname,'native-validation.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify(summary));
}
main().catch(error=>{console.error(error);process.exitCode=1});
