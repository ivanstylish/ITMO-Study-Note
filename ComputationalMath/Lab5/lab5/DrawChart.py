import matplotlib

matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt


class DrawChart:

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

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(x_fine, safe_curve("lagrange"),
                color="blue", linestyle="-", lw=2.5, label="Лагранж")
        ax.plot(x_fine, safe_curve("newton_forward"),
                color="green", linestyle="--", lw=2, label="Ньютон вперёд")
        ax.plot(x_fine, safe_curve("newton_backward"),
                color="purple", linestyle="-.", lw=2, label="Ньютон назад")
        ax.plot(x_fine, safe_curve("gauss_forward"),
                color="orange", linestyle=":", lw=2, label="Гаусс вперёд")
        ax.plot(x_fine, safe_curve("gauss_backward"),
                color="red", linestyle="--", lw=1.5, alpha=0.7, label="Гаусс назад")

        # 绘制原始节点
        ax.scatter(self._d.x, self._d.y,
                   color="black", zorder=5, s=60, label="Узлы интерполяции")

        # 绘制查询点
        if query_points:
            for xp, _ in query_points:
                try:
                    yp = self._ip.lagrange(xp)
                    ax.scatter([xp], [yp], color="red",
                               zorder=6, s=90, marker="*")
                    ax.annotate(
                        f"x={xp}\ny≈{yp:.4f}", (xp, yp),
                        textcoords="offset points", xytext=(8, 8),
                        fontsize=9, color="darkred",
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
