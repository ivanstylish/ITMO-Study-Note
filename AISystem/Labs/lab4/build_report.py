"""从实验结果生成俄文报告，保留实验一封面，只修改实验号。"""
from pathlib import Path
import ast
import hashlib
import json
from zipfile import ZipFile, ZIP_DEFLATED
import pandas as pd
from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from lxml import etree

ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT.parent / "lab1" / "Лабораторная_работа_1.docx"
FINAL = ROOT / "Лабораторная_работа_4.docx"
QA, OUT = ROOT / "_qa", ROOT / "output"
NAMES = {"euclidean": "Евклидово", "manhattan": "Манхэттенское", "chebyshev": "Чебышёва"}
CODE_RU = {
    "手写 kNN：fit 保存训练数据，predict 查找邻居并投票或求平均。":
        "kNN: fit сохраняет данные, predict находит соседей и формирует ответ.",
    "k 必须是正整数。": "k должен быть положительным целым.",
    "task 必须是 classification 或 regression。": "task: classification или regression.",
    "不支持的距离度量。": "Неизвестная метрика расстояния.",
    "x 应为二维特征矩阵，y 应为等长的一维数值标签。":
        "x: матрица признаков; y: числовой вектор той же длины.",
    "样本数不能小于 k，数据不能包含缺失值或无穷大。":
        "Нужно не менее k объектов и только конечные значения.",
    "请先调用 fit。": "Сначала вызовите fit.",
    "预测特征的维数必须与训练数据一致，且所有值有限。":
        "Нужны те же признаки, что в train, и конечные значения.",
    "等距邻居按训练数据顺序选择，保证第 k 个邻居处也可复现。":
        "При равных расстояниях сохраняем порядок train, включая границу k.",
    "先比票数，再比本类邻居距离总和，最后选较小标签。":
        "Сначала число голосов, затем сумма расстояний и меньшая метка.",
    "手写分类和回归指标，不使用 sklearn.metrics。":
        "Собственные метрики классификации и регрессии без sklearn.metrics.",
    "实际值和预测值应为非空、等长的一维数组。":
        "Нужны непустые одномерные массивы одинаковой длины.",
    "指标输入不能包含缺失值或无穷大。": "Значения должны быть конечными.",
    "类别标签必须是一维且不重复。": "Метки: одномерный массив без повторов.",
    "类别列表必须包含所有实际标签和预测标签。":
        "Список классов должен содержать все истинные и предсказанные метки.",
    "某类没有预测样本或真实样本时，相应指标取 0。":
        "При нулевом знаменателе метрика класса равна 0.",
}


def math_node(tag, *parts):
    node = OxmlElement("m:" + tag)
    for part in parts:
        if isinstance(part, str):
            run, text = OxmlElement("m:r"), OxmlElement("m:t")
            text.text = part
            text.set(qn("xml:space"), "preserve")
            run.append(text)
            node.append(run)
        else:
            node.append(part)
    return node


def sub(base, index):
    return math_node("sSub", math_node("e", base), math_node("sub", index))


def square(*parts):
    return math_node("sSup", math_node("e", *parts), math_node("sup", "2"))


def fraction(top, bottom):
    return math_node("f", math_node("num", *top), math_node("den", *bottom))


def summation(index, *parts, upper=None):
    props = OxmlElement("m:naryPr")
    for tag, value in [("chr", "∑"), ("limLoc", "subSup"), ("supHide", "1" if upper is None else "0")]:
        child = OxmlElement("m:" + tag)
        child.set(qn("m:val"), value)
        props.append(child)
    return math_node("nary", props, math_node("sub", index),
                     math_node("sup", upper or ""), math_node("e", *parts))


def root(*parts):
    props, hidden = OxmlElement("m:radPr"), OxmlElement("m:degHide")
    hidden.set(qn("m:val"), "1")
    props.append(hidden)
    return math_node("rad", props, math_node("deg"), math_node("e", *parts))


def create_report():
    summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    wine, diabetes = (summary["datasets"][name] for name in ("wine", "diabetes"))
    # Аналитические выводы ниже относятся к зафиксированному протоколу.
    assert summary["seed"] == 42 and summary["k_values"] == [3, 5, 10, 15]
    assert (wine["best_validation"]["k"], wine["best_validation"]["distance"]) == (15, "euclidean")
    assert (diabetes["best_validation"]["k"], diabetes["best_validation"]["distance"]) == (15, "chebyshev")
    doc = Document(REFERENCE)
    body = doc._element.body
    for child in list(body)[26:-1]:
        body.remove(child)
    for node in body[9].iter(qn("w:t")):
        node.text = node.text.replace("1", "4")
    for role, size in [("Body", 12), ("Heading", 12), ("Caption", 10), ("Code", 8)]:
        style = doc.styles.add_style("Lab4 " + role, WD_STYLE_TYPE.PARAGRAPH)
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
        pf.widow_control = True
        if role == "Code":
            style.element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")

    def para(text, role="Body"):
        p = doc.add_paragraph(text, style="Lab4 " + role)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if role == "Body" else WD_ALIGN_PARAGRAPH.LEFT
        return p

    bookmark_id = 1000

    def heading(text, page=True):
        nonlocal bookmark_id
        p = para(text, "Heading")
        p.paragraph_format.page_break_before = page
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(8)
        level = OxmlElement("w:outlineLvl")
        level.set(qn("w:val"), "0")
        p._p.get_or_add_pPr().append(level)
        start, end = OxmlElement("w:bookmarkStart"), OxmlElement("w:bookmarkEnd")
        start.set(qn("w:id"), str(bookmark_id))
        start.set(qn("w:name"), "lab4_section_" + str(bookmark_id - 999))
        end.set(qn("w:id"), str(bookmark_id))
        p._p.insert(1, start)
        p._p.append(end)
        bookmark_id += 1

    def equation(*parts):
        p = para("", "Body")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p._p.append(math_node("oMathPara", math_node("oMath", *parts)))

    def table(headers, rows, widths, size=9):
        t = doc.add_table(rows=1, cols=len(headers))
        t.autofit = False
        for column, width in zip(t.columns, widths):
            column.width = Cm(width)
        for i, values in enumerate([headers] + list(rows)):
            cells = t.rows[0].cells if i == 0 else t.add_row().cells
            trpr = t.rows[i]._tr.get_or_add_trPr()
            trpr.append(OxmlElement("w:cantSplit"))
            if i == 0:
                trpr.append(OxmlElement("w:tblHeader"))
            for j, (cell, value, width) in enumerate(zip(cells, values, widths)):
                cell.width = Cm(width)
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(str(value))
                r.font.name, r.font.size = "Times New Roman", Pt(size)
                r.font.bold = i == 0
                tcpr = cell._tc.get_or_add_tcPr()
                borders = OxmlElement("w:tcBorders")
                for edge in ("top", "bottom", "left", "right"):
                    tag = OxmlElement("w:" + edge)
                    for attr, val in (("val", "single"), ("sz", "4"), ("color", "BFBFBF")):
                        tag.set(qn("w:" + attr), val)
                    borders.append(tag)
                tcpr.append(borders)
                if i == 0:
                    shade = OxmlElement("w:shd")
                    shade.set(qn("w:fill"), "E7E6E6")
                    tcpr.append(shade)
        doc.add_paragraph().paragraph_format.space_after = Pt(0)

    def picture(name, caption, width=16.8):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(OUT / "figures" / (name + ".png")), width=Cm(width))
        p = para(caption, "Caption")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p = para("Содержание", "Heading")
    p.paragraph_format.page_break_before = True
    sections = ["ЦЕЛЬ РАБОТЫ И ТЕОРИЯ", "ОПИСАТЕЛЬНАЯ СТАТИСТИКА WINE",
                "ОПИСАТЕЛЬНАЯ СТАТИСТИКА DIABETES", "РАЗБИЕНИЕ И ПРЕДОБРАБОТКА",
                "ВАЛИДАЦИЯ: КЛАССИФИКАЦИЯ", "ВАЛИДАЦИЯ: РЕГРЕССИЯ",
                "ТЕСТ: КЛАССИФИКАЦИЯ", "ТЕСТ: РЕГРЕССИЯ", "РЕАЛИЗАЦИЯ КЛАССА KNN",
                "САМОСТОЯТЕЛЬНЫЕ МЕТРИКИ", "ВЫВОДЫ"]
    for page, title in enumerate(sections, 3):
        p = para("", "Caption")
        anchor = "lab4_section_" + str(page - 2)
        link = OxmlElement("w:hyperlink")
        link.set(qn("w:anchor"), anchor)
        run, text = OxmlElement("w:r"), OxmlElement("w:t")
        text.text = title
        run.append(text)
        link.append(run)
        run = OxmlElement("w:r")
        run.append(OxmlElement("w:tab"))
        link.append(run)
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), f" PAGEREF {anchor} \\h ")
        run, text = OxmlElement("w:r"), OxmlElement("w:t")
        text.text = str(page)
        run.append(text)
        field.append(run)
        link.append(field)
        p._p.append(link)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
        p.paragraph_format.space_after = Pt(10)
    update = doc.settings.element.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        doc.settings.element.append(update)
    update.set(qn("w:val"), "true")

    heading(sections[0])
    para("Лабораторная работа № 4. Метод k-ближайших соседей (kNN). Цель: самостоятельно реализовать классификацию и регрессию, исследовать влияние числа соседей и расстояния и проверить качество при разбиении без утечки данных.")
    para("kNN является непараметрическим ленивым методом: fit сохраняет обучающие объекты, а predict вычисляет расстояния до них. Для классификации используется большинство голосов k соседей, для регрессии - среднее их целевых значений.")
    equation(sub("d", "2"), "(x,u) = ", root(summation("j=1", square("(", sub("x", "j"), "−", sub("u", "j"), ")"), upper="d")),
             ";  ", sub("d", "1"), "(x,u) = ", summation("j=1", "|", sub("x", "j"), "−", sub("u", "j"), "|", upper="d"))
    equation(sub("d", "∞"), "(x,u) = ", sub("max", "j"), "|", sub("x", "j"), "−", sub("u", "j"), "|;  ",
             sub("ŷ", "регр"), " = ", fraction(["1"], ["k"]), summation("i∈Nₖ(x)", sub("y", "i")))
    para("При равенстве голосов выбирается класс с меньшей суммой расстояний до его соседей. Если равны и суммы, выбирается меньшая числовая метка. Равные расстояния при отборе k соседей разрешаются исходным порядком объектов train (стабильная сортировка).")
    equation("accuracy = ", fraction([summation("c", sub("TP", "c"))], ["N"]), ";  ",
             sub("P", "c"), " = ", fraction([sub("TP", "c")], [sub("TP", "c"), "+", sub("FP", "c")]))
    equation(sub("R", "c"), " = ", fraction([sub("TP", "c")], [sub("TP", "c"), "+", sub("FN", "c")]), ";  ",
             sub("F1", "c"), " = ", fraction(["2", sub("P", "c"), sub("R", "c")], [sub("P", "c"), "+", sub("R", "c")]))
    para("Macro precision, recall и F1 - среднее соответствующих показателей по классам. Сначала вычисляется F1 каждого класса, затем берётся среднее; F1 не вычисляется из уже усреднённых precision и recall. При нулевом знаменателе показатель класса принят равным нулю.")
    equation("MAE = ", fraction(["1"], ["N"]), summation("i=1", "|", sub("y", "i"), "−", sub("ŷ", "i"), "|", upper="N"),
             ";  MSE = ", fraction(["1"], ["N"]), summation("i=1", square("(", sub("y", "i"), "−", sub("ŷ", "i"), ")"), upper="N"))
    equation(square("R"), " = 1 − ", fraction(
        [summation("i=1", square("(", sub("y", "i"), "−", sub("ŷ", "i"), ")"), upper="N")],
        [summation("i=1", square("(", sub("y", "i"), "−ȳ)"), upper="N")]))
    para("В R² среднее ȳ относится к оцениваемому набору. Для постоянного y знаменатель равен нулю: реализация возвращает NaN. В Wine и Diabetes этой ситуации нет. Масштабирование необходимо, так как признаки с большим численным разбросом иначе доминируют в расстоянии.")

    short_wine = ["alcohol", "malic_acid", "ash", "alcalinity", "magnesium", "total_phenols",
                  "flavanoids", "nonflav. phenols", "proanthocyanins", "color_intensity", "hue", "OD280/OD315", "proline"]
    for name, title, short in [("wine", sections[1], short_wine), ("diabetes", sections[2], None)]:
        heading(title)
        if name == "wine":
            para("Источник: sklearn.datasets.load_wine(). 178 объектов, 13 числовых химических признаков, три класса вина: 59, 71 и 48 объектов. Пропусков и полных дубликатов нет. Классы обозначены 0, 1 и 2; их номера не задают порядок качества вина.")
        else:
            para("Источник: sklearn.datasets.load_diabetes(scaled=False). 442 пациента, 10 исходных числовых признаков; цель - количественный показатель прогрессирования заболевания через год. Пропусков и полных дубликатов нет. age - возраст, sex - код пола 1/2, bmi - индекс массы тела, bp - среднее давление, s1–s6 - показатели сыворотки крови.")
        stats = pd.read_csv(OUT / (name + "_statistics.csv"), index_col=0)
        if name == "wine":
            stats = stats.drop(index="target")
        labels = short if short else list(stats.index)
        rows = [[label] + [f"{row[k]:.2f}" for k in ["mean", "std", "min", "25%", "50%", "75%", "max"]]
                for label, (_, row) in zip(labels, stats.iterrows())]
        table(["Признак", "Среднее", "SD", "Мин.", "Q1", "Медиана", "Q3", "Макс."], rows,
              [3.6, 2.0, 1.65, 1.7, 1.65, 1.9, 1.65, 1.85], size=8.5)
        para("Таблица: статистика исходных данных; SD рассчитано с ddof=1. Число наблюдений одинаково для всех признаков. Полные имена и точные значения сохранены в CSV. Описательная статистика всего набора служит только для описания данных и не используется для обучения или выбора параметров.")
        picture(name + "_statistics", "Рисунок " + ("1" if name == "wine" else "2") + ". Масштаб признаков и распределение целевой переменной.")
        if name == "wine":
            para("Разброс proline (SD = 314,91) намного больше, чем у hue (SD = 0,23). Без стандартизации вклад proline в расстояние был бы несоразмерно большим.")
        else:
            para("Вызов scaled=False исключает предварительное масштабирование по всему набору. Код пола уже числовой, дополнительное кодирование не требуется; стандартизация применяется ко всем десяти признакам, цель не масштабируется.")

    heading(sections[3])
    para("Зафиксирован random_state = 42. Сначала 40 % объектов выделяются во временный набор, затем он делится пополам на validation и test. Для Wine оба разбиения стратифицированы. Из-за округления размеров доли близки к 60/20/20.")
    table(["Набор", "Train", "Validation", "Test", "Всего"],
          [["Wine", 106, 36, 36, 178], ["Diabetes", 265, 88, 89, 442]], [4.1, 3, 3.5, 3, 2.4], 11)
    table(["Класс Wine", "Train", "Validation", "Test", "Всего"],
          [[0, 35, 12, 12, 59], [1, 42, 14, 15, 71], [2, 29, 10, 9, 48]], [4.1, 3, 3.5, 3, 2.4], 11)
    equation(sub("z", "j"), " = ", fraction([sub("x", "j"), "−", sub("μ", "train,j")], [sub("σ", "train,j")]), ",  ddof = 0")
    para("Среднее и стандартное отклонение вычисляются исключительно по train, затем неизменно применяются к validation и test. Для постоянного признака делитель заменяется на 1. В этих двух наборах постоянных признаков нет. Удаление строк, заполнение пропусков и преобразование категорий не потребовались.")
    para("Например, для Wine на train: μ(proline) = 755,0283, σ(proline) = 314,3256. Для Diabetes: μ(bmi) = 26,6113, σ(bmi) = 4,4416. Индексы строк каждого набора и все параметры нормировки сохранены в output.")
    para("Для каждой задачи проверены 4 значения k (3, 5, 10, 15) и 3 расстояния, всего 12 конфигураций. Wine: максимизируется macro F1; Diabetes: минимизируется MSE. При равенстве главного показателя выбирается меньшее k, затем расстояние по порядку: евклидово, манхэттенское, Чебышёва.")
    para("После выбора конфигурации модель сохраняет только исходный train; объединения train и validation нет. Для выбранной модели predict вызывается на test один раз. Тест не участвует в подборе параметров. Реализованы собственные KNN, матрица ошибок и метрики; sklearn используется только для загрузки данных и train_test_split.")

    for name, title, number in [("wine", sections[4], 3), ("diabetes", sections[5], 4)]:
        heading(title)
        grid = pd.read_csv(OUT / (name + "_validation.csv"))
        columns = ["accuracy", "precision_macro", "recall_macro", "F1_macro"] if name == "wine" else ["MAE", "MSE", "R2"]
        rows = [[NAMES[r.distance], r.k] + [f"{r[c]:.4f}" for c in columns] for _, r in grid.iterrows()]
        table(["Расстояние", "k"] + (["Accuracy", "P macro", "R macro", "F1 macro"] if name == "wine" else ["MAE", "MSE", "R²"]),
              rows, [4.4, 1.2] + ([2.85] * 4 if name == "wine" else [3.8] * 3), 10)
        picture(name + "_validation", f"Рисунок {number}. Зависимость качества от k для трёх расстояний.")
        if name == "wine":
            para("Лучший результат: k = 15, евклидово расстояние, macro F1 = 0,9743. Для L2 увеличение k улучшает качество, для L∞ качество при k = 15 падает до 0,8347. Усреднение соседей не гарантирует улучшения при любой метрике.")
        else:
            para("Лучший результат по MSE: k = 15, расстояние Чебышёва, MSE = 2915,4694, R² = 0,4943. Различие с k = 10 для этой метрики небольшое: 5,3303 единицы MSE. Минимальная MAE (42,5720) достигается при L2 и k = 3, но параметр выбирается по заранее принятой MSE.")

    heading(sections[6])
    para("Финальная конфигурация Wine: k = 15, евклидово расстояние, обучение на 106 объектах, тест на 36 объектах.")
    table(["Accuracy", "Precision macro", "Recall macro", "F1 macro"],
          [[f"{wine['test_metrics'][k]:.4f}" for k in ["accuracy", "precision_macro", "recall_macro", "F1_macro"]]], [4.2] * 4, 11)
    picture("wine_confusion_matrix", "Рисунок 5. Строки - истинный класс, столбцы - предсказанный.", 13)
    para("Верно классифицированы 35 из 36 объектов. Единственная ошибка: один объект истинного класса 1 отнесён к классу 2. Все 12 объектов класса 0 и все 9 объектов класса 2 распознаны верно. Для класса 2 precision = 9/10, а recall = 9/9.")
    para("Тестовая macro F1 = 0,9710 близка к валидационной 0,9743. При этом тест содержит только 36 объектов: ошибка на одном объекте меняет accuracy на 1/36 ≈ 2,78 процентного пункта. Результат относится к данному фиксированному разбиению.")

    heading(sections[7])
    para("Финальная конфигурация Diabetes: k = 15, расстояние Чебышёва, обучение на 265 объектах, тест на 89 объектах.")
    table(["MAE", "MSE", "R²"], [[f"{diabetes['test_metrics'][k]:.4f}" for k in ["MAE", "MSE", "R2"]]], [5.6] * 3, 11)
    picture("diabetes_predictions", "Рисунок 6. Сопоставление фактических значений и прогнозов на тесте.")
    para("Средняя абсолютная ошибка составляет 46,5213 единицы целевого показателя. R² = 0,4510 означает снижение суммы квадратов ошибок примерно на 45,10 % относительно постоянного прогноза, равного среднему фактических значений теста. Это характеристика качества, а не причинное объяснение заболевания.")
    para("Прогнозы усредняются по соседям: на графике заметно сглаживание крайних значений. MSE теста (3175,5054) выше валидационной MSE (2915,4694); выборка невелика, а усреднение 15 наблюдений ограничивает возможность точно воспроизводить крайние значения.")

    for title, filename in [(sections[8], "knn.py"), (sections[9], "metrics.py")]:
        heading(title)
        para("Полный исходный код. Комментарии поясняют правило выбора соседей и голосования." if filename == "knn.py" else
             "Полный код собственных метрик. Строки матрицы ошибок соответствуют истинным классам, столбцы - предсказанным.")
        listing = (ROOT / filename).read_text(encoding="utf-8")
        for chinese, russian in CODE_RU.items():
            listing = listing.replace(chinese, russian)
        assert not any("\u4e00" <= ch <= "\u9fff" for ch in listing)
        ast.parse(listing)
        for line in listing.splitlines():
            p = para(line, "Code")
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.widow_control = False

    heading(sections[10])
    para("Реализованы классификация и регрессия kNN, три расстояния и собственные метрики. Проверены все 24 конфигурации. Wine лучше классифицируется при k = 15 и L2 (тестовая accuracy 0,9722), Diabetes лучше по валидационной MSE при k = 15 и L∞ (тестовое R² 0,4510). Единой лучшей метрики для обеих задач не найдено.")
    para("Большое k снижает чувствительность к отдельным наблюдениям, но может смешивать классы или чрезмерно сглаживать регрессию. На Wine расстояние L∞ ухудшает качество при росте k; на Diabetes оно даёт лучший результат. Вывод ограничен исследованной сеткой и фиксированным разбиением, а не является утверждением о любом наборе данных.")
    QA.mkdir(exist_ok=True)
    authored = QA / "authored.docx"
    doc.save(authored)
    editable = {"word/document.xml", "word/_rels/document.xml.rels", "word/styles.xml", "word/settings.xml", "[Content_Types].xml"}
    ready = QA / "report_ready.docx"
    with ZipFile(REFERENCE) as source, ZipFile(authored) as draft, ZipFile(ready, "w", ZIP_DEFLATED) as result:
        for name in source.namelist():
            result.writestr(name, draft.read(name) if name in editable else source.read(name))
        for name in draft.namelist():
            if name not in source.namelist():
                result.writestr(name, draft.read(name))
    with ZipFile(REFERENCE) as source, ZipFile(ready) as result:
        preserved = [name for name in source.namelist() if name not in editable]
        assert all(source.read(name) == result.read(name) for name in preserved)
        old = etree.fromstring(source.read("word/document.xml"))
        new = etree.fromstring(result.read("word/document.xml"))
        a, b = old.find(qn("w:body")), new.find(qn("w:body"))
        for node in b[9].iter(qn("w:t")):
            node.text = node.text.replace("4", "1")
        for i in range(26):
            assert etree.tostring(a[i], method="c14n") == etree.tostring(b[i], method="c14n"), i
        assert etree.tostring(a[-1], method="c14n") == etree.tostring(b[-1], method="c14n")
        old_rels = etree.fromstring(source.read("word/_rels/document.xml.rels"))
        new_rels = etree.fromstring(result.read("word/_rels/document.xml.rels"))
        assert all(any(r.attrib == s.attrib for s in new_rels) for r in old_rels)
        old_styles = etree.fromstring(source.read("word/styles.xml"))
        new_styles = etree.fromstring(result.read("word/styles.xml"))
        for s in old_styles:
            assert any(etree.tostring(s, method="c14n") == etree.tostring(t, method="c14n") for t in new_styles)
        namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
                      "m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
        anchors = new.xpath(".//w:hyperlink/@w:anchor", namespaces=namespaces)
        bookmarks = new.xpath(".//w:bookmarkStart/@w:name", namespaces=namespaces)
        assert len(anchors) == 11 and all(anchor in bookmarks for anchor in anchors)
        assert len(new.xpath(".//w:fldSimple", namespaces=namespaces)) == 11
        assert len(new.xpath(".//m:oMath", namespaces=namespaces)) == 7
    (QA / "verification.json").write_text(json.dumps({"reference_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        "cover_unchanged_except_lab_number": True, "page_geometry_unchanged": True,
        "preserved_package_parts": len(preserved), "original_styles_and_relationships_preserved": True}, indent=2), encoding="utf-8")
    destination = FINAL
    try:
        ready.replace(destination)
    except PermissionError:
        destination = FINAL.with_stem(FINAL.stem + "_更新版")
        ready.replace(destination)
    print(destination)


if __name__ == "__main__":
    create_report()
