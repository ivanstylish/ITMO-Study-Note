import fs from 'node:fs';
const targets=await(await fetch('http://127.0.0.1:19337/json')).json();
const target=targets.find(t=>t.type==='page'&&t.url.startsWith('https://tikz.dev/editor/web/'));
if(!target)throw Error('TikZ editor tab not found');
const ws=new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
let serial=0;
const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(pending.has(m.id)){const {resolve,reject}=pending.get(m.id);pending.delete(m.id);m.error?reject(Error(JSON.stringify(m.error))):resolve(m.result);}};
async function cdp(method,params={}){return await new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});}
async function evaluate(expression){const r=await cdp('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
try{
 if(process.argv[3]==='show'){
  const {windowId}=await cdp('Browser.getWindowForTarget');
  await cdp('Browser.setWindowBounds',{windowId,bounds:{windowState:'normal'}});
  await cdp('Browser.setWindowBounds',{windowId,bounds:{windowState:'maximized'}});
  await cdp('Page.bringToFront');
 }
 if(process.argv[3]==='screenshot'){
  const r=await cdp('Page.captureScreenshot',{format:'png'});fs.writeFileSync(process.argv[2],Buffer.from(r.data,'base64'));
 }else{
 const script=process.argv[3]==='source' ? `window.__TIKZ_EDITOR_APP_TEST_API__.setSource(${JSON.stringify(fs.readFileSync(process.argv[2],'utf8'))}); 'Source loaded'` : fs.readFileSync(process.argv[2],'utf8');
 console.log(JSON.stringify(await evaluate(script),null,2));
 }
}finally{ws.close();}
