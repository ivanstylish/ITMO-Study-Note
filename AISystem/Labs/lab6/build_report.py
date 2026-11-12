"""Build a Russian report from saved results, retaining the original cover."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import numpy as np
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt, Cm
from lxml import etree
from mnist_lab.data import ROOT


def build():
    output, qa = ROOT / 'output', ROOT / '_qa'
    qa.mkdir(exist_ok=True)
    summary = json.loads((output / 'summary.json').read_text(encoding='utf-8'))
    drawings = json.loads((output / 'drawings.json').read_text(encoding='utf-8')) if (output / 'drawings.json').exists() else []
    template = ROOT.parent / 'lab1' / 'Лабораторная_работа_1.docx'
    complete = len(drawings) >= 2 and any(r['true'] == r['predicted'] for r in drawings[:3])
    final = ROOT / ('Лабораторная_работа_6.docx' if complete else 'Лабораторная_работа_6_проект.docx')
    doc = Document(template)
    body = doc._element.body
    for child in list(body)[26:-1]:
        body.remove(child)
    for node in body[9].iter(qn('w:t')):
        node.text = node.text.replace('1', '6')
    for role, size in [('Body', 12), ('Heading', 14), ('Caption', 10), ('Code', 8)]:
        style = doc.styles.add_style('Lab6 ' + role, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles['Normal']
        style.font.name = 'Consolas' if role == 'Code' else 'Times New Roman'
        style.font.size = Pt(size)
        style.font.bold = role == 'Heading'
        pf = style.paragraph_format
        pf.line_spacing = 1.15 if role == 'Body' else 1
        pf.space_after = Pt(0 if role == 'Code' else 6)
        pf.first_line_indent = Cm(1.25 if role == 'Body' else 0)
        pf.widow_control = role != 'Code'

    def para(text, role='Body'):
        p = doc.add_paragraph(str(text), 'Lab6 ' + role)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if role == 'Body' else WD_ALIGN_PARAGRAPH.LEFT
        return p

    def heading(text):
        p = para(text, 'Heading')
        p.paragraph_format.page_break_before = True
        p.paragraph_format.keep_with_next = True

    def picture(name, caption, width=16):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(output / 'figures' / name), width=Cm(width))
        para(caption, 'Caption')

    def table(headers, rows):
        t = doc.add_table(rows=1, cols=len(headers))
        t.style = 'Table Grid'
        for cells, values in [(t.rows[0].cells, headers)] + [(t.add_row().cells, r) for r in rows]:
            for cell, value in zip(cells, values):
                cell.text = str(value)
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.name = 'Times New Roman'; run.font.size = Pt(9)

    heading('ЦЕЛЬ И ПОСТАНОВКА ЗАДАЧИ')
    para('Цель работы — реализовать многослойную нейронную сеть на уровне матричных операций и распознавать рукописные цифры MNIST. Реализованы собственные слои, обратное распространение ошибки, оптимизатор Adam и загрузчик IDX. NumPy выполняет только операции над массивами; готовые модели и автоматическое дифференцирование не используются.')
    para('Исследованы четыре архитектуры. Архитектура и эпоха выбираются по валидационной выборке; официальный тест используется только для итоговой оценки одной выбранной модели.')
    para(f"Лучшая модель — {summary['winner']}; accuracy на 10 000 тестовых изображениях составляет {summary['test_accuracy']:.2%}, ошибок — {summary['errors']}. Это оценка на MNIST, а не гарантия распознавания произвольного рисунка.")
    heading('МЕТОД И ОБРАТНОЕ РАСПРОСТРАНЕНИЕ')
    for text in [
        'Linear: X имеет форму N×d, W — d×h, b — h. Прямой проход: Y=XW+b. Обратный проход: dX=dY·Wᵀ, dW=Xᵀ·dY, db=ΣᵢdYᵢ. Слой запоминает X. Усреднение по батчу выполняется в градиенте функции потерь ровно один раз.',
        'ReLU: f(x)=max(0,x); производная равна 1 при x>0 и 0 иначе. Flatten меняет только форму массива и восстанавливает исходную форму при backward.',
        'Для численной устойчивости s=z−max(z). log pᵢ=sᵢ−log Σⱼexp(sⱼ). Кросс-энтропия L=−ΣₙΣᵢyₙᵢlog pₙᵢ/N, её градиент по логитам равен (p−y)/N. Вычисление log p напрямую предотвращает log(0) при очень малых вероятностях.',
        'He-инициализация: Wᵢⱼ∼N(0,2/d), b=0. Inverted Dropout использует маску M∼Bernoulli(1−q): H′=H⊙M/(1−q). На инференсе Dropout тождественен; при backward используется та же маска.',
        'Adam: mₜ=β₁mₜ₋₁+(1−β₁)gₜ, vₜ=β₂vₜ₋₁+(1−β₂)gₜ². Поправки: m̂ₜ=mₜ/(1−β₁ᵗ), v̂ₜ=vₜ/(1−β₂ᵗ). Обновление θ←θ−αm̂ₜ/(√v̂ₜ+ε). Приняты α=0,001, β₁=0,9, β₂=0,999, ε=10⁻⁸. Для каждой матрицы и смещения хранятся отдельные моменты; t увеличивается один раз на мини-батч.',
        'Точность accuracy = число верных прогнозов / число объектов. Матрица ошибок: строки — истинные цифры, столбцы — предсказанные. Для метрик train и val Dropout отключён, чтобы сравнение было одинаковым.'
    ]: para(text)
    heading('ДАННЫЕ И ПОДГОТОВКА')
    para('Использован оригинальный MNIST в формате IDX: 60 000 обучающих и 10 000 тестовых изображений 28×28. Файлы получены из открытого зеркала CVDF; контрольные MD5 проверяются перед чтением. Загрузчик самостоятельно читает big-endian заголовки, проверяет magic 2051/2049, размеры, длину данных и диапазон меток 0–9.')
    para('Изображения преобразованы в float32 и делятся на 255. Метки кодируются one-hot длины 10. Перестановка default_rng(42) выделяет первые 6000 индексов для val, остальные 54000 — для train. Это случайное, не стратифицированное разбиение. Индексы сохранены в output/split.npz.')
    table(['Цифра', 'Train', 'Val', 'Test'], [[i, summary['train_classes'][i], summary['val_classes'][i], summary['test_classes'][i]] for i in range(10)])
    picture('classes.png', 'Рисунок 1 — Распределение классов в исходной обучающей выборке.', 14)
    heading('ПРИМЕРЫ И ПРОТОКОЛ ОБУЧЕНИЯ')
    picture('examples.png', 'Рисунок 2 — Первые 25 изображений исходного MNIST.', 12)
    para('Во всех опытах: seed=42, 15 эпох, мини-батч 128, Adam с α=0,001, перемешивание перед каждой эпохой. После каждой эпохи loss и accuracy вычисляются на полном train и val без Dropout. Сохраняется эпоха с наибольшей val accuracy; при равенстве выбирается меньший val loss. При полном равенстве сохраняется первая эпоха/архитектура. Ранней остановки и подбора по тесту нет.')
    table(['Опыт', 'Архитектура', 'Dropout', 'Эпоха', 'Лучшая val accuracy'],
          [[r['name'], '→'.join(map(str, r['widths'])), r['dropout'], r['best']['epoch'], f"{r['best']['val_accuracy']:.2%}"] for r in summary['experiments']])
    for i, result in enumerate(summary['experiments'], 3):
        heading('ЭКСПЕРИМЕНТ ' + result['name'])
        picture(f"curves_{result['name']}.png", f'Рисунок {i} — Loss и accuracy на train и val.')
        best = result['best']
        para(f"Слои: {'→'.join(map(str, result['widths']))}; Dropout={result['dropout']}. Лучшая эпоха: {best['epoch']}; train accuracy={best['train_accuracy']:.2%}, val accuracy={best['val_accuracy']:.2%}; val loss={best['val_loss']:.4f}. Время обучения и оценки: {result['seconds']:.1f} с.")
        para('Рост train accuracy при ухудшении val loss указывает на возможное переобучение; рост уверенности в неверных ответах может увеличивать loss даже при стабильной accuracy.')
    heading('ИТОГОВАЯ ОЦЕНКА И АНАЛИЗ ОШИБОК')
    para(f"Выбрана модель {summary['winner']}. Test accuracy={summary['test_accuracy']:.4%}; test loss={summary['test_loss']:.4f}; неверных ответов {summary['errors']} из 10000. Тест оценён после завершения выбора модели.")
    picture('confusion.png', 'Рисунок 7 — Матрица ошибок на тестовой выборке.', 12)
    confusion = np.loadtxt(output / 'confusion_matrix.csv', delimiter=',', dtype=int)
    np.fill_diagonal(confusion, 0)
    pairs = np.dstack(np.unravel_index(np.argsort(confusion.ravel())[::-1][:5], (10, 10)))[0]
    para('Наиболее частые направленные ошибки: ' + '; '.join(f'{a}→{b}: {confusion[a,b]}' for a, b in pairs) + '.')
    para('Возможные причины — сходные петли и наклон штрихов, разрывы или соединения, необычный почерк и слабый контраст. Это гипотезы по изображениям ошибок, а не доказанная причинная связь. Полносвязная сеть не обладает встроенной инвариантностью к переносу.')
    heading('ПРИМЕРЫ ОШИБОК')
    picture('errors.png', 'Рисунок 8 — Первые 12 ошибочно распознанных тестовых объектов.', 15)
    heading('РАСПОЗНАВАНИЕ ВНЕШНИХ ИЗОБРАЖЕНИЙ')
    para('Алгоритм: чтение изображения и обработка ориентации, наложение прозрачности на белый фон, оттенки серого, выбор инверсии по медиане граничных пикселей, выделение области цифры, пропорциональное масштабирование до стороны не более 20 пикселей, размещение на чёрном холсте 28×28, перенос центра масс к (13,5;13,5), деление на 255. Перенос выполняется без циклического заворачивания пикселей. Пустое изображение отклоняется.')
    para('Сеть получает один объект формы 1×28×28. Сохранённые веса загружаются без обучения; Softmax возвращает десять вероятностей. Слишком тонкие штрихи, необычный наклон, цветной или неоднородный фон могут ухудшать результат. Вход должен содержать одну цифру на однотонном контрастном фоне.')
    if drawings:
        correct = sum(r['true'] == r['predicted'] for r in drawings)
        para(f'Проверены {len(drawings)} собственных рисунка из Paint; верно распознаны {correct}. В первых трёх попытках есть верный ответ, что удовлетворяет практическому условию задания. Это малая проверка применения, а не статистическая оценка качества на произвольном почерке.')
        table(['Файл', 'Истинная цифра', 'Прогноз', 'p прогноза', 'p истинной цифры'],
              [[r['file'], r['true'], r['predicted'], f"{r['probabilities'][r['predicted']]:.2%}",
                f"{r['probabilities'][r['true']]:.2%}"] for r in drawings])
        para('Штрихи исходных рисунков очень тонкие относительно большого холста. После уменьшения до 28×28 они становятся слабыми и отличаются от штрихов MNIST. Это возможная причина неопределённости и ошибки, а не доказательство её единственной причины. Предобработка и веса для этих рисунков не подбирались заново.')
        for r in drawings:
            heading('ПРОВЕРКА СОБСТВЕННОГО РИСУНКА ' + str(r['true']))
            picture(r['figure'], f"Файл {r['file']}: истинная цифра {r['true']}, прогноз {r['predicted']}.")
            ranked = np.argsort(r['probabilities'])[::-1][:3]
            para('Три наибольшие вероятности Softmax: ' + '; '.join(f"{i}: {r['probabilities'][i]:.2%}" for i in ranked) + '.')
            para('Ответ верный.' if r['true'] == r['predicted'] else 'Ответ неверный; исходный рисунок и ошибочный прогноз сохранены. Разница вероятностей двух ведущих классов мала, но даже высокая вероятность не гарантирует правильный ответ.')
    else:
        para('Практическая проверка на собственных рисунках будет выполнена отдельно; данный проект отчёта не содержит результатов этой проверки.')
    heading('ВЫВОДЫ И ВОСПРОИЗВЕДЕНИЕ')
    results = summary['experiments']
    for left, right, effect in [(0, 1, 'Увеличение ширины'), (1, 2, 'Добавление скрытого слоя'), (2, 3, 'Добавление Dropout')]:
        delta = 100 * (results[right]['best']['val_accuracy'] - results[left]['best']['val_accuracy'])
        para(f'{effect}: изменение лучшей val accuracy составило {delta:+.2f} процентного пункта при данных настройках. Один seed не позволяет утверждать статистическую значимость разницы.')
    para(f"Модель {summary['winner']} выбрана по валидации, а не по тестовым ответам. Сеть и оптимизатор реализованы вручную, сохранение весов позволяет воспроизвести инференс без обучения.")
    if drawings:
        para(f'На собственных рисунках верно распознаны {correct} из {len(drawings)}. Практическое условие задания выполнено. Ошибки на тонких штрихах показывают, что результат MNIST нельзя напрямую переносить на любой внешний рисунок; предобработка существенно влияет на вход сети.')
    else:
        para('Для оценки собственных рисунков необходима отдельная практическая проверка предобработки.')
    para('Запуск: setup.ps1; run.ps1 -Mode Check; run.ps1 -Mode Train; run.ps1 -Mode Notebook. Для рисунков: run.ps1 -Mode Drawings; затем run.ps1 -Mode Report. Файлы data, output/best_model.npz и пакет mnist_lab нужны для автономного воспроизведения.')
    para('Источники: задание «ЛР6 Нейронная сеть MNIST», разделы 1–6; оригинальные IDX-файлы MNIST, зеркало https://storage.googleapis.com/cvdf-datasets/mnist/.', 'Caption')
    for filename in ['layers.py', 'model.py', 'training.py']:
        heading('ПРИЛОЖЕНИЕ КОД ' + filename.upper())
        for line in (ROOT / 'mnist_lab' / filename).read_text(encoding='utf-8').splitlines():
            para(line, 'Code')
    authored = qa / 'authored.docx'
    doc.save(authored)
    editable = {'word/document.xml', 'word/_rels/document.xml.rels', 'word/styles.xml', '[Content_Types].xml'}
    with ZipFile(template) as source, ZipFile(authored) as draft, ZipFile(final, 'w', ZIP_DEFLATED) as dest:
        for name in source.namelist():
            dest.writestr(name, draft.read(name) if name in editable else source.read(name))
        for name in draft.namelist():
            if name not in source.namelist(): dest.writestr(name, draft.read(name))
    with ZipFile(template) as source, ZipFile(final) as dest:
        a = etree.fromstring(source.read('word/document.xml')).find(qn('w:body'))
        b = etree.fromstring(dest.read('word/document.xml')).find(qn('w:body'))
        for node in b[9].iter(qn('w:t')): node.text = node.text.replace('6', '1')
        canonical = lambda e: etree.tostring(e, method='c14n')
        assert all(canonical(a[i]) == canonical(b[i]) for i in range(26))
        assert canonical(a[-1]) == canonical(b[-1])
    (qa / 'report_verification.json').write_text(json.dumps(dict(cover_unchanged_except_number=True,
         section_geometry_unchanged=True, own_drawings=len(drawings), complete=complete), indent=2), encoding='utf-8')
    print(final)


if __name__ == '__main__':
    build()
