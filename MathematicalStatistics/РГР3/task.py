"""
РГР №3 — Регрессионные модели и их интерпретация
Вариант A-3 | Математическая статистика, ИТМО 2026
"""

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings("ignore")

# ── Палитра ────────────────────────────────────────────────────────────────
C_BG      = "#0f1117"
C_PANEL   = "#1a1d27"
C_GRID    = "#2a2d3a"
C_TEXT    = "#e8eaf0"
C_SUB     = "#8b8fa8"
C_DATA    = "#64b5f6"   # scatter points
C_LINEAR  = "#ef5350"   # linear model
C_QUAD    = "#66bb6a"   # quadratic model
C_POWER   = "#ffa726"   # power model
C_ACCENT  = "#ab47bc"

plt.rcParams.update({
    "figure.facecolor":  C_BG,
    "axes.facecolor":    C_PANEL,
    "axes.edgecolor":    C_GRID,
    "axes.labelcolor":   C_TEXT,
    "axes.titlecolor":   C_TEXT,
    "axes.grid":         True,
    "grid.color":        C_GRID,
    "grid.linewidth":    0.7,
    "xtick.color":       C_SUB,
    "ytick.color":       C_SUB,
    "text.color":        C_TEXT,
    "legend.facecolor":  C_PANEL,
    "legend.edgecolor":  C_GRID,
    "legend.labelcolor": C_TEXT,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
})

# ── Данные ─────────────────────────────────────────────────────────────────
x = np.array([64,1000,1000,1500,2000,2000,2000,2000,2000,3000,
              3000,4000,4000,4000,4000,4000,4000,4000,4000,4000,
              5000,5000,6000,6000,6300,8000,8000,8000,8000,8000,
              8000,8000,8000,8000,8000,8000,8000,10480,12000,12000,
              16000,16000,16000,16000,16000,16000,16000,16000,16000,
              16000,20970,24000,32000,32000,32000,32000,32000,32000,
              32000,64000], dtype=float)
y = np.array([10,17,12,7,22,18,24,25,31,44,38,22,38,35,24,25,30,
              37,29,12,20,120,21,198,30,64,45,32,51,50,66,14,72,36,
              67,105,60,32,72,49,214,132,52,144,100,259,212,54,93,45,
              208,237,141,367,134,277,510,307,114,915], dtype=float)

n = len(x)
x_bar, y_bar = np.mean(x), np.mean(y)
Sxx  = np.sum((x - x_bar)**2)
Sxy  = np.sum((x - x_bar)*(y - y_bar))
TSS  = np.sum((y - y_bar)**2)

# ── Линейная модель ─────────────────────────────────────────────────────────
theta1 = Sxy / Sxx
theta0 = y_bar - theta1 * x_bar
y_lin  = theta0 + theta1 * x
RSS_lin = np.sum((y - y_lin)**2)
R2_lin  = 1 - RSS_lin / TSS
A_lin   = 100/n * np.sum(np.abs((y - y_lin)/y))
s2 = RSS_lin / (n - 2);  s = np.sqrt(s2)
SE1 = s / np.sqrt(Sxx)
SE0 = s * np.sqrt(1/n + x_bar**2/Sxx)
t_crit = stats.t.ppf(0.975, df=n-2)
t_obs  = theta1 / SE1
ci1_lo, ci1_hi = theta1 - t_crit*SE1, theta1 + t_crit*SE1
ci0_lo, ci0_hi = theta0 - t_crit*SE0, theta0 + t_crit*SE0

# ── Квадратичная модель ─────────────────────────────────────────────────────
Xq = np.column_stack([np.ones(n), x, x**2])
a_q, b_q, c_q = np.linalg.lstsq(Xq, y, rcond=None)[0]
y_quad  = a_q + b_q*x + c_q*x**2
RSS_quad = np.sum((y - y_quad)**2)
R2_quad  = 1 - RSS_quad / TSS
A_quad   = 100/n * np.sum(np.abs((y - y_quad)/y))

# ── Степенная модель ────────────────────────────────────────────────────────
lx, ly = np.log(x), np.log(y)
b_pow = np.sum((lx - lx.mean())*(ly - ly.mean())) / np.sum((lx - lx.mean())**2)
a_pow = np.exp(ly.mean() - b_pow * lx.mean())
y_pow  = a_pow * x**b_pow
RSS_pow = np.sum((y - y_pow)**2)
R2_pow  = 1 - RSS_pow / TSS
A_pow   = 100/n * np.sum(np.abs((y - y_pow)/y))

# ── Гладкая кривая для графиков ─────────────────────────────────────────────
xs = np.linspace(x.min(), x.max(), 500)
ys_lin  = theta0 + theta1 * xs
ys_quad = a_q + b_q*xs + c_q*xs**2
ys_pow  = a_pow * xs**b_pow

x_star = 10000
pred_lin  = theta0 + theta1 * x_star
pred_quad = a_q + b_q*x_star + c_q*x_star**2
pred_pow  = a_pow * x_star**b_pow

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Диаграмма рассеяния + три модели
# ══════════════════════════════════════════════════════════════════════════════
fig1, ax = plt.subplots(figsize=(12, 7))
fig1.suptitle("РГР №3 · Вариант A-3 — Регрессионные модели",
              fontsize=16, fontweight="bold", color=C_TEXT, y=0.98)

ax.scatter(x, y, color=C_DATA, alpha=0.75, s=55, zorder=5,
           edgecolors="white", linewidths=0.4, label="Данные")
ax.plot(xs, ys_lin,  color=C_LINEAR, lw=2.2, ls="--",
        label=f"Линейная  R²={R2_lin:.3f}")
ax.plot(xs, ys_quad, color=C_QUAD,   lw=2.5,
        label=f"Квадратичная  R²={R2_quad:.3f}")
ax.plot(xs, ys_pow,  color=C_POWER,  lw=2.2, ls="-.",
        label=f"Степенная  R²={R2_pow:.3f}")

# Прогноз при x*=10000
for pred, col in [(pred_lin, C_LINEAR), (pred_quad, C_QUAD), (pred_pow, C_POWER)]:
    ax.plot([x_star, x_star], [0, pred], color=col, alpha=0.35, lw=1, ls=":")
    ax.plot([0, x_star], [pred, pred],   color=col, alpha=0.35, lw=1, ls=":")
ax.axvline(x_star, color=C_ACCENT, lw=1.2, alpha=0.6, ls=":")
ax.text(x_star + 400, 50, "x* = 10 000", color=C_ACCENT, fontsize=9)

ax.set_xlabel("x (фактор)", fontsize=12)
ax.set_ylabel("y (результат)", fontsize=12)
ax.legend(loc="upper left", fontsize=10)
ax.set_xlim(-500, 66000)
ax.set_ylim(-30, 980)

# Текстовый блок уравнений
info = (
    f"Линейная:      ŷ = {theta0:.2f} + {theta1:.5f}·x\n"
    f"Квадратичная:  ŷ = {a_q:.2f} + {b_q:.5f}·x + {c_q:.2e}·x²\n"
    f"Степенная:     ŷ = {a_pow:.4f}·x^{b_pow:.4f}"
)
ax.text(0.98, 0.03, info, transform=ax.transAxes,
        fontsize=8.5, color=C_SUB, ha="right", va="bottom",
        fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", fc=C_BG, ec=C_GRID, alpha=0.85))

plt.tight_layout()
plt.savefig("fig1_scatter_models.png",
            dpi=160, bbox_inches="tight", facecolor=C_BG)
print("Сохранено: fig1_scatter_models.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Сравнение моделей: метрики (bar chart)
# ══════════════════════════════════════════════════════════════════════════════
fig2, axes = plt.subplots(1, 2, figsize=(12, 5))
fig2.suptitle("Сравнение качества трёх моделей", fontsize=15,
              fontweight="bold", color=C_TEXT)

labels = ["Линейная", "Квадратичная", "Степенная"]
r2s    = [R2_lin,  R2_quad,  R2_pow]
As     = [A_lin,   A_quad,   A_pow]
colors = [C_LINEAR, C_QUAD, C_POWER]

# R²
bars = axes[0].bar(labels, r2s, color=colors, width=0.5,
                   edgecolor=C_BG, linewidth=1.2)
axes[0].set_ylim(0, 1.05)
axes[0].set_title("Коэффициент детерминации R²", fontsize=12)
axes[0].axhline(1, color=C_GRID, lw=0.8, ls="--")
for bar, v in zip(bars, r2s):
    axes[0].text(bar.get_x() + bar.get_width()/2, v + 0.02,
                 f"{v:.3f}", ha="center", fontsize=12, fontweight="bold")

# Средняя ошибка
bars2 = axes[1].bar(labels, As, color=colors, width=0.5,
                    edgecolor=C_BG, linewidth=1.2)
axes[1].set_title("Средняя ошибка аппроксимации Ā, %", fontsize=12)
for bar, v in zip(bars2, As):
    axes[1].text(bar.get_x() + bar.get_width()/2, v + 1,
                 f"{v:.1f}%", ha="center", fontsize=12, fontweight="bold")

for ax_ in axes:
    ax_.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig("fig2_model_comparison.png",
            dpi=160, bbox_inches="tight", facecolor=C_BG)
print("Сохранено: fig2_model_comparison.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Графики остатков для трёх моделей
# ══════════════════════════════════════════════════════════════════════════════
fig3, axes3 = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
fig3.suptitle("Анализ остатков", fontsize=15, fontweight="bold", color=C_TEXT)

residuals = [y - y_lin, y - y_quad, y - y_pow]
titles    = ["Линейная", "Квадратичная", "Степенная"]
cols      = [C_LINEAR, C_QUAD, C_POWER]

for ax_, res, ttl, col in zip(axes3, residuals, titles, cols):
    ax_.scatter(x, res, color=col, alpha=0.7, s=45,
                edgecolors="white", linewidths=0.3)
    ax_.axhline(0, color="white", lw=1.2, ls="--", alpha=0.7)
    # Полоса ±s
    s_ = np.std(res, ddof=2)
    ax_.axhline(+s_, color=col, lw=0.8, ls=":", alpha=0.5)
    ax_.axhline(-s_, color=col, lw=0.8, ls=":", alpha=0.5)
    ax_.fill_between([x.min(), x.max()], -s_, s_, color=col, alpha=0.06)
    ax_.set_title(f"{ttl}  (σ={s_:.1f})", fontsize=11)
    ax_.set_xlabel("x")
    ax_.set_ylabel("Остаток  eᵢ" if ax_ is axes3[0] else "")

plt.tight_layout()
plt.savefig("fig3_residuals.png",
            dpi=160, bbox_inches="tight", facecolor=C_BG)
print("Сохранено: fig3_residuals.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Детальный анализ линейной модели (доверительный интервал, t-тест)
# ══════════════════════════════════════════════════════════════════════════════
fig4 = plt.figure(figsize=(14, 8))
fig4.suptitle("Статистический анализ линейной модели",
              fontsize=15, fontweight="bold", color=C_TEXT)
gs = gridspec.GridSpec(2, 2, figure=fig4, hspace=0.45, wspace=0.35)

# -- (0,0) Линейная модель с полосой доверительного интервала
ax40 = fig4.add_subplot(gs[0, 0])
se_band = t_crit * s * np.sqrt(1/n + (xs - x_bar)**2/Sxx)
ax40.fill_between(xs, ys_lin - se_band, ys_lin + se_band,
                  color=C_LINEAR, alpha=0.2, label="95% ДИ прогноза")
ax40.scatter(x, y, color=C_DATA, s=40, alpha=0.7, zorder=5,
             edgecolors="white", linewidths=0.3)
ax40.plot(xs, ys_lin, color=C_LINEAR, lw=2, label="Линейная модель")
ax40.set_title("Линейная модель с ДИ", fontsize=11)
ax40.set_xlabel("x");  ax40.set_ylabel("y")
ax40.legend(fontsize=8)

# -- (0,1) Распределение остатков (гистограмма)
ax41 = fig4.add_subplot(gs[0, 1])
e_lin = y - y_lin
ax41.hist(e_lin, bins=14, color=C_LINEAR, edgecolor=C_BG,
          alpha=0.85, density=True)
# Нормальная кривая
xe = np.linspace(e_lin.min(), e_lin.max(), 200)
ax41.plot(xe, stats.norm.pdf(xe, 0, s), color="white", lw=1.8,
          label="N(0, s²)")
ax41.axvline(0, color=C_ACCENT, ls="--", lw=1.2)
ax41.set_title("Гистограмма остатков", fontsize=11)
ax41.set_xlabel("eᵢ");  ax41.legend(fontsize=8)

# -- (1,0) t-тест визуализация
ax42 = fig4.add_subplot(gs[1, 0])
df_ = n - 2
t_range = np.linspace(-15, 15, 500)
pdf_t = stats.t.pdf(t_range, df=df_)
ax42.plot(t_range, pdf_t, color=C_TEXT, lw=1.8)
ax42.fill_between(t_range, pdf_t,
                  where=(t_range < -t_crit) | (t_range > t_crit),
                  color=C_LINEAR, alpha=0.45, label=f"Зона отверж. (α=0.05)")
ax42.axvline(t_obs,   color=C_ACCENT, lw=2.2, label=f"t_набл = {t_obs:.2f}")
ax42.axvline(-t_crit, color=C_GRID,   lw=1, ls="--")
ax42.axvline( t_crit, color=C_GRID,   lw=1, ls="--",
              label=f"±t_кр = ±{t_crit:.4f}")
ax42.set_title("Проверка H₀: θ₁ = 0", fontsize=11)
ax42.set_xlabel("t");  ax42.legend(fontsize=8)
ax42.set_xlim(-15, 15)

# -- (1,1) Таблица с итогами
ax43 = fig4.add_subplot(gs[1, 1])
ax43.axis("off")
table_data = [
    ["Параметр", "Значение"],
    ["θ̂₀", f"{theta0:.4f}"],
    ["θ̂₁", f"{theta1:.6f}"],
    ["SE(θ̂₀)", f"{SE0:.4f}"],
    ["SE(θ̂₁)", f"{SE1:.7f}"],
    ["ДИ θ₀", f"[{ci0_lo:.2f}; {ci0_hi:.2f}]"],
    ["ДИ θ₁", f"[{ci1_lo:.5f}; {ci1_hi:.5f}]"],
    ["t_набл", f"{t_obs:.4f}"],
    ["t_кр (α=0.05)", f"{t_crit:.4f}"],
    ["R²", f"{R2_lin:.4f}"],
    ["s (ст. ош.)", f"{s:.4f}"],
    ["Ā, %", f"{A_lin:.2f}%"],
]
tbl = ax43.table(cellText=table_data[1:], colLabels=table_data[0],
                 loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1.15, 1.55)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor(C_PANEL if r % 2 == 0 else C_BG)
    cell.set_edgecolor(C_GRID)
    cell.set_text_props(color=C_TEXT if r > 0 else C_ACCENT)
ax43.set_title("Сводная таблица — линейная модель", fontsize=10, pad=8)

plt.savefig("fig4_linear_analysis.png",
            dpi=160, bbox_inches="tight", facecolor=C_BG)
print("Сохранено: fig4_linear_analysis.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Прогнозы при x* = 10 000
# ══════════════════════════════════════════════════════════════════════════════
fig5, ax5 = plt.subplots(figsize=(9, 5))
fig5.suptitle("Прогноз при x* = 10 000", fontsize=14,
              fontweight="bold", color=C_TEXT)

preds  = [pred_lin, pred_quad, pred_pow]
colors5= [C_LINEAR, C_QUAD, C_POWER]
lbls5  = [f"Линейная\n{pred_lin:.2f}", f"Квадратичная\n{pred_quad:.2f}",
          f"Степенная\n{pred_pow:.2f}"]
bars5 = ax5.bar(["Линейная", "Квадратичная", "Степенная"],
                preds, color=colors5, width=0.45,
                edgecolor=C_BG, linewidth=1.2)
for bar, v in zip(bars5, preds):
    ax5.text(bar.get_x()+bar.get_width()/2, v+1,
             f"ŷ = {v:.2f}", ha="center", fontsize=12, fontweight="bold")
ax5.set_ylabel("ŷ(x* = 10 000)", fontsize=12)
ax5.set_ylim(0, max(preds)*1.25)
ax5.tick_params(labelsize=12)

plt.tight_layout()
plt.savefig("fig5_forecast.png",
            dpi=160, bbox_inches="tight", facecolor=C_BG)
print("Сохранено: fig5_forecast.png")
print()
print("=" * 55)
print("ИТОГИ")
print("=" * 55)
print(f"Линейная:      θ₀={theta0:.4f}, θ₁={theta1:.6f}, R²={R2_lin:.4f}, Ā={A_lin:.2f}%")
print(f"Квадратичная:  a={a_q:.4f}, b={b_q:.5f}, c={c_q:.3e}, R²={R2_quad:.4f}, Ā={A_quad:.2f}%")
print(f"Степенная:     a={a_pow:.5f}, b={b_pow:.5f}, R²={R2_pow:.4f}, Ā={A_pow:.2f}%")
print(f"\nПрогноз при x*=10000:  Лин={pred_lin:.2f}, Кв={pred_quad:.2f}, Степ={pred_pow:.2f}")
print(f"t_набл={t_obs:.4f}, t_кр={t_crit:.4f}  →  H₀ {'отвергается' if abs(t_obs) > t_crit else 'не отвергается'}")
plt.show()