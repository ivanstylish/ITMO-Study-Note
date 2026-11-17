function optionWords(text){return text.trim().split(/\s+/).filter(Boolean);}
function balanceOptionLines(words,measure,limit){
 const whole=words.join(' ');if(words.length<2||measure(whole)<=limit)return [whole];
 let best=null;
 for(let i=1;i<words.length;i++){const lines=[words.slice(0,i).join(' '),words.slice(i).join(' ')],widths=lines.map(measure),score=Math.max(...widths);if(!best||score<best.score)best={lines,score};}
 return best.lines;
}
async function centerOptionButtons(p){
 const frames=currentFrames(p);if(!frames.has(1))throw Error('请选择已生成的 A Final 页面。');
 const scratch=figma.createFrame();p.appendChild(scratch);scratch.name='Temporary button text measurement';scratch.resize(1,1);scratch.x=50000;scratch.y=50000;scratch.visible=false;scratch.fills=[];
 const probe=figma.createText();scratch.appendChild(probe);probe.name='Button text measurement';
 const measured=new Map(),mainDone=new Set(),skipped=[],buttons=[];
 const isButton=n=>['FRAME','COMPONENT','INSTANCE'].includes(n.type)&&/^(?:UI \/ )?(?:btn(?:\s|$)|generic-button(?:\s|$))/.test(n.name);
 async function fix(n){
  const labels=n.children.filter(c=>c.type==='TEXT');if(labels.length!==1){skipped.push(n.id);return;}
  const label=labels[0],segments=label.getStyledTextSegments(['fontName']);
  if(!segments.length||new Set(segments.map(s=>JSON.stringify(s.fontName))).size!==1||typeof label.fontSize!=='number'){skipped.push(n.id);return;}
  const font=segments[0].fontName;await figma.loadFontAsync(font);probe.fontName=font;probe.fontSize=label.fontSize;probe.letterSpacing=label.letterSpacing||{unit:'PIXELS',value:0};probe.lineHeight=label.lineHeight||{unit:'AUTO'};probe.textAutoResize='WIDTH_AND_HEIGHT';
  const measure=text=>{const key=JSON.stringify([font,label.fontSize,label.letterSpacing,text]);if(!measured.has(key)){probe.characters=text;measured.set(key,probe.width);}return measured.get(key);};
  const padX=Math.max(14,n.paddingLeft||0,n.paddingRight||0),padY=Math.max(10,n.paddingTop||0,n.paddingBottom||0),gap=n.itemSpacing||0;
  const icons=n.children.filter(c=>c!==label),iconWidth=icons.reduce((sum,c)=>sum+c.width,0),gaps=Math.max(0,n.children.length-1)*gap;
  const limit=Math.max(120,Math.min(360,(n.parent?.width||1000)-24)-2*padX-iconWidth-gaps);
  const words=optionWords(label.characters),lines=balanceOptionLines(words,measure,limit);
  const textWidth=Math.max(...lines.map(measure)),lineHeight=label.lineHeight?.unit==='PIXELS'?label.lineHeight.value:label.fontSize*1.5;
  if(n.layoutMode!=='HORIZONTAL')n.layoutMode='HORIZONTAL';
  n.primaryAxisSizingMode=n.counterAxisSizingMode='FIXED';n.primaryAxisAlignItems=n.counterAxisAlignItems='CENTER';n.paddingLeft=n.paddingRight=padX;n.paddingTop=n.paddingBottom=padY;
  if(label.characters!==lines.join('\n'))label.characters=lines.join('\n');
  label.textAutoResize='WIDTH_AND_HEIGHT';label.layoutSizingHorizontal='HUG';label.layoutSizingVertical='HUG';label.textAlignHorizontal='CENTER';label.textAlignVertical='CENTER';
  n.resize(Math.ceil(Math.max(n.width,textWidth+iconWidth+gaps+2*padX)),Math.ceil(Math.max(n.height,44,lineHeight*lines.length+2*padY)));
 }
 try{
  for(const frame of frames.values())for(const button of frame.findAll(isButton)){
   if(button.type==='INSTANCE'&&button.getMainComponentAsync){const main=await button.getMainComponentAsync();if(main&&!mainDone.has(main.id)){await fix(main);mainDone.add(main.id);}}
   await fix(button);buttons.push({frame,button,label:optionWords(button.findAll(n=>n.type==='TEXT').map(t=>t.characters).join(' ')).join(' ')});
  }
  let targets=0;const used=new Set();
  for(const {frame,button,label}of buttons){
   const layer=frame.children.find(n=>n.name==='Prototype click targets / locked for editing');if(!layer)continue;
   const x=button.absoluteTransform[0][2]-frame.absoluteTransform[0][2]-layer.x,y=button.absoluteTransform[1][2]-frame.absoluteTransform[1][2]-layer.y;
   const candidates=layer.children.filter(n=>!used.has(n.id)&&optionWords(n.name).join(' ')===label);
   candidates.sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y));const hot=candidates[0];if(!hot)continue;
   hot.x=x;hot.y=y;hot.resize(button.width,button.height);used.add(hot.id);targets++;
  }
  return {buttons:buttons.length,clickTargets:targets,skipped};
 }finally{scratch.remove();}
}
