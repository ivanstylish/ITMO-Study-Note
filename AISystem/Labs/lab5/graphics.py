"""Рисунки из сохранённых результатов; готовые метрики не используются."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_results(out, counts, importance, curve, areas):
    figures = out / "figures"
    figures.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    def save(fig, name):
        fig.savefig(figures / f"{name}.png", dpi=180, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.5), layout="constrained")
    x = np.arange(3)
    for c, offset in ((0, -0.18), (1, 0.18)):
        bars = ax.bar(x + offset, [counts[s][str(c)] for s in ("all", "train", "test")],
                      0.36, label=f"Класс {c}")
        ax.bar_label(bars)
    ax.set(xticks=x, xticklabels=["Все данные", "Train", "Test"], xlabel="Выборка",
           ylabel="Число объектов", title="Распределение классов и разбиение 80/20")
    ax.set_ylim(0, max(counts["all"].values()) * 1.2)
    ax.legend()
    save(fig, "class_counts")

    fig, ax = plt.subplots(figsize=(7, 3.6), layout="constrained")
    bars = ax.barh(importance.feature, importance.sum_IG, label="Сумма IG без весов")
    ax.invert_yaxis()
    ax.bar_label(bars, fmt="%.3f", padding=3)
    ax.set(xlabel="Суммарный информационный выигрыш, бит", ylabel="Признак",
           title="Важность пяти отобранных признаков")
    ax.set_xlim(0, importance.sum_IG.max() * 1.22)
    ax.legend(loc="lower right")
    save(fig, "feature_importance")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    axes[0].plot(curve.FPR, curve.TPR, "o-", label=f"ID3, AUC = {areas['ROC_AUC']:.4f}")
    axes[0].plot([0, 1], [0, 1], "--", color="gray", label="Случайный классификатор")
    axes[0].set(xlabel="FPR = FP / (FP + TN)", ylabel="TPR = Recall", title="ROC на тесте")
    axes[1].plot(curve.recall, curve.curve_precision, "o-", label=f"ID3, AUC = {areas['PR_AUC']:.4f}")
    prevalence = counts["test"]["1"] / sum(counts["test"].values())
    axes[1].axhline(prevalence, linestyle="--", color="gray", label=f"Доля класса 1 = {prevalence:.3f}")
    axes[1].set(xlabel="Recall", ylabel="Precision", title="PR на тесте, метод трапеций")
    for ax in axes:
        ax.set(xlim=(-0.03, 1.03), ylim=(-0.03, 1.05))
        ax.legend(fontsize=8, loc="lower right" if ax is axes[0] else "lower left")
        ax.grid(alpha=0.25)
    save(fig, "roc_pr")

    finite = curve[np.isfinite(curve.threshold)].sort_values("threshold")
    fig, ax = plt.subplots(figsize=(7, 3.6), layout="constrained")
    ax.plot(finite.threshold, finite.precision, "o-", label="Precision (0 при отсутствии прогнозов 1)")
    ax.plot(finite.threshold, finite.recall, "s-", label="Recall")
    ax.axvline(0.5, linestyle="--", color="gray", label="Порог 0.5")
    ax.set(xlabel="Порог t, прогноз 1 при p ≥ t", ylabel="Значение метрики",
           title="Влияние порога на тестовые precision и recall", ylim=(-0.03, 1.08))
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25)
    save(fig, "threshold_effect")
