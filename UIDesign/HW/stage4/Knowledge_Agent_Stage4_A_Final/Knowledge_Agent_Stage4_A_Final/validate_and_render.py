from pathlib import Path
import argparse,subprocess,re,json,concurrent.futures,threading

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--chrome',default=r'C:\Program Files\Google\Chrome\Application\chrome.exe')
parser.add_argument('--screenshots',action='store_true')
args=parser.parse_args()
startup=None
if hasattr(subprocess,'STARTUPINFO'):
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW

def browser(extra,url,profile):
    cmd=[args.chrome,'--headless=new','--disable-gpu','--no-first-run','--no-sandbox','--disable-extensions','--hide-scrollbars','--user-data-dir='+str(profile)]+extra+[url]
    return subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=50,startupinfo=startup)

result=browser(['--window-size=1363,1023','--virtual-time-budget=12000','--dump-dom'],(root/'web-source/capture.html').as_uri()+'?capture=1',root/'export-browser')
match=re.search(r'<script id="scene-data" type="application/json">(.*?)</script>',result.stdout,re.S)
if not match:raise RuntimeError('Browser export failed: '+result.stderr[-1000:])
export=json.loads(match[1]);scenes=export['scenes']
assert len(scenes)==91
assert all(c[1] for c in export['checks']),export['checks']
assert not any(a['overflows'] or a['clippedText'] for a in export['audits'])
scene_ids={s['id'] for s in scenes}
def visit(d):
    yield d
    for child in d.get('children',[]):yield from visit(child)
def norm(t):return re.sub(r'\s+','',t).casefold()
baseline=json.loads((root/'expected-content.json').read_text(encoding='utf-8'))
preserved=0
for s in scenes:
    nodes=list(visit(s['tree']));dom_ids={n.get('domId') for n in nodes}
    assert all(a['to'] in scene_ids and a['domId'] in dom_ids for a in s['actions']),s['id']
    assert all(n['w']>0 and n['h']>0 for n in nodes),(s['id'],'invalid dimensions')
    if s['id']<=81:
        actual=norm(' '.join(n['text'] for n in nodes if n['kind']=='text'))
        missing=[t for t in baseline[str(s['id'])] if norm(t) not in actual]
        assert not missing,(s['id'],missing)
        preserved+=len(baseline[str(s['id'])])
(root/'scenes.json').write_text(json.dumps(scenes,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(root/'code.js').write_text('const SCENES='+json.dumps(scenes,ensure_ascii=False,separators=(',',':'))+';\n'+(root/'importer.js').read_text(encoding='utf-8'),encoding='utf-8')
report={'mainScreens':81,'zoomScreens':10,'allScenes':91,'sourceActions':sum(len(s['actions']) for s in scenes),'preservedTextAssertions':preserved,'interactions':export['checks'],'audits':export['audits'],'fonts':['Segoe UI','Georgia','Courier New'],'nativeFigmaVerified':False}
(root/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['allScenes','sourceActions','preservedTextAssertions','interactions']}),flush=True)

if args.screenshots:
    output=root/'previews';output.mkdir(exist_ok=True)
    assignments=threading.local();counter=0;lock=threading.Lock()
    def screenshot(s):
        global counter
        if not hasattr(assignments,'profile'):
            with lock:counter+=1;assignments.profile=root/('screenshot-browser-'+str(counter))
        path=output/(str(s['id']).zfill(2)+'.png')
        # Keep viewport height at 936; full content is available through vertical scrolling in Figma.
        result=browser(['--window-size=1363,1023','--virtual-time-budget=700','--screenshot='+str(path)],(root/'web-source/index.html').as_uri()+'?capture=1#'+str(s['id']),assignments.profile)
        assert path.exists(),(s['id'],result.stderr[-500:])
        return s['id']
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for i,n in enumerate(pool.map(screenshot,scenes[:81]),1):
            if i%10==0 or i==81:print(f'Visual capture {i}/81',flush=True)
