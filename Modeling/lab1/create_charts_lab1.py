from pathlib import Path
import numpy as np
import openpyxl
import matplotlib.pyplot as plt

folder = Path(__file__).resolve().parent
excel_file = folder / "!_УИР1_Варианты_с — копия.xlsx"
output = folder / "output" / "charts_lab1"
output.mkdir(parents=True, exist_ok=True)

plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["figure.autolayout"] = True
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.25

book = openpyxl.load_workbook(excel_file, read_only=True, data_only=True)
sheet = book["101-150"]
assert sheet["P1"].value == 115, "Проверьте, что вариант 115 находится в столбце P"
values = []
for row in sheet.iter_rows(min_row=2, max_row=301, min_col=16, max_col=16):
    values.append(row[0].value)
book.close()
x = np.array(values, dtype=float)
assert np.isfinite(x).all(), "Исходные данные содержат пропуски или недопустимые значения"
n = len(x)

# 计算均值、标准差、变异系数
mean = np.mean(x)
variance = np.var(x, ddof=1)
std = np.sqrt(variance)
cv = std / mean

q = 0.3
assert cv > 1 and q < 2 / (1 + cv**2), "Выбранные параметры H_2 не подходят для этих данных"
t1 = mean * (1 + np.sqrt((1-q) * (cv**2-1) / (2*q)))
t2 = mean * (1 - np.sqrt(q * (cv**2-1) / (2*(1-q))))

rng = np.random.default_rng(11501)
u1 = rng.random(n)
u2 = rng.random(n)
scale = np.where(u1 < q, t1, t2)
y = -scale * np.log1p(-u2)

# 计算自相关
lags = range(1, 11)
acf_x = []
acf_y = []
for k in lags:
    acf_x.append(np.corrcoef(x[:-k], x[k:])[0, 1])
    acf_y.append(np.corrcoef(y[:-k], y[k:])[0, 1])
bound = 1.96 / np.sqrt(n)

# 原始序列图
plt.figure()
plt.plot(range(1, n+1), x, color="royalblue")
plt.title("Исходная последовательность")
plt.xlabel("Номер наблюдения")
plt.ylabel("Значение")
plt.savefig(output / "01_original_sequence.png", dpi=200)
plt.close()

# 原始序列自相关图
plt.figure()
plt.axhspan(-bound, bound, color="lightblue", alpha=0.5, label="95%: ±1.96/√n")
plt.axhline(0, color="gray")
plt.plot(lags, acf_x, "o-", color="royalblue")
plt.xticks(lags)
plt.title("Автокорреляция исходной последовательности")
plt.xlabel("Сдвиг")
plt.ylabel("Коэффициент автокорреляции")
plt.legend()
plt.savefig(output / "02_original_acf.png", dpi=200)
plt.close()

# 原始序列频数直方图
plt.figure()
bins = np.linspace(x.min(), x.max(), 19)
plt.hist(x, bins=bins, color="royalblue", edgecolor="white")
plt.title("Гистограмма исходной последовательности")
plt.xlabel("Значение")
plt.ylabel("Частота")
plt.savefig(output / "03_original_histogram.png", dpi=200)
plt.close()

# 生成序列图
plt.figure()
plt.plot(range(1, n+1), y, color="tomato")
plt.title("Сгенерированная последовательность")
plt.xlabel("Номер наблюдения")
plt.ylabel("Значение")
plt.savefig(output / "04_generated_sequence.png", dpi=200)
plt.close()

# 生成序列自相关图
plt.figure()
plt.axhspan(-bound, bound, color="lightblue", alpha=0.5, label="95%: ±1.96/√n")
plt.axhline(0, color="gray")
plt.plot(lags, acf_y, "o-", color="tomato")
plt.xticks(lags)
plt.title("Автокорреляция сгенерированной последовательности")
plt.xlabel("Сдвиг")
plt.ylabel("Коэффициент автокорреляции")
plt.legend()
plt.savefig(output / "05_generated_acf.png", dpi=200)
plt.close()

# 原始,生成与理论分布比较
plt.figure()
upper = np.ceil(max(x.max(), y.max()) / 50) * 50
bins = np.linspace(0, upper, 19)

plt.hist(x, bins=bins, density=True, alpha=0.5, color="royalblue", label="Исходная ЧП")
plt.hist(y, bins=bins, density=True, histtype="step", color="tomato", label="Сгенерированная ЧП")
z = np.linspace(0, upper, 500)

# H_2
density = q/t1 * np.exp(-z/t1) + (1-q)/t2 * np.exp(-z/t2)
plt.plot(z, density, color="seagreen", label="Плотность H_2")
plt.title("Сравнение распределений")
plt.xlabel("Значение")
plt.ylabel("Плотность")
plt.legend()
plt.savefig(output / "06_distribution_comparison.png", dpi=200)
plt.close()

# 两条序列放在同一张图上比较
plt.figure()
plt.plot(range(1, n+1), x, color="royalblue", label="Исходная ЧП")
plt.plot(range(1, n+1), y, color="tomato", alpha=0.7, label="Сгенерированная ЧП")
plt.title("Сравнение последовательностей")
plt.xlabel("Номер наблюдения")
plt.ylabel("Значение")
plt.legend()
plt.savefig(output / "07_sequence_comparison.png", dpi=200)
plt.close()

print(f"Среднее = {mean:.5f}; дисперсия = {variance:.5f}; коэффициент вариации = {cv:.5f}")
print(f"t1 = {t1:.5f}; t2 = {t2:.5f}; среднее сгенерированной последовательности = {np.mean(y):.5f}")
print(f"Сохранено 7 графиков. Папка: {output}")
