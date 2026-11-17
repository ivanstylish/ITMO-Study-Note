(async()=>{
 const api=window.__TIKZ_EDITOR_APP_TEST_API__;
 const original=document.querySelector('svg[aria-label="TikZ SVG preview"]');
 if(!original)throw Error('Diagram SVG missing');
 const svg=original.cloneNode(true);
 const [x,y,w,h]=svg.getAttribute('viewBox').split(' ').map(Number);
 svg.setAttribute('xmlns','http://www.w3.org/2000/svg');
 svg.setAttribute('width',String(w*4/3));svg.setAttribute('height',String(h*4/3));
 svg.removeAttribute('style');svg.style.background='white';
 const text=new XMLSerializer().serializeToString(svg);
 const url=URL.createObjectURL(new Blob([text],{type:'image/svg+xml'}));
 try{
 const img=new Image();img.src=url;await img.decode();
 const canvas=document.createElement('canvas');canvas.width=Math.ceil(w*4/3);canvas.height=Math.ceil(h*4/3);
 const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0);
 return {svg:text,png:canvas.toDataURL('image/png').split(',')[1],states:api.getSceneTextDebug().filter(t=>/^S\d+$/.test(t.text)).length,figures:api.getFigureCount(),width:canvas.width,height:canvas.height};
 }finally{URL.revokeObjectURL(url)}
})()
