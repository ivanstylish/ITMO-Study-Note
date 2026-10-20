from pathlib import Path
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from lxml import etree
from docx import Document
import json, re, struct, os

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
TARGET=ROOT/'3310_Чжун_Цзяцзюнь_УИР2_精简版.docx'
STAGING=WORK/'formatted.docx'

def hash_file(path):return sha256(path.read_bytes()).hexdigest()
protected=[ROOT/'3310_Чжун_Цзяцзюнь_УИР2.docx',ROOT/'lab2_variant15.py']
protected += [p for parent in [ROOT/'Calculation_data',ROOT/'WinMark'] for p in parent.rglob('*') if p.is_file()]
before={str(p):hash_file(p) for p in protected}
source=Document(TARGET)
d=Document(TARGET)

def four(value):
    # Round the saved value once; the six-place display can lie on a rounding boundary.
    n=Decimal.from_float(value) if isinstance(value,float) else Decimal(str(value).replace(',','.'))
    return format(n.quantize(Decimal('0.0001'),rounding=ROUND_HALF_UP),'f').replace('.',',')

def replace(paragraph,text):
    props=deepcopy(paragraph.runs[0]._r.rPr) if paragraph.runs and paragraph.runs[0]._r.rPr is not None else None
    paragraph.clear();run=paragraph.add_run(text)
    if props is not None:run._r.insert(0,props)

changes=[]
def cell(table,row,col,value,star=False):
    c=d.tables[table].cell(row,col)
    old=c.text
    # Verify that this is the same stored result as before, then change only display precision.
    if isinstance(value,float):
        assert abs(float(old.rstrip('*').replace(',','.'))-value)<0.00000051,(table,row,col,old,value)
    text=four(value)+('*' if star else '')
    replace(c.paragraphs[0],text)
    changes.append({'table':table,'row':row,'column':col,'before':old,'after':text})

verification=json.loads((ROOT/'Calculation_data/WinMark/verification.json').read_text(encoding='utf-8'))
cases={c['model']:c['metrics'] for c in verification['checks']}

# Form 1: use the actual saved stationary probabilities, without solving again.
for system in (1,2):
    raw=(ROOT/f'Calculation_data/WinMark/system{system}.mrk').read_bytes()
    n=struct.unpack_from('<H',raw,51)[0]
    probabilities=struct.unpack_from('<'+'f'*n,raw,53+n*n*12)
    for k,value in enumerate(probabilities):cell(7,k+1,2 if system==1 else 4,value)

# Form 2: all numerical result columns, including trailing zeros and nominal-load stars.
for system in (1,2):
    metrics=cases[f'system{system}_complete']
    for table,names in [(9,['A','U','L','N']),(10,['W','T','R','X'])]:
        for group,name in enumerate(names):
            for j in range(1,5):
                if system==1 and name=='R' and j<4:continue
                key=name+str(j) if j<4 else name
                cell(table,group*4+j,system+2,metrics[key],system==1 and name=='A' and j<4)

# Numerical consistency checks retain scientific notation for the small residuals.
for row in [1,3,4,5]:
    for col in (1,2):cell(11,row,col,source.tables[11].cell(row,col).text)

# Variation: lambda is an input; only the calculated Lq and throughput are formatted.
for step in range(1,11):
    for system in (1,2):
        metrics=cases[f'system{system}_lambda{step:02}']
        cell(12,step,system,metrics['L'])
        cell(12,step,system+2,metrics['X'])

for p in d.paragraphs:
    if p.text.startswith('Вероятности MARK округлены'):
        replace(p,'Вероятности и характеристики MARK приведены с четырьмя знаками после запятой. Проверка выполнена до округления: |Σπ−1|<10⁻⁶, max|πQ|<10⁻⁷; для высокоточного контрольного решения max|πQ|<10⁻¹².')
    elif p.text.startswith('Средние загрузки одного прибора') or p.text.startswith('При λ=0,5 с⁻¹ по критерию'):
        replace(p,re.sub(r'\d+,\d{5,}',lambda m:four(m.group(0)),p.text))

# Input tables, state codes, intensity matrices and all mathematical expressions remain intact.
for i in [0,1,2,3,4,5,6,8]:assert d.tables[i]._tbl.xml==source.tables[i]._tbl.xml
assert [etree.tostring(x)for x in d._element.xpath('.//m:oMath')]==[etree.tostring(x)for x in source._element.xpath('.//m:oMath')]
assert all(a._inline.xml==b._inline.xml for a,b in zip(source.inline_shapes,d.inline_shapes))
assert [p._p.xml for p in source.paragraphs[:27]]==[p._p.xml for p in d.paragraphs[:27]]
assert d.tables[11].cell(2,1).text==source.tables[11].cell(2,1).text
assert d.tables[11].cell(2,2).text==source.tables[11].cell(2,2).text
for entry in changes:assert re.fullmatch(r'-?\d+,\d{4}\*?',entry['after'])
assert all(hash_file(Path(name))==old for name,old in before.items())
d.save(STAGING)
os.replace(STAGING,TARGET)
(WORK/'format_audit.json').write_text(json.dumps({'target':str(TARGET),'formatted_numeric_cells':len(changes),'changes':changes,'protected_file_hashes':before,'precision':'Four fractional digits, rounded once from stored MARK results; scientific residuals preserved'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Formatted',len(changes),'numerical result cells; input data, models and raw calculations preserved.')
print('Queue lengths:',d.tables[9].cell(12,3).text,d.tables[9].cell(12,4).text)
print('Variation first queue entry:',d.tables[12].cell(1,1).text)
