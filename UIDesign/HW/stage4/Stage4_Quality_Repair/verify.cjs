const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
let nextId=0;
function node(type,name,width=100,height=40){
  return {id:String(++nextId),type,name,width,height,x:0,y:0,visible:true,opacity:1,fills:[],strokes:[],effects:[],reactions:[],children:[],selection:[],
    appendChild(c){if(c.parent)c.parent.children=c.parent.children.filter(n=>n!==c);this.children.push(c);c.parent=this},
    resize(w,h){this.width=w;this.height=h},
    findAll(predicate){const result=[];for(const c of this.children){if(predicate(c))result.push(c);result.push(...c.findAll(predicate))}return result},
    remove(){this.parent.children=this.parent.children.filter(n=>n!==this)},
    clone(){const copy=node(this.type,this.name,this.width,this.height);for(const [k,v] of Object.entries(this))if(!['id','parent','children','selection'].includes(k)&&typeof v!=='function')copy[k]=JSON.parse(JSON.stringify(v));for(const c of this.children)copy.appendChild(c.clone());return copy},
    async setReactionsAsync(value){this.reactions=value},
    getStyledTextSegments(){return [{fontName:{family:'Manrope',style:'Regular'}}]}
  };
}
const figma={showUI(){},ui:{},createFrame:()=>node('FRAME','Frame'),createText:()=>node('TEXT','Text'),createPage:()=>node('PAGE','Page'),setCurrentPageAsync:async p=>{figma.currentPage=p},viewport:{scrollAndZoomIntoView(){}},loadFontAsync:async()=>{}};
const context=vm.createContext({figma,__html__:'',console});
vm.runInContext(fs.readFileSync(path.join(__dirname,'code.js'),'utf8'),context);
const fill=[{type:'SOLID',color:{r:.2,g:.3,b:.2}}];
function addBorders(n,sides=['top','right','bottom','left']){
  for(const side of sides){const horizontal=side==='top'||side==='bottom';const s=node('RECTANGLE','Border / '+side,horizontal?n.width:1,horizontal?1:n.height);s.fills=fill;s.x=side==='right'?n.width-1:0;s.y=side==='bottom'?n.height-1:0;n.appendChild(s)}
}
const button=node('COMPONENT','UI / btn primary');button.cornerRadius=11;addBorders(button);
const action={trigger:{type:'ON_CLICK'},actions:[{destinationId:'target'}]};button.reactions=[action];
assert(context.repairBorder(button));assert.equal(button.children.length,0);assert.equal(button.strokeWeight,1);assert.equal(button.cornerRadius,11);assert.equal(button.reactions[0],action);
assert.equal(context.repairBorder(button),false,'second execution must be a no-op');
const divider=node('FRAME','file-option');addBorders(divider,['bottom']);assert.equal(context.repairBorder(divider),false);assert.equal(divider.children.length,1);
const uneven=node('FRAME','custom');addBorders(uneven);uneven.children[0].height=2;assert.equal(context.repairBorder(uneven),false);
const wired=node('FRAME','wired border');addBorders(wired);wired.children[0].reactions=[action];assert.equal(context.repairBorder(wired),false);

const source=process.argv[2];
if(source){
  const scenes=JSON.parse(fs.readFileSync(source,'utf8'));
  const page=node('PAGE','81 states');
  function build(d){
    const n=node(d.kind==='text'?'TEXT':'FRAME',d.name,d.w,d.h);n.x=d.x;n.y=d.y;
    if(d.kind==='text')n.characters=d.text;
    for(const child of d.children||[])n.appendChild(build(child));
    const b=d.border||{};
    for(const side of ['top','right','bottom','left'])if(b[side]){
      const horizontal=side==='top'||side==='bottom';const s=node('RECTANGLE','Border / '+side,horizontal?d.w:b[side],horizontal?b[side]:d.h);
      s.x=side==='right'?d.w-b[side]:0;s.y=side==='bottom'?d.h-b[side]:0;s.fills=[{type:'SOLID',color:{r:b.color.r,g:b.color.g,b:b.color.b},opacity:b.color.a}];n.appendChild(s);
    }
    return n;
  }
  for(const scene of scenes)page.appendChild(build(scene.tree));
  const namesBefore=page.findAll(n=>n.type==='TEXT').map(n=>n.characters);
  const auditBefore=context.audit(page);
  context.repair(page).then(result=>{
    assert.equal(result.rows,6);assert(result.borders>=169);assert.equal(page.children.length,81);
    assert.deepEqual(page.findAll(n=>n.type==='TEXT').map(n=>n.characters),namesBefore,'all original text must survive');
    const rows=page.findAll(n=>n.name==='file-option');
    for(const row of rows){const size=row.children.find(n=>n.name==='muted small');assert.equal(size.width,80);assert.equal(size.children[0].textAlignHorizontal,'RIGHT');assert.equal(row.itemSpacing,24);assert.equal(row.children.find(n=>n.name==='Border / bottom').layoutPositioning,'ABSOLUTE');}
    return context.repair(page).then(async second=>{
      assert.equal(second.borders,0);assert.equal(second.rows,6);
      page.selection=[page.children[0]];
      const sourceText=page.children[0].findAll(n=>n.type==='TEXT').map(n=>n.characters);
      const variants=await context.makeComparisons(page);
      assert.equal(variants.screens.length,3);assert.equal(page.children.length,81);
      const comparison=figma.currentPage;
      assert.equal(comparison.children.length,3);
      const switches=comparison.findAll(n=>n.reactions.length);
      assert.equal(switches.length,9);assert(switches.every(n=>variants.screens.some(s=>s.id===n.reactions[0].actions[0].destinationId)));
      for(const frame of comparison.children)assert.deepEqual(frame.children[0].findAll(n=>n.type==='TEXT').map(n=>n.characters),sourceText);
      console.log(JSON.stringify({status:'PASS',screenCount:81,preservedTextNodes:namesBefore.length,sourceButtons:auditBefore.editableButtons,bordersRepaired:result.borders,fileRowsRepaired:result.rows,comparisonScreens:3,themeSwitches:9,idempotent:true,scope:'API mock with local scenes; live Figma rendering not verified'}));
    });
  }).catch(error=>{console.error(error);process.exitCode=1});
}else console.log('PASS: border geometry, corner radius, actions, dividers, retry safety');
