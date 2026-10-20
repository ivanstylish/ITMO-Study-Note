from pathlib import Path
from copy import deepcopy
import json, re, hashlib
from docx import Document
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '_audit' / 'figure_cleanup_20261019'
WORK.mkdir(exist_ok=True)
SOURCE = ROOT / '3310_Чжун_Цзяцзюнь_УИР2.docx'
OUTPUT = ROOT / '3310_Чжун_Цзяцзюнь_УИР2_Для_WinMark.docx'

def actual_values():
    rows = []
    for k in range(1, 11):
        row = {'lambda': k / 10}
        for system in (1, 2):
            filename = ROOT / 'Calculation_data' / 'WinMark' / 'Variation' / f'system{system}_lambda{k:02}.html'
            html = filename.read_text(encoding='cp1251')
            match = re.search(r'(?:<P>|<br>)L = [^<]* = ([0-9.]+)<br>', html)
            if not match:
                raise ValueError(f'No actual L value in {filename}')
            row[f'system{system}'] = float(match.group(1))
        rows.append(row)
    return rows

def replace(paragraph, text):
    props = deepcopy(paragraph.runs[0]._r.rPr) if paragraph.runs and paragraph.runs[0]._r.rPr is not None else None
    paragraph.clear()
    r = paragraph.add_run(text)
    if props is not None:
        r._r.insert(0, props)

def edit():
    d = Document(SOURCE)
    paragraphs = d.paragraphs
    expected = [(s._inline.xpath('.//a:blip')[0].get(qn('r:embed')), s.width, s.height) for s in d.inline_shapes]
    assert len(expected) == 5
    old_rid = expected[-1][0]
    old_target = d.part.related_parts[old_rid].partname
    assert str(old_target) == '/word/media/image5.png'
    # Replace the four-panel image with the criterion graph from native MARK exports.
    # Reuse the relationship so the obsolete image is absent from the DOCX package.
    new_rid, new_image = d.part.get_or_add_image(str(WORK / 'queue_comparison.png'))
    old_part = d.part.related_parts[old_rid]
    old_hash = hashlib.sha256(old_part.blob).hexdigest()
    new_part = d.part.related_parts[new_rid]
    d.part.rels[old_rid]._target = new_part
    if new_rid != old_rid:
        d.part.drop_rel(new_rid)
    shape = d.inline_shapes[-1]
    shape.width = expected[-1][1]
    shape.height = round(shape.width * 940 / 1600)
    props = shape._inline.docPr
    props.set('name', 'Средняя суммарная очередь по данным WinMark')
    props.set('descr', 'Критерий д: Lq двух систем при изменении λ от 0,1 до 1,0 с⁻¹. Источник: фактические HTML-отчёты WinMark; не снимок экрана программы.')
    replace(paragraphs[108], 'Для сравнительного анализа используется заданный критерий «д» — минимальная суммарная средняя длина очередей. При b=10 с, неизменных rᵢ и ёмкостях λ изменяется от 0,1 до 1,0 с⁻¹. Кривые построены по фактическим значениям Lq из HTML-отчётов WinMark. Синяя линия — система 1, коричневая — система 2.')
    replace(paragraphs[110], 'Рисунок 5. Средняя суммарная длина очередей по результатам WinMark.')
    replace(paragraphs[112], 'Кривые очередей пересекаются между λ=0,5 и 0,6 с⁻¹. При заданном λ=0,5 с⁻¹ Lq¹=1,925832 < Lq²=1,976939, поэтому выбирается система 1. С ростом λ длины очередей стремятся к трём заявкам. Выбор по этому критерию зависит от интенсивности входа и организации обслуживания.')
    replace(paragraphs[133], '4. При изменении λ сохранены b=10 с, r=(0,7;0,2;0,1), ёмкости и параметры гиперэкспоненциального обслуживания. Для каждой точки заново рассчитаны вероятности и характеристики в MARK. На рисунке 5 показан заданный критерий «д»; график построен по фактическим значениям Lq из экспортированных HTML-отчётов WinMark.')
    # Existing cover, structural diagrams, transition graphs and data tables stay intact.
    assert all(a.xml == b.xml for a, b in zip(list(Document(SOURCE)._element.body)[:26], list(d._element.body)[:26]))
    assert len(d.inline_shapes) == 5
    for i in range(4):
        s = d.inline_shapes[i]
        rid = s._inline.xpath('.//a:blip')[0].get(qn('r:embed'))
        assert (rid, s.width, s.height) == expected[i]
    source_tables = Document(SOURCE).tables
    assert all(a._tbl.xml == b._tbl.xml for a, b in zip(source_tables, d.tables))
    d.save(OUTPUT)
    # Native comparisons and captions have to agree with the already reported table.
    for k, row in enumerate(actual_values(), 1):
        for system in (1, 2):
            value = float(d.tables[12].cell(k, system).text.replace(',', '.'))
            assert abs(value - row[f'system{system}']) < 0.00000051
    (WORK / 'change_record.json').write_text(json.dumps({'source':str(SOURCE),'output':str(OUTPUT),'removed_image_sha256':old_hash,'removed_subplots':['loss probability','throughput','sojourn time'],'retained_figures':['system 1 structure','system 1 transitions','system 2 structure','system 2 transitions','Lq comparison from actual WinMark exports']}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(OUTPUT)

if __name__ == '__main__':
    import sys
    if sys.argv[-1] == 'data':
        (WORK / 'queue_values.json').write_text(json.dumps(actual_values(), indent=2), encoding='utf-8')
        print('Read 20 Lq values from actual native WinMark HTML exports.')
    else:
        edit()
