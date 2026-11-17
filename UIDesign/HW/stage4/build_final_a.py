from pathlib import Path
import shutil,re,json

base=Path(__file__).resolve().parent
old=base/'Knowledge_Agent_Figma_Editable'/'Knowledge_Agent_Figma_Editable'
out=base/'Knowledge_Agent_Stage4_A_Final'
web=out/'web-source';web.mkdir(parents=True,exist_ok=True)
for name in ['index.html','app.js','data.js','style.css']:
    shutil.copy2(old/'web-source'/name,web/name)
css=(web/'style.css').read_text(encoding='utf-8')
css=re.sub(r'@font-face\{[^}]+\}','',css)
css=css.replace("'Bodoni Moda',Didot,'Times New Roman',serif","Georgia,'Times New Roman',serif")
css += '''
/* Garden A / installed Windows typography. */
:root{--bg:#f7f8f6;--paper:#fff;--ink:#232621;--muted:#606b59;--line:#dfe5d9;--lime:#d1fca6;--green:#34745c}
body{font-family:'Segoe UI',Arial,sans-serif;font-size:14px}
button,input,textarea,select{font-family:inherit}
.brand-mark{font-family:'Segoe UI',Arial,sans-serif;font-weight:600}
.btn{min-height:44px;font-size:13px;font-weight:600;border-radius:11px;border-width:1px;padding:11px 17px}
.btn .ico{width:16px;height:16px}.nav button{font-size:14px;font-weight:500}
.subtitle,.message p,.meta-value{color:#596650}.subtitle{font-size:14px;line-height:1.6}
.muted,.small,.mono,.eyebrow,.step-state,.meta-label,.graph-legend,.neighbor small,.node-meta,.setting-row>span:first-child{color:#606b59}
.small{font-size:12px}.mono{font-size:12px}.step-title{font-size:13px}.step-state{font-size:11px}.step-num{font-size:12px}
.badge,.pill{font-size:11px}.setting-row{font-size:13px;gap:20px}.setting-row>span:last-child{font-size:13px;overflow-wrap:anywhere;text-align:right}
.table th{font-size:12px;color:#606b59}.table td{font-size:13px}.table{table-layout:fixed}.table th:first-child{width:36%}.table th:nth-child(2){width:20%}.table th:nth-child(3){width:17%}.table th:last-child{width:5%}.table td{overflow-wrap:anywhere}
.file-table-head,.file-option{display:grid;grid-template-columns:minmax(0,1fr) 80px 104px;align-items:center;column-gap:24px;padding-left:20px;padding-right:20px}
.file-table-head{margin-bottom:8px}.file-table-head h2{margin:0}.file-table-head>span{font-size:12px;text-align:right}
.file-table-head:after{content:''}.file-option{padding-top:20px;padding-bottom:20px;min-height:85px}.file-option:last-child{border-bottom:0}
.file-option>span:first-child{display:flex;align-items:center;gap:10px;overflow-wrap:anywhere;min-width:0}
.file-option>span:nth-child(2){width:80px;text-align:right;font-size:12px;font-variant-numeric:tabular-nums}.file-option>.btn{width:104px}
.source-rows{display:flex;flex-direction:column;gap:20px}.source-row{display:flex;align-items:flex-start;justify-content:space-between;gap:22px;min-width:0}
.source-cell{font-size:14px;line-height:1.65;color:#44513c;min-width:0;overflow-wrap:anywhere}.source-cell:first-child{flex:1}.source-cell.source-heading{font-size:17px;font-weight:600;color:#232621}.source-cell.source-status{flex:0 1 auto;font-size:12px;color:#476e37;white-space:normal}
.source-row .check{flex:0 0 18px;margin:5px 0}.source-row .source-cell:not(:first-child){max-width:42%}.source-row.single .source-cell{max-width:100%}
.source-card{padding:28px;min-height:260px}.model-choice{display:flex;align-items:center;gap:12px;margin-bottom:22px;font-size:13px;color:#596650}.model-choice select{border:1px solid var(--line);border-radius:11px;background:white;padding:9px 13px;font-size:13px;min-width:180px;color:var(--ink)}
.analysis-answer{font-weight:500}.history-card .mono{white-space:nowrap}.graph-tools .icon-button{width:34px;height:34px}.graph-side .mono{overflow-wrap:anywhere}.graph-world{touch-action:none}
.card{box-shadow:none}.drop-format{color:#606b59;font-size:13px}.drop-title{font-weight:600}.side-recent>button{font-size:13px;color:#596650}.crumb{font-size:12px}.connected{font-size:12px}.explanation,.change-main p,.extract-line{color:#596650;font-size:13px}
.settings-grid .setting-row{align-items:flex-start}.settings-grid .setting-row>span{min-width:0}.settings-card h2{font-size:17px}.model-setting-button{padding:5px 10px;border:1px solid var(--line);border-radius:8px;background:#fff}
.source-extra{font-size:13px}.source-warning{border-left:3px solid #ab785d}.source-note{border-left:3px solid var(--green)}
@media(max-width:760px){.file-table-head,.file-option{grid-template-columns:minmax(0,1fr) 52px 88px;column-gap:10px;padding-left:0;padding-right:0}.file-option>span:nth-child(2){width:52px}.file-option>.btn{width:88px;font-size:12px;padding:10px}.file-option>span:first-child{gap:7px;font-size:12px}.file-table-head h2{font-size:17px}.source-row{flex-wrap:wrap;gap:8px}.source-cell{font-size:13px}.source-row .source-cell:not(:first-child){max-width:100%}.model-choice{flex-wrap:wrap}.settings-grid .setting-row{font-size:13px}.table{min-width:650px}.subtitle{font-size:13px}.nav button{font-size:13px}.btn{font-size:12px}.side-card{display:none}}
'''
(web/'style.css').write_text(css,encoding='utf-8')
app=(web/'app.js').read_text(encoding='utf-8')
app=app.replace('<div class="card-head"><h2>Имя файла</h2>','<div class="file-table-head"><h2>Имя файла</h2>')
app=app.replace("${ico('file')} &nbsp; ${f[0]}","${ico('file')}<span>${f[0]}</span>")
app=app.replace('if([9,10,16,17,54,55,63,64,69,74,81].includes(current)&&!original)',"if([9,10,16,17,23,54,55,63,64,69,74,81].includes(current)&&!original&&!document.body.classList.contains('capture'))")
app=app.replace('17:15,54:51','17:15,23:15,54:51')
# These controls are the review utility, not product content.
start=app.index("$('#reviewbar').innerHTML=`")
end=app.index('`;\n',start)+2
app=app[:start]+'''$('#reviewbar').innerHTML=`<button onclick="go(current===1?81:current-1)" aria-label="Предыдущий экран">←</button><span class="page-counter">${String(current).padStart(2,'0')} / 81</span><button onclick="go(current===81?1:current+1)" aria-label="Следующий экран">→</button><span class="separator"></span><button onclick="drawPicker();document.querySelector('#screen-picker').showModal()">Все экраны</button>`;'''+app[end:]
app=app.replace("'<em>Новая компоновка</em>'","''")
(web/'app.js').write_text(app,encoding='utf-8')
index=(web/'index.html').read_text(encoding='utf-8').replace('<script src="app.js"></script>','<script src="app.js"></script><script src="final.js"></script>')
(web/'index.html').write_text(index,encoding='utf-8')
print(json.dumps({'output':str(out),'font':'Segoe UI','brandFont':'Georgia','sourceScreens':81}))
