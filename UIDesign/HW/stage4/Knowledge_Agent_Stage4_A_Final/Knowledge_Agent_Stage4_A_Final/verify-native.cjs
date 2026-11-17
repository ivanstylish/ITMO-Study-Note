const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const registry=new Map(),textStyles=new Map();let sequence=0,readyResolve,done;
class Node {
 constructor(type){this.id=String(++sequence);this.type=type;this.name=type;this.children=[];this.x=this.y=0;this.width=this.height=100;this.fills=[];this.strokes=[];this.reactions=[];this.layoutMode='NONE';this.opacity=1;this.fontSize=14;this.lineHeight={unit:'PIXELS',value:21};registry.set(this.id,this);}
 appendChild(n){if(n.parent)n.parent.children=n.parent.children.filter(c=>c!==n);this.children.push(n);n.parent=this;}
 resize(w,h){assert(Number.isFinite(w)&&Number.isFinite(h)&&w>0&&h>0,[this.name,w,h].join(' / '));this.width=w;this.height=h;}
 set layoutSizingHorizontal(value){assert(['FIXED','FILL','HUG'].includes(value));if(value==='FILL')assert(this.parent&&this.parent.layoutMode!=='NONE');this.horizontal=value;}
 set layoutSizingVertical(value){assert(['FIXED','FILL','HUG'].includes(value));this.vertical=value;}
 set textStyleId(id){const style=textStyles.get(id);assert(style);this.fontName=style.fontName;this.fontSize=style.fontSize;this.lineHeight=style.lineHeight;}
 set characters(value){assert(this.type==='TEXT');assert(loaded.has(JSON.stringify(this.fontName)),'Font must load before editing');this.text=value;}
 get characters(){return this.text||'';}
 findAll(predicate){const result=[];for(const c of this.children){if(predicate(c))result.push(c);result.push(...c.findAll(predicate))}return result;}
 async setReactionsAsync(reactions){for(const r of reactions){assert(['ON_CLICK','AFTER_TIMEOUT'].includes(r.trigger.type));for(const a of r.actions){assert(registry.has(a.destinationId));assert(['NAVIGATE','CHANGE_TO'].includes(a.navigation));}}this.reactions=reactions;}
 clone(asInstance=false){const copy=new Node(asInstance?'INSTANCE':this.type);for(const [k,v]of Object.entries(this)){if(['id','type','children','parent'].includes(k))continue;copy[k]=typeof v==='object'&&v!==null?structuredClone(v):v;}for(const child of this.children)copy.appendChild(child.clone());return copy;}
 createInstance(){assert(this.type==='COMPONENT');const copy=this.clone(true);copy.mainComponent=this;return copy;}
}
const loaded=new Set();
const fontNames=['Segoe UI','Georgia','Courier New'].flatMap(family=>['Regular','Semibold','Bold','Black'].map(style=>({fontName:{family,style}})));
const figma={
 showUI(){},ui:{postMessage(m){if(m.type==='ready')readyResolve(m);if(m.type==='done'||m.type==='error')done=m;}},
 root:new Node('DOCUMENT'),currentPage:null,
 listAvailableFontsAsync:async()=>fontNames,
 loadFontAsync:async font=>{assert(fontNames.some(f=>JSON.stringify(f.fontName)===JSON.stringify(font)));loaded.add(JSON.stringify(font));},
 createPage(){const n=new Node('PAGE');this.root.appendChild(n);return n;},
 setCurrentPageAsync:async page=>{figma.currentPage=page;},
 createFrame:()=>new Node('FRAME'),createComponent:()=>new Node('COMPONENT'),createText:()=>new Node('TEXT'),
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
 const data=JSON.parse(fs.readFileSync(path.join(__dirname,'scenes.json'),'utf8'));context.SCENES=data;
 vm.runInContext(fs.readFileSync(path.join(__dirname,'importer.js'),'utf8'),context);
 const fonts=await ready;assert.equal(fonts.missing.length,0);
 await figma.ui.onmessage({type:'import'});
 assert(done&&done.type==='done',JSON.stringify(done));
 assert.equal(done.screens,91);assert.equal(done.imageLayers,0);assert.equal(done.unresolved.length,0);assert.equal(done.timers,12);
 assert.equal(done.links,data.reduce((sum,s)=>sum+s.actions.length,0));
 const page=figma.currentPage,frames=page.children.filter(n=>/^\d+ · /.test(n.name));assert.equal(frames.length,91);
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
 assert(dropdown.children[3].children.some(n=>n.type==='TEXT'&&n.characters==='Claude Sonnet'));
 assert(dropdown.children.every(n=>n.height===dropdown.children[0].height),'Opening the menu must not move its auto-layout parent');
 const source=JSON.parse(fs.readFileSync(path.join(__dirname,'expected-content.json'),'utf8'));
 const norm=t=>t.replace(/\s+/g,'').toLowerCase();
 for(const frame of frames){const id=+frame.name.split(' · ')[0];if(id>81)continue;const text=norm(frame.findAll(n=>n.type==='TEXT').map(n=>n.characters).join(' '));assert(source[id].every(t=>text.includes(norm(t))),'Native output lost text on screen '+id);}
 const summary={status:'PASS',scope:'API simulation; real Figma rendering is not verified',screens:done.screens,clickConnections:done.links,timers:done.timers,imageLayers:0,unresolved:0,types:done.types,textStyles:textStyles.size,fontFamilies:[...new Set(actualText.map(t=>t.fontName.family))],modelSelectorVariants:4,libraryComponentsDoNotOverlap:true};
 fs.writeFileSync(path.join(__dirname,'native-validation.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify(summary));
}
main().catch(error=>{console.error(error);process.exitCode=1});
