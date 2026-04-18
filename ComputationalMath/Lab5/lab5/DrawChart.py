# =====================================================================
#  4. DrawChart — построение и сохранение графика
# =====================================================================
import matplotlib
matplotlib.use("Agg")  # без GUI-дисплея (обязательно до pyplot)
import numpy as np
from matplotlib import pyplot as plt


class DrawChart:
    """Строит кривые интерполяции и сохраняет PNG."""

    def __init__(self, data, interpolator):
        self._d = data
        self._ip = interpolator

    def plot(self, query_points=None,
             title="Интерполяция", filename="interpolation_plot.png"):
        x_fine = np.linspace(self._d.x[0], self._d.x[-1], 500)

        def safe_curve(method_name):
            vals = []
            for xp in x_fine:
                try:
                    vals.append(getattr(self._ip, method_name)(xp))
                except Exception:
                    vals.append(float("nan"))
            return vals

        fig, ax = plt.subplots(figsize=(9, 6))
        ax.plot(x_fine, safe_curve("lagrange"),
                "b-", lw=2, label="Лагранж")
        ax.plot(x_fine, safe_curve("newton_divided"),
                "g--", lw=2, label="Ньютон (разд. разн.)")
        ax.scatter(self._d.x, self._d.y,
                   color="red", zorder=5, s=60, label="Узлы интерполяции")

        if query_points:
            for xp, _ in query_points:
                try:
                    yp = self._ip.lagrange(xp)
                    ax.scatter([xp], [yp], color="orange",
                               zorder=6, s=90, marker="*")
                    ax.annotate(
                        f"x={xp}\ny≈{yp:.4f}", (xp, yp),
                        textcoords="offset points", xytext=(8, 8),
                        fontsize=9, color="darkorange",
                    )
                except Exception:
                    pass

        ax.set_title(title, fontsize=13)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend()
        ax.grid(True, alpha=0.4)
        plt.tight_layout()
        plt.savefig(filename, dpi=120)
        plt.close()
        print(f"\nГрафик сохранён в '{filename}'.")