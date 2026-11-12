"""Отчёт по сохранённому эксперименту; обложка из ЛР1 меняет только номер."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from lxml import etree

ROOT = Path(__file__).resolve().parent
OUT, QA = ROOT / "output", ROOT / "_qa"
REFERENCE = ROOT.parent / "lab1" / "Лабораторная_работа_1.docx"
FINAL = ROOT / "Лабораторная_работа_5_оформление.docx"
REFERENCE_SHA = "23c5e5c9992df2a8562d78125a77faa19c6c7c964565f74f6bb52cecce3a2439"


def create_report():
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == REFERENCE_SHA
    assert summary["seed"] == 42 and summary["tree"] == {"depth": 5, "leaves": 31, "nodes": 48}
    assert summary["dataset_sha256"] == "d5905d231bedd7e4cdcf708fab55fc65b79dfe12012e846eccad3e88b5ecb019"
    assert summary["selected_features"] == ["class_attendance", "parental_status", "reading_scientific", "high_school_type", "course_id"]
    doc = Document(REFERENCE)
    body = doc._element.body
    for child in list(body)[26:-1]:
        body.remove(child)
    for node in body[9].iter(qn("w:t")):
        node.text = node.text.replace("1", "5")
    for role, size in (("Body", 12), ("Heading", 12), ("Caption", 10), ("Code", 8)):
        style = doc.styles.add_style("Lab5 " + role, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles["Normal"]
        style.font.name = "Consolas" if role == "Code" else "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = role == "Heading"
        style.font.italic = role in ("Heading", "Caption")
        style.font.color.rgb = RGBColor(0, 0, 0)
        pf = style.paragraph_format
        pf.space_before, pf.space_after = Pt(0), Pt(5 if role == "Body" else 3)
        pf.line_spacing = 1.15 if role == "Body" else 1.0
        pf.first_line_indent = Inches(0.5) if role == "Body" else Cm(0)
        pf.widow_control = role != "Code"
        if role == "Code":
            pf.space_after = Pt(0)

    def para(text, role="Body"):
        p = doc.add_paragraph(text.replace(";", ",").replace("；", "，"), style="Lab5 " + role)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if role == "Body" else WD_ALIGN_PARAGRAPH.LEFT
        return p

    def heading(text, page=True):
        p = para(text, "Heading")
        p.paragraph_format.page_break_before = page
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(8)

    def equation(text):
        def run(value):
            r = OxmlElement("m:r")
            t = OxmlElement("m:t")
            t.text = value
            r.append(t)
            return r

        def group(tag, *items):
            e = OxmlElement("m:" + tag)
            for item in items:
                e.append(run(item) if isinstance(item, str) else item)
            return e

        def frac(a, b):
            return group("f", group("num", a), group("den", b))

        def sub(a, b):
            return group("sSub", group("e", a), group("sub", b))

        def summation(index, *items):
            pr = OxmlElement("m:naryPr")
            char = OxmlElement("m:chr")
            char.set(qn("m:val"), "∑")
            pr.append(char)
            hide = OxmlElement("m:supHide")
            hide.set(qn("m:val"), "1")
            pr.append(hide)
            return group("nary", pr, group("sub", index), group("sup"), group("e", *items))

        if text.startswith("H(S)"):
            parts = ["H(S) = −", summation("c", sub("p", "c"), sub("log", "2"), sub("p", "c")), "    0 log₂ 0 = 0"]
        elif text.startswith("IG(S"):
            parts = ["IG(S, A) = H(S) − ", summation("v", frac("|Sᵥ|", "|S|"), " H(Sᵥ)")]
        elif text.startswith("p₁"):
            parts = [sub("p", "1"), " = ", frac(sub("n", "1"), "n"), "    ŷ(t) = 1[p₁ ≥ t]"]
        elif text.startswith("Accuracy"):
            parts = ["Accuracy = ", frac("TP + TN", "N"), "    Precision = ", frac("TP", "TP + FP")]
        elif text.startswith("Recall"):
            parts = ["Recall = TPR = ", frac("TP", "TP + FN"), "    FPR = ", frac("FP", "FP + TN")]
        elif text.startswith("AUC"):
            parts = ["AUC = ", summation("i", "(xᵢ₊₁ − xᵢ)", frac("yᵢ₊₁ + yᵢ", "2"))]
        else:
            parts = ["Importance(A) = ", summation("u", "1[Aᵤ = A] IG(Sᵤ, A)")]
        p = para("")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p._p.append(group("oMathPara", group("oMath", *parts)))

    def table(headers, rows, widths, size=10):
        t = doc.add_table(rows=1, cols=len(headers))
        t.autofit = False
        for col, width in zip(t.columns, widths):
            col.width = Cm(width)
        for i, values in enumerate([headers] + list(rows)):
            cells = t.rows[0].cells if i == 0 else t.add_row().cells
            trpr = t.rows[i]._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if i == 0:
                trpr.append(OxmlElement("w:tblHeader"))
            for j, (cell, value, width) in enumerate(zip(cells, values, widths)):
                cell.width = Cm(width)
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tcpr = cell._tc.get_or_add_tcPr()
                margins = OxmlElement("w:tcMar")
                for edge in ("top", "bottom", "left", "right"):
                    e = OxmlElement("w:" + edge)
                    e.set(qn("w:w"), "70")
                    e.set(qn("w:type"), "dxa")
                    margins.append(e)
                tcpr.append(margins)
                borders = OxmlElement("w:tcBorders")
                for edge in ("top", "bottom", "left", "right"):
                    e = OxmlElement("w:" + edge)
                    for attr, val in (("val", "single"), ("sz", "4"), ("color", "D9D9D9")):
                        e.set(qn("w:" + attr), val)
                    borders.append(e)
                tcpr.append(borders)
                shade = OxmlElement("w:shd")
                shade.set(qn("w:fill"), "D9E2F3" if i == 0 else "F7F9FC" if i % 2 == 0 else "FFFFFF")
                tcpr.append(shade)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(str(value))
                r.font.name, r.font.size = "Times New Roman", Pt(size)
                r.font.bold, r.font.color.rgb = i == 0, RGBColor(0, 0, 0)
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 0.4
        p.add_run().font.size = Pt(2)

    def picture(name, caption, width=16.8):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(OUT / "figures" / f"{name}.png"), width=Cm(width))
        para(caption, "Caption").alignment = WD_ALIGN_PARAGRAPH.CENTER

    heading("ЦЕЛЬ РАБОТЫ И ТЕОРЕТИЧЕСКИЕ СВЕДЕНИЯ")
    para("Лабораторная работа 5. Деревья решений. Вариант нечётный. Цель: самостоятельно реализовать многоветвевое дерево ID3 для бинарной классификации категориальных данных, оценить качество и переобучение, построить ROC- и PR-кривые и вычислить AUC методом трапеций.")
    para("В узле выбирается один из оставшихся признаков с максимальным информационным выигрышем. Для каждой категории создаётся своя ветвь. Энтропия измеряет неопределённость класса: для чистого узла она равна нулю, при равных долях двух классов достигает одного бита.")
    equation("H(S) = −Σс pс log₂ pс,   0 log₂ 0 = 0.")
    equation("IG(S, A) = H(S) − Σᵥ (|Sᵥ| / |S|) H(Sᵥ).")
    para("Рекурсия останавливается при чистом узле, отсутствии оставшихся признаков или неположительном максимальном IG. В вычислениях выигрыш не более 10⁻¹² считается нулём. При равных выигрышах сохраняется порядок признаков после случайного отбора. Один признак используется не более одного раза на каждом пути.")
    para("Каждый узел хранит число обучающих объектов n и долю p₁ объектов класса 1. Прогноз вероятности равен p₁ в достигнутом листе. Если категории нет среди ветвей, используется p₁ текущего узла. Класс равен 1 при p₁ ≥ t, иначе 0; основной порог t = 0,5.")
    equation("p₁ = n₁ / n;   ŷ(t) = 1[p₁ ≥ t].")
    equation("Accuracy = (TP + TN) / N;   Precision = TP / (TP + FP);")
    equation("Recall = TPR = TP / (TP + FN);   FPR = FP / (FP + TN).")
    para("TP и TN — верные положительные и отрицательные прогнозы, FP и FN — ложноположительные и ложноотрицательные. При H₀: y=0 ошибки FP относятся к I роду, FN — ко II. При нулевом знаменателе precision или recall в таблицах принимается равным нулю.")
    para("ROC строится по FPR и TPR, PR — по recall и precision. Для площади координаты стабильно сортируются по x, затем суммируются площади трапеций. На ROC присутствуют точки (0; 0), (1; 1) и диагональ случайного классификатора.")
    equation("AUC = Σᵢ (xᵢ₊₁ − xᵢ)(yᵢ₊₁ + yᵢ) / 2.")
    para("Алгоритм дерева, метрики, перебор порогов и интегрирование реализованы самостоятельно. NumPy используется для вычислений, Pandas — для таблиц, Matplotlib — для графиков; из sklearn вызывается только разрешённая функция train_test_split.")

    heading("ПОДГОТОВКА ДАННЫХ")
    para("Использован Higher Education Students Performance Evaluation, UCI № 856 [1]. Исходный CSV содержит 145 строк, ID студента, 31 предиктор и GRADE. Цель y = 1 при GRADE ≥ 3, иначе y = 0. GRADE и STUDENT ID исключены из признаков до отбора. COURSE ID — код курса, а не идентификатор студента; он остаётся допустимым категориальным предиктором.")
    para("Пропусков и полных дубликатов строк в исходном файле нет. Для потенциальных пропусков предусмотрена отдельная категория <MISSING>, включая символ ? и пустые строки. Строки не удаляются. Все коды трактуются как категории: нормализация, one-hot-кодирование и числовые пороги не применяются.")
    table(["Выборка", "Класс 0", "Класс 1", "Всего"],
          [["Все данные", 67, 78, 145], ["Train", 54, 62, 116], ["Test", 13, 16, 29]], [5.4, 3.8, 3.8, 3.8])
    para("Разбиение train/test = 80/20 выполнено с stratify=y и random_state=42. Доля класса 1: 53,79 % в полном наборе, 53,45 % в train и 55,17 % в test. Небольшое отличие обусловлено целым числом объектов. Индексы строк сохранены в split.csv.")
    para("Из n = 31 признака один раз до построения дерева выбраны floor(√31) = 5. Использован отдельный генератор NumPy default_rng(42), choice без возвращения. Повторный отбор в узлах не выполняется. Названия в коде сопоставлены исходным столбцам:")
    table(["Столбец CSV", "Имя в программе", "Смысл и категории"], [
        ["22", "class_attendance", "Посещение занятий: 1 всегда, 2 иногда, 3 никогда"],
        ["14", "parental_status", "Статус родителей: 1 в браке, 2 разведены, 3 умер один или оба"],
        ["19", "reading_scientific", "Чтение научных книг/журналов: 1 нет, 2 иногда, 3 часто"],
        ["3", "high_school_type", "Школа: 1 частная, 2 государственная, 3 другая"],
        ["COURSE ID", "course_id", "Категориальный код курса, наблюдаются значения 1–9"],
    ], [2.4, 5.1, 9.3], 10)
    para("В данных встречаются только категории посещения 1 и 2; категория 3 указана в описании UCI. Ни качество на test, ни значения GRADE не используются для выбора пяти признаков. Тест служит оценке уже построенной модели; пороги ниже исследуются описательно, без подбора лучшего порога по тесту.")

    heading("СТРУКТУРА ПОСТРОЕННОГО ДЕРЕВА")
    para("Корень имеет глубину 0. Полная глубина равна 5, число листьев — 31, число всех узлов — 48. Внутренние узлы используют все пять отобранных признаков. Ниже показана структура до глубины 3; полный вывод из 48 строк сохранён в output/tree.txt. n — размер узла, p1 — доля класса 1, IG — выигрыш выбранного разбиения.")
    # Branch guides show the hierarchy, tabs align node statistics.
    lines = (OUT / "tree_preview.txt").read_text(encoding="utf-8").splitlines()
    header = para("Узел и ветвь\tn\tp₁\tIG", "Code")
    for stop in (11.4, 12.5, 14.5):
        header.paragraph_format.tab_stops.add_tab_stop(Cm(stop))
    header.runs[0].bold = True
    for i, line in enumerate(lines):
        depth = (len(line) - len(line.lstrip())) // 2
        content = line.strip()
        prefix = "│  " * max(0, depth - 1) + ("└─ " if depth else "")
        if "subtree omitted" in content:
            content = prefix + "⋯ продолжение поддерева"
        else:
            label, n, probability, gain = content.split("; ")
            label = label.replace(" -> ", " → ").replace("LEAF", "Лист")
            content = prefix + label + "\t" + n[2:] + "\t" + probability[3:] + "\t" + gain[3:]
        p = para(content, "Code")
        for stop in (11.4, 12.5, 14.5):
            p.paragraph_format.tab_stops.add_tab_stop(Cm(stop))
        p.paragraph_format.line_spacing = Pt(10)
        p.paragraph_format.space_after = Pt(1)
        p.runs[0].font.size = Pt(8)
    
    para("В корне выбран course_id с IG = 0,421771. Например, course_id=3 ведёт в чистый лист класса 1, а course_id=8 — в чистый лист класса 0. В ветвях курсов 1 и 9 требуются дополнительные признаки. Чистые листья на малом числе объектов не гарантируют безошибочности на новых данных.")
    para("Из 31 листа девять остаются смешанными и содержат 49 обучающих объектов. После исчерпания признаков или нулевого выигрыша разделить их дальше нельзя по правилам задания; поэтому обучающая accuracy не обязана достигать 1 даже без отсечения ветвей.")

    heading("ВАЖНОСТЬ ПРИЗНАКОВ И КАЧЕСТВО")
    equation("Importance(A) = Σᵤ I[признак узла u = A] · IG(Sᵤ, A).")
    para("По условию суммируются локальные IG без веса |Sᵤ|/|Sroot| и без нормировки. Поэтому это не стандартная взвешенная MDI-важность: сумма учитывает и небольшие глубокие узлы.")
    picture("feature_importance", "Рисунок 1. Суммарный IG по всем узлам, где использован признак.", width=14.5)
    importance = pd.read_csv(OUT / "feature_importance.csv")
    table(["Признак", "Сумма IG, бит"], [[r.feature, f"{r.sum_IG:.6f}"] for _, r in importance.iterrows()], [11.4, 5.4])
    para("Наибольшая суммарная важность у reading_scientific, затем parental_status и high_school_type. Course_id выбран в корне и даёт самое сильное начальное разбиение, но его единственный IG меньше сумм повторно используемых признаков. Важность не доказывает причинной связи с успеваемостью; IG склонен отдавать предпочтение многозначным признакам.")
    table(["Выборка", "Accuracy", "Precision", "Recall", "TP", "FP", "FN", "TN"],
          [[r["split"], f"{r['accuracy']:.4f}", f"{r['precision']:.4f}", f"{r['recall']:.4f}", r["TP"], r["FP"], r["FN"], r["TN"]] for r in summary["metrics"]],
          [3.2, 2.8, 2.8, 2.8, 1.3, 1.3, 1.3, 1.3], 10)
    para("Основной порог 0,5. На тесте верны 22 прогноза из 29. Ложноотрицательных ошибок больше: FN = 5 против FP = 2. Пять студентов с GRADE ≥ 3 ошибочно отнесены к классу 0, два студента с GRADE < 3 — к классу 1.")

    heading("ROC И PR КРИВЫЕ")
    picture("roc_pr", "Рисунок 2. ROC и PR на тестовой выборке, площади вычислены трапециями.")
    a = summary["test_auc"]
    para(f"ROC AUC = {a['ROC_AUC']:.6f}; PR AUC = {a['PR_AUC']:.6f}. PR AUC здесь означает площадь под ломаной методом трапеций, а не average precision. Доля положительного класса в test равна 16/29 ≈ 0,5517; на PR она показана горизонтальной справочной линией.")
    para("Пороги взяты из уникальных долей класса 1 в листьях плюс 0 и 1. Код дополнительно учитывает оценки отката в текущий узел, если они встретились при предсказании. В этом тесте новых оценок не возникло. При t=0,5 и t=1 прогнозы одинаковы: в тесте нет вероятности 0,5 или между 0,5 и 1.")
    curve = pd.read_csv(OUT / "threshold_curves.csv")
    rows = []
    for _, r in curve.iterrows():
        rows.append(["+∞" if r.threshold == float("inf") else f"{r.threshold:.4f}",
                     int(r.TP), int(r.FP), int(r.FN), int(r.TN), f"{r.precision:.4f}", f"{r.recall:.4f}", f"{r.FPR:.4f}"])
    table(["Порог", "TP", "FP", "FN", "TN", "Precision", "Recall", "FPR"], rows,
          [2.4, 1.2, 1.2, 1.2, 1.2, 3.2, 3.2, 3.2], 10)
    para("Технический порог +∞ добавляет точку ROC (0; 0), поскольку при правиле p ≥ t порог 1 ещё оставляет положительные прогнозы с p=1. Порог 0 даёт ROC (1; 1). Для PR при отсутствии положительных прогнозов задаётся опорная precision=1 и recall=0; в обычной таблице метрик precision остаётся 0. Эта конвенция явно отделена в столбце curve_precision файла threshold_curves.csv.")

    heading("ВЛИЯНИЕ ПОРОГА И ВЫВОДЫ")
    picture("threshold_effect", "Рисунок 3. Precision и recall при изменении порога на тесте.")
    para("При снижении t с 0,5 до 0,4 recall растёт с 0,6875 до 0,8125, FN уменьшается с 5 до 3; одновременно FP увеличивается с 2 до 5, precision падает с 0,8462 до 0,7222. При t=0 все объекты положительные: FN=0, FP=13, recall=1, precision=0,5517.")
    para("При повышении порога число положительных прогнозов не растёт: TP и FP не увеличиваются, FN не уменьшается, поэтому recall не возрастает. Precision часто повышается, но строгой монотонности нет: переход от t=0,4 к t≈0,4706 уменьшает её с 0,7222 до 0,7059, так как исключается верный положительный прогноз.")
    para("Accuracy train = 0,8362, test = 0,7586: разрыв 7,76 процентного пункта. Precision падает с 0,9388 до 0,8462, recall — с 0,7419 до 0,6875. Это признаки ухудшения обобщения и возможного переобучения. Однако тест содержит лишь 29 объектов: один объект меняет accuracy на 3,45 п.п.; по одному разбиению нельзя надёжно оценить устойчивость разрыва. Прунинг и дополнительная настройка в основной эксперимент не вводились.")
    para("Реализовано многоветвевое ID3 с требуемыми остановами и откатом вероятности при неизвестной категории. Главные признаки по заданной сумме IG — научное чтение, статус родителей и тип школы; самое сильное корневое разбиение даёт код курса. На тесте ложных отрицаний больше, чем ложных подтверждений. Снижение порога уменьшает пропуски класса 1 ценой увеличения FP. Итоговые метрики относятся к фиксированным пяти признакам и одному разбиению.")
    para("Воспроизведение: python experiment.py; python -m unittest -v test_decision_tree.py. Данные — data/students.csv, результаты — output, зависимости — requirements.txt. Девять проверок алгоритма и метрик пройдены.")
    para("Источники: [1] Yilmaz N., Şekeroğlu B. Higher Education Students Performance Evaluation. UCI, DOI 10.24432/C51G82, https://archive.ics.uci.edu/dataset/856. [2] Задание «ЛР5 Деревья решений», разделы 2–5.", "Caption")

    source = (ROOT / "decision_tree.py").read_text(encoding="utf-8").splitlines()
    cut = next(i for i, line in enumerate(source) if line.startswith("    def predict_proba"))
    for title, lines in (("РЕАЛИЗАЦИЯ ДЕРЕВА ПОСТРОЕНИЕ", source[:cut]),
                         ("РЕАЛИЗАЦИЯ ДЕРЕВА ПРЕДСКАЗАНИЕ И ВЫВОД", source[cut:]),
                         ("РЕАЛИЗАЦИЯ МЕТРИК И КРИВЫХ", (ROOT / "metrics.py").read_text(encoding="utf-8").splitlines())):
        heading(title)
        for line in lines:
            para(line, "Code")

    QA.mkdir(exist_ok=True)
    authored = QA / "authored.docx"
    doc.save(authored)
    editable = {"word/document.xml", "word/_rels/document.xml.rels", "word/styles.xml", "[Content_Types].xml"}
    with ZipFile(REFERENCE) as source_zip, ZipFile(authored) as draft, ZipFile(FINAL, "w", ZIP_DEFLATED) as result:
        for name in source_zip.namelist():
            result.writestr(name, draft.read(name) if name in editable else source_zip.read(name))
        for name in draft.namelist():
            if name not in source_zip.namelist():
                result.writestr(name, draft.read(name))
    with ZipFile(REFERENCE) as old, ZipFile(FINAL) as new:
        preserved = [name for name in old.namelist() if name not in editable]
        assert all(old.read(name) == new.read(name) for name in preserved)
        a = etree.fromstring(old.read("word/document.xml")).find(qn("w:body"))
        b = etree.fromstring(new.read("word/document.xml")).find(qn("w:body"))
        for node in b[9].iter(qn("w:t")):
            node.text = node.text.replace("5", "1")
        canonical = lambda e: etree.tostring(e, method="c14n")
        assert all(canonical(a[i]) == canonical(b[i]) for i in range(26))
        assert canonical(a[-1]) == canonical(b[-1])
        for part in ("word/styles.xml", "word/_rels/document.xml.rels"):
            src, dst = etree.fromstring(old.read(part)), etree.fromstring(new.read(part))
            assert all(any(canonical(s) == canonical(t) for t in dst) for s in src)
        inventory = {name: hashlib.sha256(old.read(name)).hexdigest() for name in old.namelist()}
    assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == REFERENCE_SHA
    (QA / "verification.json").write_text(json.dumps({
        "reference_sha256": REFERENCE_SHA, "cover_unchanged_except_lab_number": True,
        "section_geometry_unchanged": True, "original_styles_and_relationships_preserved": True,
        "preserved_parts": preserved, "reference_part_sha256": inventory,
        "control_questions_in_report": False}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(FINAL)


if __name__ == "__main__":
    create_report()
