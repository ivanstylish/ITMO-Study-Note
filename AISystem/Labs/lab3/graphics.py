"""Графики эксперимента. Здесь нет обучения и выбора параметров."""
import numpy as np
from regularization import VARIANTS, CATEGORY, INTERACTION


def make_figures(out, results, grid, iterations):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    folder = out / "figures"
    folder.mkdir(exist_ok=True)
    colors = ["#245d98", "#c34433", "#288264", "#8155a6"]
    styles = ["-", "--", "-.", ":"]
    steps = np.arange(iterations + 1)
    chart_specs = [("train_MSE", "MSE на обучающем наборе", "MSE"),
                   ("validation_MSE", "MSE на валидационном наборе", "MSE"),
                   ("train_R2", "R² на обучающем наборе", "R²"),
                   ("validation_R2", "R² на валидационном наборе", "R²")]

    def draw_curve(ax, result, key, title, ylabel, small=False):
        for i, variant in enumerate(VARIANTS):
            ax.plot(steps, result["history"][key][:, i], label=variant,
                    color=colors[i], linestyle=styles[i], linewidth=1.7)
        ax.set(title=title, xlabel="Итерация", ylabel=ylabel)
        ax.set_xscale("symlog", linthresh=10)
        if ylabel == "MSE":
            ax.set_yscale("log")
        ax.grid(alpha=0.25)
        if not small:
            ax.legend(fontsize=9, loc="lower left" if ylabel == "R²" else "upper right")
        # Деталь последних 10% итераций показывает почти совпадающие линии.
        inset = ax.inset_axes([0.50, 0.24, 0.46, 0.30])
        start = max(1, int(iterations * 0.9))
        for i in range(4):
            inset.plot(steps[start:], result["history"][key][start:, i],
                       color=colors[i], linestyle=styles[i], linewidth=1.2)
        inset.set_title("Последние 10% итераций", fontsize=9 if small else 8)
        inset.tick_params(labelsize=9 if small else 7)
        inset.ticklabel_format(axis="y", style="plain", useOffset=False)
        inset.locator_params(axis="y", nbins=3)
        inset.set_xticks([start, (start + iterations) // 2, iterations])
        inset.set_xlim(start - (iterations-start)*0.12, iterations + (iterations-start)*0.12)
        inset.grid(alpha=0.2)

    for number, (name, result) in enumerate(results.items(), 1):
        fig, axes = plt.subplots(2, 2, figsize=(8, 6.2))
        for ax, (key, title, ylabel) in zip(axes.flat, chart_specs):
            draw_curve(ax, result, key, title, ylabel, small=True)
            single, axis = plt.subplots(figsize=(8, 5), constrained_layout=True)
            draw_curve(axis, result, key, name + " — " + title, ylabel)
            single.savefig(folder / f"model_{number}_{key}.png", dpi=170)
            plt.close(single)
        fig.suptitle(name + ": сравнение четырёх вариантов", fontsize=13)
        fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center",
                   ncol=4, fontsize=9, bbox_to_anchor=(0.5, 0.0))
        fig.tight_layout(rect=(0, 0.065, 1, 0.935))
        fig.savefig(folder / f"model_{number}_curves.png", dpi=180)
        plt.close(fig)

        trials = grid[grid.model == name]
        fig, axes = plt.subplots(1, 3, figsize=(8, 2.55), constrained_layout=True)
        for ax, variant in zip(axes, ["L1", "L2", "ElasticNet"]):
            subset = trials[trials.variant == variant]
            for ratio, group in subset.groupby("l1_ratio"):
                label = f"ρ={ratio:g}" if variant == "ElasticNet" else variant
                ax.plot(group["lambda"], group.validation_MSE, "o-", label=label)
            ax.set(title=variant, xlabel="λ", ylabel="Валидационная MSE")
            ax.set_xscale("log")
            ax.grid(alpha=0.25)
            ax.legend(fontsize=9)
        fig.suptitle(name + ": влияние параметров регуляризации")
        fig.savefig(folder / f"model_{number}_parameters.png", dpi=180)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
        positions = np.arange(len(result["features"]))
        for i, variant in enumerate(VARIANTS):
            ax.bar(positions + (i-1.5)*0.18, result["weights"][1:, i], width=0.18,
                   label=variant, color=colors[i])
        short = {"Hours Studied": "Учёба", "Previous Scores": "Прошлые баллы",
                 "Sleep Hours": "Сон", "Sample Question Papers Practiced": "Практика",
                 CATEGORY: "Внеучебная\nактивность", INTERACTION: "Взаимодействие"}
        ax.set_xticks(positions)
        ax.set_xticklabels([short[f] for f in result["features"]])
        ax.set(title=name + ": стандартизованные коэффициенты", ylabel="Коэффициент")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.legend(fontsize=8)
        fig.savefig(folder / f"model_{number}_coefficients.png", dpi=180)
        plt.close(fig)

