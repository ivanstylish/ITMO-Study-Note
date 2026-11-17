function isEmptyOutput(text){return /^(?:Нет (?:копий|знаний)|Файл не будет создан|Ничего не найдено|Нет результатов)/i.test(text.trim());}
async function repairOutputText(p){
 const frames=currentFrames(p);if(frames.size!==91)throw Error('当前页应包含 91 个 A Final 画面，请先选择完整原型页面。');
 const scratch=figma.createFrame();p.appendChild(scratch);scratch.name='Temporary output text measurement';scratch.resize(1,1);scratch.x=50000;scratch.y=50000;scratch.visible=false;scratch.fills=[];
 const probe=figma.createText();scratch.appendChild(probe);probe.name='Output text measurement';
 const cache=new Map(),loaded=new Set(),expanded=[],amber=[],skipped=[];
 const excluded=n=>/^(?:UI \/ )?(?:btn(?:\s|$)|generic-button|graph-node|brand|model-choice|setting-row|editable-conversation)/.test(n.name);
 async function measure(n){
  const segments=n.getStyledTextSegments(['fontName']);if(segments.length!==1||typeof n.fontSize!=='number')return null;
  const font=segments[0].fontName,key=JSON.stringify(font);if(!loaded.has(key)){await figma.loadFontAsync(font);loaded.add(key);}
  probe.fontName=font;probe.fontSize=n.fontSize;probe.letterSpacing=n.letterSpacing||{unit:'PIXELS',value:0};probe.lineHeight=n.lineHeight||{unit:'AUTO'};probe.textAutoResize='WIDTH_AND_HEIGHT';
  const token=JSON.stringify([font,n.fontSize,n.letterSpacing,n.characters]);if(!cache.has(token)){probe.characters=n.characters;cache.set(token,probe.width);}return cache.get(token);
 }
 function widthAvailable(n){
  const parent=n.parent;if(!parent||!('width'in parent))return n.width;
  const siblings=parent.children.filter(c=>c!==n&&c.visible!==false&&c.layoutPositioning!=='ABSOLUTE');
  if(parent.layoutMode==='HORIZONTAL')return parent.width-(parent.paddingLeft||0)-(parent.paddingRight||0)-siblings.reduce((s,c)=>s+c.width,0)-(parent.itemSpacing||0)*siblings.length;
  let right=parent.width-(parent.paddingRight||0);
  for(const c of siblings)if(c.x>n.x&&c.y<n.y+n.height&&c.y+c.height>n.y)right=Math.min(right,c.x-2);
  return right-Math.max(n.x,parent.paddingLeft||0);
 }
 try{
  for(const [scene,frame]of frames){
   for(const n of frame.findAll(n=>n.type==='TEXT')){
    if(isEmptyOutput(n.characters)){n.fills=approvedPaint(color('#806015'));amber.push({scene,id:n.id,text:n.characters});}
    let ancestor=n.parent,skip=false;while(ancestor&&ancestor!==frame){if(excluded(ancestor)){skip=true;break;}ancestor=ancestor.parent;}
    if(skip||n.characters.includes('\n')||n.parent.children.length!==1)continue;
    const natural=await measure(n);if(natural===null){skipped.push(n.id);continue;}
    const parent=n.parent;
    // Empty-result rows sometimes reserve half the row for a short field label.
    if(isEmptyOutput(n.characters)&&/^source-cell/.test(parent.name)&&/^source-row/.test(parent.parent?.name)){
     const row=parent.parent,cells=row.children;
     if(cells.length===2&&cells[1]===parent&&cells[0].children.length===1&&cells[0].children[0].type==='TEXT'){
      const first=await measure(cells[0].children[0]);
      if(first!==null&&first+natural+4+(row.itemSpacing||0)<=row.width-(row.paddingLeft||0)-(row.paddingRight||0)){
       cells[0].resize(Math.ceil(first+2),cells[0].height);parent.resize(Math.floor(widthAvailable(parent)),parent.height);
      }
     }
    }
    let available=widthAvailable(n);
    // Grow compact, transparent label wrappers only into proven free parent space.
    if(natural+1>available&&/^(?:span|button|step-title|step-state|subtitle|p|badge(?:\s|$))/.test(parent.name)){
     const room=widthAvailable(parent),extra=(parent.paddingLeft||0)+(parent.paddingRight||0);
     if(natural+extra+1<=room){parent.resize(Math.ceil(natural+extra+1),parent.height);available=widthAvailable(n);}
    }
    if(natural+1<=available&&(n.width<natural+1||n.height>(n.lineHeight?.value||n.fontSize*1.5)*1.6)){
     n.textAutoResize='WIDTH_AND_HEIGHT';
     if(parent.layoutMode==='HORIZONTAL'||parent.layoutMode==='VERTICAL'){n.layoutSizingHorizontal='HUG';n.layoutSizingVertical='HUG';}
     expanded.push({scene,id:n.id,text:n.characters,available});
    }
   }
  }
  return {frameCount:frames.size,expandedText:expanded.length,emptyOutputs:amber.length,skipped,details:expanded,amber};
 }finally{scratch.remove();}
}
