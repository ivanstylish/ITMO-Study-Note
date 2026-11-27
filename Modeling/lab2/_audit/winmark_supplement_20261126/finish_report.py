from pathlib import Path
import hashlib
import re
import struct
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from PIL import Image

work = Path(__file__).resolve().parent
root = work.parents[1]
source = root / '3310_Чжун_Цзяцзюнь_УИР2.docx'
base = root / 'Calculation_data/WinMark'
native = base / 'ReportSupplement'
initial_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert initial_hash == '44e60f7a44319feb1cd65cb3e0beb95177da723d48bdb06aaa68bf456d8b6665'

def scan_tables(path):
    s = path.read_text(encoding='cp1251')
    out = {}
    for block in re.findall(r'<TABLE[^>]*>(.*?)</TABLE>',s,re.S|re.I):
        rows = re.findall(r'<TR><TH>([A-Za-z][A-Za-z0-9]*)<TD>([^<]+(?:<TD>[^<]+)*)',block,re.I)
        for key, vals in rows:
            out[key]=[float(v) for v in vals.split('<TD>')]
    assert out['lambda'] == [i/10 for i in range(1,11)]
    return out

data = [scan_tables(native / f'system{i}.html') for i in (1,2)]
formulas = []
for i, (n,scan) in enumerate(zip((11,36),data),1):
    assert all(abs(sum(scan[f'p{k}'][j] for k in range(n))-1)<2e-5 for j in range(10))
    rows = list(re.finditer(r'(\w+) = ([^<]+?) = ([.\d-]+)<br>',(base/f'system{i}.html').read_text(encoding='cp1251')))
    formulas.append([m.groups() for m in rows])
    assert len(rows)==(30 if i==1 else 32)
    for step in range(1,11):
        original = (base/f'Variation/system{i}_lambda{step:02d}.html').read_text(encoding='cp1251')
        for metric in ('L','R','X','W','T') + tuple(f'p{k}' for k in range(n)):
            m = re.search(r'(?:<P>|<br>)'+metric+r' = (?:[^<]+ = )?([.\d-]+)<br>',original)
            assert m and abs(scan[metric][step-1]-float(m[1]))<2e-5,(i,step,metric)

# Compare the actual graph project's saved WinMark series with both full models.
b = (native/'comparison.mrk').read_bytes()
assert struct.unpack_from('<H',b,0)[0]==6
n=11
offset = 72 + n*n*12 + n*4 + 16 + 12 + n*10*4
for j,(index,key) in enumerate(((2,'L'),(3,'L'),(4,'R'),(5,'R'))):
    values=struct.unpack_from('<10f',b,offset+index*40)
    assert max(abs(x-y) for x,y in zip(values,data[j%2][key]))<2e-6,(index,key,values)

img=Image.open(work/'loss_window.png')
assert img.width>=1400 and img.height>=700
img.crop((9,53,1430,735)).save(native/'loss_comparison.png')

doc = Document(source)
parents = list(doc._element.body)
unchanged = {el:el.xml for el in parents}
old = doc.paragraphs
def body(s):return doc.add_paragraph(s,style='RBody')
def title(s):
    p=doc.add_paragraph(s,style='RTitle')
    p.paragraph_format.page_break_before=True
    p.paragraph_format.keep_with_next=True
    return p
def caption(s):
    p=doc.add_paragraph(s,style='RCaption')
    p.paragraph_format.keep_with_next=True
    return p
def table(headers,rows,widths,size=10):
    t=doc.add_table(rows=0,cols=len(headers))
    borders=OxmlElement('w:tblBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e=OxmlElement('w:'+edge)
        for key,val in [('val','single'),('sz','4'),('color','C0C0C0')]:e.set(qn('w:'+key),val)
        borders.append(e)
    t._tbl.tblPr.append(borders)
    t.autofit=False
    for col,width in zip(t.columns,widths):col.width=Cm(width)
    for j,line in enumerate([headers,*rows]):
        row=t.add_row()
        trpr=row._tr.get_or_add_trPr()
        trpr.append(OxmlElement('w:cantSplit'))
        if not j:trpr.append(OxmlElement('w:tblHeader'))
        for k,(cell,value,width) in enumerate(zip(row.cells,line,widths)):
            cell.width=Cm(width)
            p=cell.paragraphs[0]
            p.paragraph_format.space_before=Pt(1)
            p.paragraph_format.space_after=Pt(1)
            p.paragraph_format.line_spacing=1
            if len(headers)>3 or k==len(headers)-1:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            run=p.add_run(str(value))
            run.font.name='Times New Roman';run.font.size=Pt(size);run.bold=j==0
    return t
def decimal(x):return f'{float(x):.4f}'.replace('.',',')

old[80].runs[0].text='Таблица 5. Матрица системы 2. Строки S0–S35, столбцы S0–S18 и S19–S35 на двух снимках. Диагональ приведена в таблице А.2.'
for run in old[80].runs[1:]:run.text=''
before=old[129]
before.runs[0].text='На рисунках 5 и 6 и в таблице 11 представлены результаты варьирования λ от 0,1 до 1,0 с⁻¹ с шагом 0,1 при неизменных b, rᵢ и ёмкостях. По оси абсцисс указан номер шага k, которому соответствует λ = 0,1k с⁻¹. Синяя линия соответствует системе 1, красная — системе 2.'
for run in before.runs[1:]:run.text=''
old[131].runs[0].text='Рисунок 5. Средняя суммарная длина очередей при варьировании λ (WinMark).'
for run in old[131].runs[1:]:run.text=''

loss=doc.add_paragraph(style='RBody')
loss.alignment=WD_ALIGN_PARAGRAPH.CENTER
loss.paragraph_format.keep_with_next=True
loss.add_run().add_picture(str(native/'loss_comparison.png'),width=Cm(17.8))
label=doc.add_paragraph('Рисунок 6. Вероятности потери заявок при варьировании λ (WinMark).',style='RCaption')
result=body('На всех десяти шагах вероятность потери в системе 1 ниже. При заданной интенсивности λ = 0,5 с⁻¹ она равна 0,4223 для системы 1 и 0,6034 для системы 2. Результаты по потерям и временным характеристикам приведены в таблице В.1.')
for p in (loss,label,result):old[134]._p.addprevious(p._p)

title('Приложение А. Параметры моделей WinMark')
body('При варьировании изменяется только интенсивность входного потока. В матрицах поступления заданы через элемент lambda и коэффициенты переходов. Интенсивности завершения обслуживания постоянны. Диагональный элемент равен сумме остальных элементов строки с обратным знаком.')
caption('Таблица А.1. Параметры расчёта в WinMark.')
table(['Параметр','Система 1','Система 2'],[
    ('Размер матрицы','11 × 11','36 × 36'),
    ('Количество формул расчёта','30','32'),
    ('Заданное λ, с⁻¹','0,5000','0,5000'),
    ('Начальное λ, шаг и число точек','0,1000 / 0,1000 / 10','0,1000 / 0,1000 / 10'),
    ('Интенсивности поступления','λrᵢ / Σсвоб. rⱼ к свободному прибору, λ в общий накопитель','0,7λ к П1, 0,2λ к П2, 0,1λα к ветви A и 0,1λ(1−α) к ветви B'),
    ('Интенсивности завершения, с⁻¹','0,1000 на занятый прибор, 0,3000 при непустой очереди','П1, П2 — 0,1000. Ветви A, B — 0,166196846 и 0,033803154'),
    ('Вместимость накопителей','3 общих места','2 / 1 / 0'),
],[5.1,6.3,6.8],11)
body('В графиках для системы 2 суммарная очередь вычисляется по локальным стационарным распределениям П1 и П2. Общая вероятность потери учитывает заполнение каждого прибора с весом, равным вероятности направления заявки к нему. Значения обеих кривых сверены с результатами расчёта отдельных моделей на каждом шаге.')
body('На снимках окна ввода матрицы на диагонали указаны номера состояний. Численные значения диагонали при заданном λ = 0,5 с⁻¹ приведены в таблице А.2. На первом снимке матрицы системы 2 показаны столбцы S0–S18, на втором — S19–S35.')
diag=[]
for i,n in enumerate((11,36),1):
    raw=(base/f'system{i}.mrk').read_bytes()
    q = struct.unpack_from(f'<{n*n}f',raw,53)
    assert all(abs(sum(q[k*n:(k+1)*n]))<1e-7 for k in range(n))
    diag.append([decimal(q[k*n+k]) for k in range(n)])
caption('Таблица А.2. Диагональные элементы матриц Qₛₛ, с⁻¹.')
table(['Состояние','Система 1','Состояние','Система 2','Состояние','Система 2','Состояние','Система 2'],[
    [f'S{k}' if k<11 else '—',diag[0][k] if k<11 else '—',*(field for j in (k,k+12,k+24) for field in (f'S{j}',diag[1][j]))] for k in range(12)
],[2.25]*8,9.5)

title('Приложение Б. Формулы и значения характеристик WinMark')
body('Расчёт в точке λ = 0,5 с⁻¹. В формулах p0, p1, … обозначают вероятности S0, S1, … . В столбце формул сохранён синтаксис WinMark, числовые результаты приведены с четырьмя знаками.')
for i,rows in enumerate(formulas,1):
    if i==2:
        p=caption('Таблица Б.2. Формулы и значения характеристик системы 2.')
        p.paragraph_format.page_break_before=True
    else:caption('Таблица Б.1. Формулы и значения характеристик системы 1.')
    table(['Имя','Формула WinMark','Значение'],[(k,expr.replace('+','+\u200b'),decimal(v)) for k,expr,v in rows],[1.6,13.6,3],10)

title('Приложение В. Дополнительные результаты варьирования WinMark')
body('Длины очередей и производительность приведены в таблице 11. Ниже приведены вероятности потерь, время ожидания, время пребывания и вероятности состояний по тем же десяти шагам. Шаг 5 соответствует исходному варианту.')
caption('Таблица В.1. Потери и средние времена в обеих системах.')
table(['λ, с⁻¹','Потери 1','Потери 2','Ожид. 1, с','Ожид. 2, с','Преб. 1, с','Преб. 2, с'],[
    [f'0,{j+1}' if j<9 else '1,0',*(decimal(scan[k][j]) for k in ('R','W','T') for scan in data)] for j in range(10)
],[2.0,2.7,2.7,2.7,2.7,2.7,2.7],10)
pi_header=['Состояние',*[f'0,{i}' for i in range(1,10)],'1,0']
for num,(i,start,end) in enumerate(((1,0,11),(2,0,36)),2):
    p=caption(f'Таблица В.{num}. Стационарные вероятности системы {i} при варьировании λ, с⁻¹.')
    if i==2:p.paragraph_format.page_break_before=True
    table(pi_header,[[f'S{k}',*map(decimal,data[i-1][f'p{k}'])] for k in range(start,end)],[2.15]+[1.6]*10,9.5)

# No other existing content node is touched.
modified={old[80]._p,old[129]._p,old[131]._p}
for el,xml in unchanged.items():
    if el not in modified:assert el.xml==xml
out=root/'3310_Чжун_Цзяцзюнь_УИР2_补充版.docx'
doc.save(out)
assert hashlib.sha256(source.read_bytes()).hexdigest()==initial_hash
print(out)
print('Verified both WinMark scans against 20 earlier point runs. Graph arrays match the individual model results.')
