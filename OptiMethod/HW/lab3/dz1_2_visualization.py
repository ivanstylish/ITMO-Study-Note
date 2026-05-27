#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

# ===================== Функции =====================
def f(x):
    return np.tan(x) - 2.0 * np.sin(x)

def df(x):
    return 1.0 / (np.cos(x) ** 2) - 2.0 * np.cos(x)

def hermite_poly(x, x1, x2):
    """Вычисляет кубический многочлен Эрмита P₃(x) на [x1, x2]."""
    h = x2 - x1
    t = (x - x1) / h
    # Базисные функции Эрмита
    H00 = (1 + 2*t) * (1 - t)**2    # f(x1)
    H10 = t * (1 - t)**2            # f'(x1)
    H01 = t**2 * (3 - 2*t)          # f(x2)
    H11 = t**2 * (t - 1)            # f'(x2)
    return H00 * f(x1) + H10 * h * df(x1) + H01 * f(x2) + H11 * h * df(x2)

# ===================== Данные итераций =====================
history = [
    {"iter": 1, "x1": 0.000000, "x2": 0.785398, "x0": 0.639349,
     "f(x0)": -0.449814, "f'(x0)": -0.052127},
    {"iter": 2, "x1": 0.639349, "x2": 0.785398, "x0": 0.654174,
     "f(x0)": -0.450196, "f'(x0)":  0.000900},
    {"iter": 3, "x1": 0.639349, "x2": 0.654174, "x0": 0.653928,
     "f(x0)": -0.450196, "f'(x0)":  0.000000},
]

# ===================== Визуализация =====================
fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))
fig.suptitle(
    "ДЗ 1.2 — Кубическая аппроксимация (Эрмит). "
    "Вариант 6: $f(x)=\mathrm{tg}(x)-2\sin(x)$, $x\in[0,\pi/4]$",
    fontsize=14, fontweight='bold'
)

colors = ['#d62728', '#2ca02c', '#1f77b4']  # красный, зелёный, синий

for idx, (rec, ax) in enumerate(zip(history, axes)):
    x1, x2, x0 = rec["x1"], rec["x2"], rec["x0"]
    color = colors[idx]

    # Исходная функция
    x_plot = np.linspace(0.001, np.pi/4, 500)
    ax.plot(x_plot, f(x_plot), 'k-', linewidth=2.0,
            label='$f(x)=\mathrm{tg}x-2\sin x$')

    # Кубический многочлен Эрмита
    x_poly = np.linspace(max(x1, 0.001), x2, 400)
    p_vals = hermite_poly(x_poly, x1, x2)
    ax.plot(x_poly, p_vals, '--', color=color, linewidth=2.0,
            label=f'$P_3(x)$, ит.{idx+1}')

    # Опорные точки
    ax.scatter([x1, x2], [f(x1), f(x2)],
               s=80, c=color, marker='s', zorder=5,
               edgecolors='black', linewidths=0.8,
               label=f'$x_1$={x1:.4f}, $x_2$={x2:.4f}')

    # Точка x₀ (приближение минимума)
    ax.axvline(x=x0, color=color, linestyle=':', linewidth=1.5, alpha=0.8,
               label=f'$x_0$={x0:.4f}')
    ax.scatter([x0], [f(x0)], s=100, c=color, marker='D', zorder=6,
               edgecolors='black', linewidths=1.0)

    # Оформление
    ax.set_title(f'Итерация {idx+1}', fontsize=12, fontweight='bold')
    ax.set_xlabel('$x$', fontsize=11)
    ax.set_ylabel('$y$', fontsize=11)
    ax.legend(fontsize=8.5, loc='lower left')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, np.pi/4)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))

plt.tight_layout()
plt.savefig("visualization_cubic_lab3_improved.png", dpi=200, bbox_inches='tight')
print("График сохранён: visualization_cubic_lab3_improved.png")
plt.show()

