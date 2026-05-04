import math
import os

import matplotlib.pyplot as plt

from ODEEquation import ODEEquation
from Error import ErrorEstimator


class Plotter:

    _OUTPUT_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot")
    _OUTPUT_FILE = "lab6_plot.png"
    _N_FINE      = 500

    _STYLES = [
        ("royalblue",  "--", "o"),
        ("crimson",    "--", "s"),
        ("seagreen",   "--", "^"),
        ("darkorchid", "--", "D"),
    ]

    @classmethod
    def plot(cls, eq: ODEEquation,
             results: dict,
             x0: float, y0: float,
             xn: float, h: float) -> str:

        os.makedirs(cls._OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(cls._OUTPUT_DIR, cls._OUTPUT_FILE)

        xs_fine = [x0 + i * (xn - x0) / cls._N_FINE
                   for i in range(cls._N_FINE + 1)]
        ys_fine = []
        for x in xs_fine:
            try:
                ys_fine.append(eq.exact_safe(x, x0, y0))
            except ValueError:
                ys_fine.append(float("nan"))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(
            f"Лаб. 6 — Вариант 15  |  {eq.label}\n"
            f"y({x0}) = {y0},  h = {h},  x ∈ [{x0}, {xn}]",
            fontsize=11,
        )

        ax1.plot(xs_fine, ys_fine, "k-", linewidth=2.5,
                 label="Точное решение", zorder=5)
        for idx, (sname, (xs, ys)) in enumerate(results.items()):
            c, ls, mk = cls._STYLES[idx % len(cls._STYLES)]
            ax1.plot(xs, ys, color=c, linestyle=ls, marker=mk,
                     markersize=4, linewidth=1.3, label=sname)
        ax1.set_xlabel("x")
        ax1.set_ylabel("y")
        ax1.set_title("Решения")
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)

        for idx, (sname, (xs, ys)) in enumerate(results.items()):
            c, _, mk = cls._STYLES[idx % len(cls._STYLES)]
            errs = ErrorEstimator.pointwise_errors(eq, x0, y0, xs, ys)
            safe = [max(e, 1e-17) if math.isfinite(e) else float("nan")
                    for e in errs]
            ax2.semilogy(xs, safe, color=c, marker=mk,
                         markersize=3, linewidth=1.3, label=sname)
        ax2.set_xlabel("x")
        ax2.set_ylabel("|погрешность|")
        ax2.set_title("Абсолютные погрешности (log)")
        ax2.legend(fontsize=9)
        ax2.grid(True, which="both", alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=130, bbox_inches="tight")
        plt.close(fig)
        return output_path