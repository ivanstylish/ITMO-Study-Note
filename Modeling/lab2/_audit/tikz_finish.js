(()=>{
 const api=window.__TIKZ_EDITOR_APP_TEST_API__;
 api.runCommand('view.toggle-grid');
 api.runCommand('view.toggle-inspector-panel');
 api.runCommand('view.fit-to-content');
 const workspace=JSON.parse(localStorage.getItem('tikz-editor:workspace'));
 if(workspace.documents.length!==2)throw Error('Expected two documents');
 for(let i=0;i<2;i++)workspace.documents[i].title=`System ${i+1} — state graph`;
 localStorage.setItem('tikz-editor:workspace',JSON.stringify(workspace));
 return {documents:workspace.documents.map(d=>({title:d.title,sourceLength:d.source.length})),states:api.getSceneTextDebug().filter(t=>/^S\d+$/.test(t.text)).length};
})()
