(async()=>{
 const api=window.__TIKZ_EDITOR_APP_TEST_API__;
 let captured;
 const create=URL.createObjectURL;
 URL.createObjectURL=function(blob){captured=blob;return create.call(this,blob)};
 try{await api.runCommand('file.export-svg-download');await new Promise(r=>setTimeout(r,800));return captured?{svg:await captured.text(),type:captured.type}: {error:'No SVG captured',text:document.body.innerText.slice(-3000)};}finally{URL.createObjectURL=create}
})()
