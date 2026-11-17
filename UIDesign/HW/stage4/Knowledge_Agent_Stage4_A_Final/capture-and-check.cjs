const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),{pathToFileURL}=require('node:url');
const root=__dirname;
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 const proc=cp.spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-first-run','--disable-extensions','--no-sandbox','--remote-debugging-port=9237','--user-data-dir='+path.join(root,'qa-browser-profile'),'about:blank'],{windowsHide:true,stdio:'ignore'});
 let targets;
 for(let i=0;i<40;i++){try{targets=await(await fetch('http://127.0.0.1:9237/json/list')).json();break}catch{await delay(200)}}
 if(!targets)throw new Error('Browser did not start');
 const socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j});
 let sequence=0;const pending=new Map();socket.onmessage=e=>{const data=JSON.parse(e.data);if(data.id&&pending.has(data.id)){const [resolve,reject]=pending.get(data.id);pending.delete(data.id);data.error?reject(Error(data.error.message)):resolve(data.result)}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,[resolve,reject]);socket.send(JSON.stringify({id,method,params}))});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(r.exceptionDetails.text+' '+JSON.stringify(r.exceptionDetails.exception));return r.result.value};
 try{
  await send('Page.enable');await send('Emulation.setDeviceMetricsOverride',{width:1363,height:936,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:pathToFileURL(path.join(root,'web-source','index.html')).href+'?capture=1'});
  for(let i=0;i<80;i++){try{if(await evaluate('typeof captureCurrent+" "+typeof SCREENS')==='undefined object'&&await evaluate('typeof finalReady')==='boolean')break}catch{}await delay(100)}
  await evaluate('document.fonts.ready');await evaluate(fs.readFileSync(path.join(root,'capture-dom.js'),'utf8'));
  const meta=await evaluate('SCREENS.map(s=>({id:s.id,name:s.title}))');
  const scenes=[],audits=[];fs.mkdirSync(path.join(root,'previews'),{recursive:true});
  for(const m of meta){
   await evaluate('go('+m.id+')');await evaluate('document.fonts.ready');
   const scene=await evaluate('captureCurrent()');scenes.push({id:m.id,name:m.name,...scene});
   audits.push({id:m.id,font:scene.bodyFont,overflows:scene.overflows,clippedText:scene.clippedText});
   const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{x:0,y:0,width:1363,height:scene.height,scale:1}});
   fs.writeFileSync(path.join(root,'previews',String(m.id).padStart(2,'0')+'.png'),Buffer.from(shot.data,'base64'));
   if(m.id%10===0)process.stdout.write('Captured '+m.id+'/81\n');
  }
  const zoomIds={};let next=82;
  for(const id of [44,45,46,47,48])for(const delta of [-.2,.2]){
   await evaluate('go('+id+');graphZoom('+delta+')');const scene=await evaluate('captureCurrent()');
   const extra=next++;zoomIds[id+':'+(delta<0?'out':'in')]=extra;
   scenes.push({id:extra,name:meta[id-1].name+' · '+(delta<0?'80%':'120%'),source:id,...scene});
  }
  for(const scene of scenes){const id=scene.source||scene.id;if(id>=44&&id<=48){for(const tool of scene.graphTools){let to=id;if(tool.label==='Уменьшить')to=zoomIds[id+':out'];if(tool.label==='Увеличить')to=zoomIds[id+':in'];scene.actions.push({...tool,to})}}}
  // Exercise important transitions through the actual DOM events.
  const interactions=await evaluate(`(()=>{
   const checks=[];go(1);document.querySelector('.dropzone .btn').click();checks.push(['choose-file',current===2]);
   document.querySelector('.file-option .btn').click();checks.push(['open-file',current===5]);
   document.querySelector('.actions .primary').click();checks.push(['analyze',current===9]);
   go(7);document.querySelector('.check').click();checks.push(['empty-plan',current===11&&document.querySelector('.actions .primary').disabled]);
   go(14);document.querySelectorAll('.check')[1].click();checks.push(['single-note',current===68]);
   go(33);document.querySelector('.actions .btn').click();checks.push(['conflict-back',current===27]);
   go(4);document.querySelector('.actions .primary').click();checks.push(['clipboard-route',current===59]);
   go(42);document.querySelector('.actions .btn').click();checks.push(['restore-cancel',current===41]);
   go(6);const select=document.querySelector('[data-model-selector]');select.value='Claude Sonnet';select.dispatchEvent(new Event('change'));checks.push(['model-selector',selectedModel==='Claude Sonnet']);
   go(38);const search=document.querySelector('#history-search');search.value='RAG';search.dispatchEvent(new Event('input'));checks.push(['history-search',[...document.querySelectorAll('#history-rows tr')].filter(r=>!r.hidden).length===1]);
   return checks;
  })()`);
  fs.writeFileSync(path.join(root,'scenes.json'),JSON.stringify(scenes));
  const report={mainScreens:81,zoomScreens:10,allScenes:scenes.length,interactions,audits,fonts:['Segoe UI','Georgia','Courier New'],nativeFigmaVerified:false};
  fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify({scenes:scenes.length,failedInteractions:interactions.filter(x=>!x[1]),overflowScenes:audits.filter(a=>a.overflows.length||a.clippedText.length)}));
 }finally{await send('Browser.close').catch(()=>{});socket.close();proc.kill();}
}
main().catch(e=>{console.error(e);process.exitCode=1});
