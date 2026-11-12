"""仅从已得到的数据和结果绘图，不参与训练或参数选择。"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAMES = {"euclidean": "Евклидово", "manhattan": "Манхэттенское", "chebyshev": "Чебышёва"}


def make_figures(out, results, summary):
    folder = out / "figures"
    folder.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    def save(fig, name):
        fig.savefig(folder / (name + ".png"), dpi=180)
        plt.close(fig)

    for name, result in results.items():
        frame, grid = result["frame"], result["grid"]
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
        stats = frame.drop(columns="target").describe().T
        axes[0].errorbar(np.arange(len(stats)), stats["mean"], yerr=stats["std"],
                         fmt="o", capsize=3, label="Среднее ± SD (ddof=1)")
        axes[0].set_xticks(np.arange(len(stats)), stats.index, rotation=70, fontsize=8)
        axes[0].set(title=f"{name.title()}: исходный масштаб", xlabel="Признак", ylabel="Значение")
        axes[0].legend(fontsize=8)
        if name == "wine":
            counts = frame.target.value_counts().sort_index()
            axes[1].bar(counts.index.astype(str), counts.values, label="Число объектов")
            axes[1].set(title="Распределение классов Wine", xlabel="Класс", ylabel="Число объектов")
        else:
            axes[1].hist(frame.target, bins=16, edgecolor="white", label="Наблюдения")
            axes[1].set(title="Распределение целевого показателя", xlabel="Прогрессирование диабета", ylabel="Частота")
        axes[1].legend(fontsize=8)
        save(fig, name + "_statistics")

        score = "F1_macro" if name == "wine" else "MSE"
        fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
        for distance, group in grid.groupby("distance", sort=False):
            ax.plot(group.k, group[score], "o-", label=NAMES[distance])
        ax.set(title=f"{name.title()}: качество на валидации", xlabel="Количество соседей k", ylabel=score,
               xticks=[3, 5, 10, 15])
        ax.legend()
        ax.grid(alpha=0.3)
        save(fig, name + "_validation")

    matrix = np.asarray(summary["datasets"]["wine"]["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(6, 4), constrained_layout=True)
    chart = ax.imshow(matrix, cmap="Blues", vmin=0)
    fig.colorbar(chart, ax=ax, label="Число объектов")
    for (i, j), value in np.ndenumerate(matrix):
        ax.text(j, i, str(value), ha="center", va="center",
                color="white" if value > matrix.max() / 2 else "black")
    ax.set(title="Wine: матрица ошибок на тесте", xlabel="Предсказанный класс", ylabel="Истинный класс",
           xticks=[0, 1, 2], yticks=[0, 1, 2])
    save(fig, "wine_confusion_matrix")

    actual, predicted = results["diabetes"]["actual"], results["diabetes"]["predicted"]
    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    ax.scatter(actual, predicted, alpha=0.75, label="Тестовые объекты")
    bounds = [min(actual.min(), predicted.min()), max(actual.max(), predicted.max())]
    ax.plot(bounds, bounds, "--", color="black", label="Идеальный прогноз")
    ax.set(title="Diabetes: фактические и предсказанные значения", xlabel="Фактическое значение",
           ylabel="Предсказанное значение")
    ax.legend()
    ax.grid(alpha=0.3)
    save(fig, "diabetes_predictions")
