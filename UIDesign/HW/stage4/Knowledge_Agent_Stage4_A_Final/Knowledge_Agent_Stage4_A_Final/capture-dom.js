(() => {
const round=n=>Math.round(n*100)/100;
let uid=0;
function color(value){
 if(!value||value==='transparent'||value==='none')return {r:0,g:0,b:0,a:0};
 const m=value.match(/[\d.]+/g);if(!m)return {r:0,g:0,b:0,a:0};
 return {r:+m[0]/255,g:+m[1]/255,b:+m[2]/255,a:m[3]===undefined?1:+m[3]};
}
const rect=(box,parent)=>({x:round(box.x-parent.x),y:round(box.y-parent.y),w:round(box.width),h:round(box.height)});
function nodeText(value,box,parent,style,name='Text',scale=1){
 return {kind:'text',name,text:value,...rect(box,parent),font:style.fontFamily,fontSize:parseFloat(style.fontSize)*scale,weight:parseInt(style.fontWeight)||400,color:color(style.color),lineHeight:(parseFloat(style.lineHeight)||parseFloat(style.fontSize)*1.2)*scale,letterSpacing:(parseFloat(style.letterSpacing)||0)*scale,align:style.textAlign};
}
function walk(el,parent){
 const style=getComputedStyle(el),box=el.getBoundingClientRect();
 if(style.display==='none'||style.visibility==='hidden'||box.width<=0||box.height<=0)return null;
 const name=el.className&&typeof el.className==='string'?el.className:el.getAttribute('aria-label')||el.tagName.toLowerCase();
 const domId=++uid;el.__captureId=domId;
 const world=el.closest('.graph-world'),matrix=world?new DOMMatrix(getComputedStyle(world).transform):null,scale=matrix?Math.hypot(matrix.a,matrix.b):1;
 if(el.tagName.toLowerCase()==='svg'){
  const clone=el.cloneNode(true),original=[el,...el.querySelectorAll('*')],copied=[clone,...clone.querySelectorAll('*')];
  for(let i=0;i<original.length;i++){const cs=getComputedStyle(original[i]);for(const p of ['fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','opacity'])copied[i].setAttribute(p,cs.getPropertyValue(p));}
  if(!clone.hasAttribute('viewBox'))clone.setAttribute('viewBox','0 0 '+el.clientWidth+' '+el.clientHeight);
  clone.setAttribute('width',round(box.width));clone.setAttribute('height',round(box.height));clone.setAttribute('xmlns','http://www.w3.org/2000/svg');
  return {kind:'svg',name,domId,...rect(box,parent),svg:clone.outerHTML};
 }
 const widths=['Top','Right','Bottom','Left'].map(side=>(parseFloat(style['border'+side+'Width'])||0)*scale);
 const d={kind:'frame',name,domId,...rect(box,parent),fill:color(style.backgroundColor),opacity:+style.opacity,radius:(parseFloat(style.borderRadius)||0)*scale,
  border:{top:widths[0],right:widths[1],bottom:widths[2],left:widths[3],color:color(style.borderTopColor)},
  clips:style.overflow==='hidden'||style.overflow==='clip',children:[],position:style.position,
  reusable:el.tagName==='BUTTON'||el.classList.contains('badge')||el.classList.contains('step-num'),
  layout:{display:style.display,direction:style.flexDirection,gap:(parseFloat(style.gap)||0)*scale,padding:[style.paddingTop,style.paddingRight,style.paddingBottom,style.paddingLeft].map(x=>(parseFloat(x)||0)*scale),justify:style.justifyContent,align:style.alignItems}};
 if(el.classList.contains('graph-canvas'))d.dots=true;
 if(el.tagName==='INPUT'&&el.type==='checkbox'){d.checkbox=true;d.checked=el.checked;return d;}
 if(['INPUT','TEXTAREA','SELECT'].includes(el.tagName)){
  const text=el.tagName==='SELECT'?el.options[el.selectedIndex].text:el.value||el.placeholder;
  const left=parseFloat(style.paddingLeft)||0,top=parseFloat(style.paddingTop)||0;
  d.children=[nodeText(text,{x:box.x+left,y:box.y+top,width:box.width-left-(parseFloat(style.paddingRight)||0),height:Math.max(parseFloat(style.lineHeight)||20,box.height-top-(parseFloat(style.paddingBottom)||0))},box,style,'Field value')];
  if(el.hasAttribute('data-model-selector'))d.modelSelector=true;
  return d;
 }
 for(const child of el.childNodes){
  if(child.nodeType===Node.ELEMENT_NODE){if(['SCRIPT','STYLE','BR'].includes(child.tagName))continue;const c=walk(child,box);if(c)d.children.push(c);}
  else if(child.nodeType===Node.TEXT_NODE&&child.textContent.trim()){
   const range=document.createRange();range.selectNodeContents(child);const b=range.getBoundingClientRect();
   if(b.width&&b.height)d.children.push(nodeText(child.textContent.replace(/^\s+|\s+$/g,''),b,box,style,child.textContent.trim().slice(0,70),scale));
  }
 }
 return d;
}
window.captureCurrent=()=>{
 const app=document.querySelector('#app'),box=app.getBoundingClientRect();
 const h=Math.max(936,Math.ceil(box.height));
 const tree={kind:'frame',name:'Application',x:0,y:0,w:1363,h,fill:color(getComputedStyle(document.body).backgroundColor),radius:0,opacity:1,border:{},clips:false,children:[]};
 for(const el of app.children){const d=walk(el,{x:0,y:0});if(d)tree.children.push(d);}
 const actions=[];
 for(const el of app.querySelectorAll('[data-go],[data-proto-to]')){
  if(el.disabled)continue;
  const to=Number(el.dataset.protoTo||el.dataset.go),b=el.getBoundingClientRect();
  if(to&&b.width>0&&b.height>0)actions.push({label:el.getAttribute('aria-label')||el.textContent.trim(),domId:el.__captureId,to,x:round(b.x),y:round(b.y),w:round(b.width),h:round(b.height)});
 }
 const graphTools=[];
 for(const el of app.querySelectorAll('.graph-tools button')){const b=el.getBoundingClientRect();graphTools.push({label:el.getAttribute('aria-label')||el.textContent.trim(),domId:el.__captureId,x:round(b.x),y:round(b.y),w:round(b.width),h:round(b.height)});}
 const textNodes=[];function collect(d){if(d.kind==='text')textNodes.push(d.text);for(const c of d.children||[])collect(c)}collect(tree);
 const overflows=[...app.querySelectorAll('button,.source-cell,.file-option,.setting-row,.model-choice')].filter(e=>e.scrollWidth>e.clientWidth+3&&!e.closest('.graph-world')).map(e=>({name:e.className,text:e.textContent.trim().slice(0,90),excess:e.scrollWidth-e.clientWidth}));
 const clippedText=[];
 for(const el of app.querySelectorAll('.source-cell,.file-option,.setting-row'))if(el.scrollHeight>el.clientHeight+3)clippedText.push(el.textContent.trim().slice(0,70));
 return {width:1363,height:h,tree,actions,graphTools,textNodes,overflows,clippedText,bodyFont:getComputedStyle(document.body).fontFamily};
};
})();
