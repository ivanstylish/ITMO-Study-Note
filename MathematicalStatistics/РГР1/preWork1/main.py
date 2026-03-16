import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Настройки графиков (чтобы кириллица отображалась нормально)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

# Загрузка данных
df = pd.read_csv("RGR1_A-12_X1-X4.csv")
columns = ['X1', 'X2', 'X3', 'X4']


# ─── Функция: строит гистограмму + среднее + интервал ±σ ─────────────────────
def plot_histogram_with_stats(col, bins='fd', title_suffix=""):
    data = df[col].dropna().values
    n = len(data)
    mean = np.mean(data)
    std = np.std(data, ddof=1)  # несмещённое СКО

    plt.figure(figsize=(9, 5.5))

    # Гистограмма (плотность)
    sns.histplot(data, bins=bins, stat='density', color='teal', alpha=0.7, edgecolor='black')

    # Вертикальные линии
    plt.axvline(mean, color='red', lw=2.4, label=f'Среднее = {mean:.2f}')
    plt.axvline(mean - std, color='darkorange', lw=1.8, ls='--',
                label=f'±σ = [{mean - std:.1f}, {mean + std:.1f}]')
    plt.axvline(mean + std, color='darkorange', lw=1.8, ls='--')

    plt.title(f"Гистограмма {col}  {title_suffix}\n(n={n}, bins={bins})", fontsize=13)
    plt.xlabel("Значение")
    plt.ylabel("Плотность")
    plt.legend()
    plt.grid(alpha=0.3)

    # Сохраняем график
    plt.tight_layout()
    plt.savefig(f"histogram_{col}_with_mean_sigma.png", dpi=140, bbox_inches='tight')
    plt.show()
    plt.close()


# ─── Строим для всех четырёх столбцов ───────────────────────────────────────
for col in columns:
    print(f"\nОбрабатываем {col} ...")

    # Три разных разбиения — чтобы увидеть структуру лучше
    plot_histogram_with_stats(col, bins='fd', title_suffix="(Freedman-Diaconis)")
    plot_histogram_with_stats(col, bins='sturges', title_suffix="(Sturges)")
    plot_histogram_with_stats(col, bins=25, title_suffix="(25 интервалов)")

print("\nВсе гистограммы сохранены в текущей папке с именами histogram_X?.png")