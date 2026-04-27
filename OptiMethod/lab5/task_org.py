import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
import warnings
import os

warnings.filterwarnings('ignore')
plt.rcParams['font.family'] = 'DejaVu Sans'

# Графики сохраняются в ту же папку, где лежит скрипт
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def save(name):
    path = os.path.join(OUTPUT_DIR, name)
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Сохранён: {path}")

# ==============================================================================
# ВАРИАНТ 6
# ==============================================================================
data = np.array([
    [0.88, 1.14, -0.10],
    [1.92, 1.95,  1.72],
    [2.85, 3.04,  4.73],
    [3.88, 4.12,  2.27],
    [5.02, 5.03,  0.03]
])

X = data[:, 0]
Y = data[:, 1]
Z = data[:, 2]

print("Мои данные:")
for i in range(len(X)):
    print(f"  Точка {i}: x={X[i]:.2f}, y={Y[i]:.2f}, z={Z[i]:.2f}")

# ==============================================================================
# ЗАДАНИЕ 1: Двумерная гауссиана
# z_G = A * exp(-Q) + offset
# Q = x_new^2/(2*sigma_x^2) + y_new^2/(2*sigma_y^2)
# x_new = (x-x0)*cos(theta) + (y-y0)*sin(theta)
# y_new = -(x-x0)*sin(theta) + (y-y0)*cos(theta)
# ==============================================================================
def gauss_2d(x, y, A, x0, y0, sigma_x, sigma_y, theta=0, offset=0):
    if theta != 0:
        x_new = (x - x0) * np.cos(theta) + (y - y0) * np.sin(theta)
        y_new = -(x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    else:
        x_new = x - x0
        y_new = y - y0
    exp_part = np.exp(-(x_new**2 / (2 * sigma_x**2) + y_new**2 / (2 * sigma_y**2)))
    return A * exp_part + offset


def loss_gauss(params):
    A, x0, y0, sigma_x, sigma_y, theta, offset = params
    if sigma_x <= 0 or sigma_y <= 0 or A <= 0:
        return 1e10
    preds = [gauss_2d(X[i], Y[i], A, x0, y0, sigma_x, sigma_y, theta, offset)
             for i in range(len(X))]
    return 0.5 * np.mean((np.array(preds) - Z) ** 2)


max_idx       = np.argmax(Z)
A_start       = Z[max_idx] + 0.1
x0_start      = X[max_idx]
y0_start      = Y[max_idx]
sigma_x_start = np.std(X) * 0.5
sigma_y_start = np.std(Y) * 0.5
params_start_gauss = [A_start, x0_start, y0_start, sigma_x_start, sigma_y_start, 0.0, 0.0]

print(f"\nНачальное приближение (гауссиана):")
print(f"  A={A_start:.2f}, x0={x0_start:.2f}, y0={y0_start:.2f}")
print(f"  sigma_x={sigma_x_start:.2f}, sigma_y={sigma_y_start:.2f}, theta=0.00, offset=0.00")

bounds_gauss = [
    (0.1, 10.0), (0.0, 6.0), (0.0, 6.0),
    (0.1, 5.0),  (0.1, 5.0), (-np.pi/4, np.pi/4), (-1.0, 1.0)
]

gauss_loss_hist = [loss_gauss(params_start_gauss)]
# Добавляем счетчик итераций
def gauss_cb(p):
    current_loss = loss_gauss(p)
    gauss_loss_hist.append(current_loss)
    iteration = len(gauss_loss_hist)
    print(f"  Гауссиана | Итерация {iteration:3}: Loss = {current_loss:.10f}")

print("\nОптимизация гауссианы (L-BFGS-B)...")
res_gauss = minimize(loss_gauss, params_start_gauss, method='L-BFGS-B',
                     bounds=bounds_gauss, callback=gauss_cb)
gauss_loss_hist.append(res_gauss.fun)

A_g, x0_g, y0_g, sx_g, sy_g, th_g, off_g = res_gauss.x
preds_gauss = [gauss_2d(X[i], Y[i], A_g, x0_g, y0_g, sx_g, sy_g, th_g, off_g)
               for i in range(len(X))]
resid_gauss = Z - np.array(preds_gauss)

print("\n" + "="*60)
print("РЕЗУЛЬТАТЫ — ГАУССИАНА")
print("="*60)
print(f"  A        = {A_g:.4f}")
print(f"  x0, y0   = ({x0_g:.4f}, {y0_g:.4f})")
print(f"  sigma_x  = {sx_g:.4f},  sigma_y = {sy_g:.4f}")
print(f"  theta    = {th_g:.4f} рад = {np.degrees(th_g):.2f} deg")
print(f"  offset   = {off_g:.4f}")
print(f"  MSE финал = {res_gauss.fun:.8f}")
print(f"\n  Аналитический вид:")
print(f"  z(x,y) = {A_g:.4f} * exp(-Q) + ({off_g:.4f})")
print(f"  Q = x_new^2/(2*{sx_g:.4f}^2) + y_new^2/(2*{sy_g:.4f}^2)")
print(f"  x_new = (x-{x0_g:.4f})*cos({th_g:.4f}) + (y-{y0_g:.4f})*sin({th_g:.4f})")
print(f"  y_new = -(x-{x0_g:.4f})*sin({th_g:.4f}) + (y-{y0_g:.4f})*cos({th_g:.4f})")

print("\n  Таблица невязок (гауссиана):")
print(f"  {'No':>3} | {'x':>6} | {'y':>6} | {'z факт':>8} | {'z модель':>9} | {'невязка':>9}")
print("  " + "-"*55)
for i in range(len(X)):
    print(f"  {i:>3} | {X[i]:>6.2f} | {Y[i]:>6.2f} | {Z[i]:>8.4f} | {preds_gauss[i]:>9.4f} | {resid_gauss[i]:>9.4f}")
print("  " + "-"*55)
print(f"  {'MSE':>3} | {' ':>6} | {' ':>6} | {' ':>8} | {' ':>9} | {0.5*np.mean(resid_gauss**2):>9.6f}")
print(f"  {'MAE':>3} | {' ':>6} | {' ':>6} | {' ':>8} | {' ':>9} | {np.mean(np.abs(resid_gauss)):>9.6f}")

# ==============================================================================
# ЗАДАНИЕ 2: Эллиптический параболоид
# z_P = a*(x-x0)^2 + b*(y-y0)^2 + c*(x-x0)*(y-y0) + z0,  ab > c^2
# ==============================================================================
print("\n" + "="*60)
print("ЗАДАНИЕ 2 — ЭЛЛИПТИЧЕСКИЙ ПАРАБОЛОИД")
print("="*60)

def paraboloid(x, y, a, b, c, x0, y0, z0):
    return a*(x-x0)**2 + b*(y-y0)**2 + c*(x-x0)*(y-y0) + z0

def loss_par(params):
    a, b, c, x0, y0, z0 = params
    if a * b <= c**2:
        return 1e10
    preds = [paraboloid(X[i], Y[i], a, b, c, x0, y0, z0) for i in range(len(X))]
    return 0.5 * np.mean((np.array(preds) - Z) ** 2)

params_start_par = [1.0, 1.0, 0.0, np.mean(X), np.mean(Y), np.max(Z)]
par_loss_hist = [loss_par(params_start_par)]
def par_cb(p):
    current_loss = loss_par(p)
    par_loss_hist.append(current_loss)
    iteration = len(par_loss_hist)
    print(f"  Параболоид | Итерация {iteration:3}: Loss = {current_loss:.10f}")

bounds_par = [(-10, 10), (-10, 10), (-10, 10), (0, 6), (0, 6), (-5, 15)]

print("\nОптимизация параболоида (L-BFGS-B)...")
res_par = minimize(loss_par, params_start_par, method='L-BFGS-B',
                   bounds=bounds_par, callback=par_cb)
par_loss_hist.append(res_par.fun)

a_p, b_p, c_p, x0_p, y0_p, z0_p = res_par.x
preds_par = [paraboloid(X[i], Y[i], a_p, b_p, c_p, x0_p, y0_p, z0_p) for i in range(len(X))]
resid_par = Z - np.array(preds_par)

print(f"\n  a={a_p:.4f}, b={b_p:.4f}, c={c_p:.4f}")
print(f"  x0={x0_p:.4f}, y0={y0_p:.4f}, z0={z0_p:.4f}")
print(f"  Условие ab > c^2: {a_p*b_p:.4f} > {c_p**2:.4f} => {a_p*b_p > c_p**2}")
print(f"  MSE финал = {res_par.fun:.8f}")
print(f"\n  Аналитический вид:")
print(f"  z(x,y) = {z0_p:.4f}")
print(f"         + {a_p:.4f}*(x - {x0_p:.4f})^2")
print(f"         + {b_p:.4f}*(y - {y0_p:.4f})^2")
print(f"         + {c_p:.4f}*(x - {x0_p:.4f})*(y - {y0_p:.4f})")

print("\n  Таблица невязок (параболоид):")
print(f"  {'No':>3} | {'x':>6} | {'y':>6} | {'z факт':>8} | {'z модель':>9} | {'невязка':>9}")
print("  " + "-"*55)
for i in range(len(X)):
    print(f"  {i:>3} | {X[i]:>6.2f} | {Y[i]:>6.2f} | {Z[i]:>8.4f} | {preds_par[i]:>9.4f} | {resid_par[i]:>9.4f}")
print("  " + "-"*55)
print(f"  {'MSE':>3} | {' ':>6} | {' ':>6} | {' ':>8} | {' ':>9} | {0.5*np.mean(resid_par**2):>9.6f}")
print(f"  {'MAE':>3} | {' ':>6} | {' ':>6} | {' ':>8} | {' ':>9} | {np.mean(np.abs(resid_par)):>9.6f}")

# ==============================================================================
# ЗАДАНИЕ 3: Константные модели
# ==============================================================================
print("\n" + "="*60)
print("ЗАДАНИЕ 3 — КОНСТАНТНЫЕ МОДЕЛИ")
print("="*60)

z_mean   = np.mean(Z)
z_median = np.median(Z)
mse_mean = 0.5 * np.mean((Z - z_mean)**2)
mae_med  = np.mean(np.abs(Z - z_median))
resid_mean   = Z - z_mean
resid_median = Z - z_median

print(f"\n  Лучшая константа (мин. MSE) = среднее = {z_mean:.4f}  =>  MSE = {mse_mean:.4f}")
print(f"  Лучшая константа (мин. MAE) = медиана = {z_median:.4f}  =>  MAE = {mae_med:.4f}")

print("\n  Таблица невязок (константа MSE — среднее):")
print(f"  {'No':>3} | {'z факт':>8} | {'z модель':>9} | {'невязка':>9}")
print("  " + "-"*36)
for i in range(len(X)):
    print(f"  {i:>3} | {Z[i]:>8.4f} | {z_mean:>9.4f} | {resid_mean[i]:>9.4f}")

print("\n  Таблица невязок (константа MAE — медиана):")
print(f"  {'No':>3} | {'z факт':>8} | {'z модель':>9} | {'невязка':>9}")
print("  " + "-"*36)
for i in range(len(X)):
    print(f"  {i:>3} | {Z[i]:>8.4f} | {z_median:>9.4f} | {resid_median[i]:>9.4f}")

# ==============================================================================
# ИТОГОВАЯ СРАВНИТЕЛЬНАЯ ТАБЛИЦА
# ==============================================================================
print("\n" + "="*60)
print("ИТОГОВОЕ СРАВНЕНИЕ МОДЕЛЕЙ")
print("="*60)
print(f"  {'Модель':<28} | {'MSE':>10} | {'MAE':>10}")
print("  " + "-"*54)
print(f"  {'Гауссиана':<28} | {0.5*np.mean(resid_gauss**2):>10.6f} | {np.mean(np.abs(resid_gauss)):>10.6f}")
print(f"  {'Параболоид':<28} | {0.5*np.mean(resid_par**2):>10.6f} | {np.mean(np.abs(resid_par)):>10.6f}")
print(f"  {'Константа (оптим. по MSE)':<28} | {mse_mean:>10.6f} | {np.mean(np.abs(resid_mean)):>10.6f}")
print(f"  {'Константа (оптим. по MAE)':<28} | {0.5*np.mean(resid_median**2):>10.6f} | {mae_med:>10.6f}")

# ==============================================================================
# ГРАФИКИ
# ==============================================================================
x_grid = np.linspace(0, 6, 60)
y_grid = np.linspace(0, 6, 60)
Xg, Yg = np.meshgrid(x_grid, y_grid)
Zg_gauss = gauss_2d(Xg, Yg, A_g, x0_g, y0_g, sx_g, sy_g, th_g, off_g)
Zg_par   = paraboloid(Xg, Yg, a_p, b_p, c_p, x0_p, y0_p, z0_p)

print("\nСохранение графиков...")

# --- 1. Кривые обучения ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Кривые обучения (Loss vs Iteration)', fontsize=14, fontweight='bold')
axes[0].semilogy(gauss_loss_hist, 'b-o', markersize=4)
axes[0].set_xlabel('Итерация'); axes[0].set_ylabel('Loss (MSE)')
axes[0].set_title('Гауссиана'); axes[0].grid(True, alpha=0.3)
axes[1].semilogy(par_loss_hist, 'r-o', markersize=4)
axes[1].set_xlabel('Итерация'); axes[1].set_ylabel('Loss (MSE)')
axes[1].set_title('Эллиптический параболоид'); axes[1].grid(True, alpha=0.3)
plt.tight_layout()
save('01_loss_curves.png')

# --- 2. Гауссиана 3D + контуры ---
fig = plt.figure(figsize=(15, 6))
fig.suptitle('Задание 1: Двумерная гауссиана (вариант 6)', fontsize=14, fontweight='bold')
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(Xg, Yg, Zg_gauss, cmap='viridis', alpha=0.8)
ax1.scatter(X, Y, Z, c='red', s=60, zorder=5, label='Данные')
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
ax1.set_title('3D-поверхность'); ax1.legend()
ax2 = fig.add_subplot(122)
cf = ax2.contourf(Xg, Yg, Zg_gauss, levels=25, cmap='viridis', alpha=0.9)
ax2.contour(Xg, Yg, Zg_gauss, levels=10, colors='white', alpha=0.4, linewidths=0.5)
ax2.scatter(X, Y, c=Z, s=120, edgecolors='red', linewidths=1.5, cmap='viridis', zorder=5)
for i in range(len(X)):
    ax2.annotate(f'z={Z[i]:.2f}', (X[i]+0.06, Y[i]+0.1), fontsize=8.5, color='white',
                 bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.45))
plt.colorbar(cf, ax=ax2, label='Z')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_title('Линии уровня + точки данных')
ax2.grid(True, alpha=0.25)
plt.tight_layout()
save('02_gaussian.png')

# --- 3. Параболоид 3D + контуры ---
fig = plt.figure(figsize=(15, 6))
fig.suptitle('Задание 2: Эллиптический параболоид (вариант 6)', fontsize=14, fontweight='bold')
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(Xg, Yg, Zg_par, cmap='plasma', alpha=0.8)
ax1.scatter(X, Y, Z, c='red', s=60, zorder=5, label='Данные')
ax1.set_xlabel('X'); ax1.set_ylabel('Y'); ax1.set_zlabel('Z')
ax1.set_title('3D-поверхность'); ax1.legend()
ax2 = fig.add_subplot(122)
cf = ax2.contourf(Xg, Yg, Zg_par, levels=25, cmap='plasma', alpha=0.9)
ax2.contour(Xg, Yg, Zg_par, levels=10, colors='white', alpha=0.4, linewidths=0.5)
ax2.scatter(X, Y, c=Z, s=120, edgecolors='red', linewidths=1.5, cmap='plasma', zorder=5)
for i in range(len(X)):
    ax2.annotate(f'z={Z[i]:.2f}', (X[i]+0.06, Y[i]+0.1), fontsize=8.5, color='white',
                 bbox=dict(boxstyle='round,pad=0.15', facecolor='black', alpha=0.45))
plt.colorbar(cf, ax=ax2, label='Z')
ax2.set_xlabel('X'); ax2.set_ylabel('Y'); ax2.set_title('Линии уровня + точки данных')
ax2.grid(True, alpha=0.25)
plt.tight_layout()
save('03_paraboloid.png')

# --- 4. Невязки —  барграфы ---
pts = [f'T{i}\n({X[i]:.1f},{Y[i]:.1f})' for i in range(len(X))]
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Невязки на каждом объекте (z - z_model)', fontsize=14, fontweight='bold')
for ax, resid, title in [
    (axes[0], resid_gauss, f'Gaussiana  MSE={0.5*np.mean(resid_gauss**2):.4f}'),
    (axes[1], resid_par,   f'Paraboloid  MSE={0.5*np.mean(resid_par**2):.4f}'),
]:
    bar_colors = ['#2ecc71' if abs(r) < 0.05 else '#f39c12' if abs(r) < 1.0 else '#e74c3c'
                  for r in resid]
    bars = ax.bar(pts, resid, color=bar_colors, edgecolor='black', linewidth=0.6)
    ax.axhline(0, color='black', linewidth=1.2)
    for bar, val in zip(bars, resid):
        ypos = val + 0.05 if val >= 0 else val - 0.05
        va   = 'bottom' if val >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, ypos, f'{val:.3f}',
                ha='center', va=va, fontsize=9)
    ax.set_ylabel('Nevyazka'); ax.set_title(title); ax.grid(True, alpha=0.3)
plt.tight_layout()
save('04_residuals.png')

# --- 5. Константные модели ---
pts_s = [f'T{i}' for i in range(len(X))]
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Задание 3: Константные модели', fontsize=14, fontweight='bold')
for ax, z_const, color, label in [
    (axes[0], z_mean,   'steelblue',
     f'Константа MSE\nz = {z_mean:.4f},  MSE = {mse_mean:.4f}'),
    (axes[1], z_median, 'darkorange',
     f'Константа MAE\nz = {z_median:.4f},  MAE = {mae_med:.4f}'),
]:
    ax.bar(pts_s, Z, color='#95a5a6', alpha=0.8, label='Real z', edgecolor='black')
    ax.axhline(z_const, color=color, linewidth=2.5, linestyle='--', label=label)
    for i in range(len(X)):
        r = Z[i] - z_const
        ax.annotate('', xy=(i, z_const), xytext=(i, Z[i]),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
        ax.text(i + 0.12, (Z[i] + z_const) / 2, f'{r:+.2f}', fontsize=8, color='red')
    ax.set_ylabel('Z'); ax.set_title(label); ax.legend(); ax.grid(True, alpha=0.3)
plt.tight_layout()
save('05_constant_models.png')

# --- 6. Сравнение линий уровня ---
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
fig.suptitle('Сравнение моделей — линии уровня (вариант 6)', fontsize=14, fontweight='bold')
for ax, Zm, title, cmap, preds in [
    (axes[0], Zg_gauss, f'Gaussiana  MSE={0.5*np.mean(resid_gauss**2):.4f}',
     'viridis', preds_gauss),
    (axes[1], Zg_par,   f'Paraboloid  MSE={0.5*np.mean(resid_par**2):.4f}',
     'plasma',  preds_par),
]:
    cf = ax.contourf(Xg, Yg, Zm, levels=25, cmap=cmap, alpha=0.9)
    ax.contour(Xg, Yg, Zm, levels=10, colors='white', alpha=0.4, linewidths=0.5)
    ax.scatter(X, Y, c=Z, s=140, edgecolors='black', linewidths=1.5, cmap=cmap,
               vmin=Zm.min(), vmax=Zm.max(), zorder=5)
    for i in range(len(X)):
        ax.annotate(f'z={Z[i]:.2f}\np={preds[i]:.2f}',
                    (X[i]+0.08, Y[i]+0.08), fontsize=7.5, color='white',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.5))
    plt.colorbar(cf, ax=ax, label='Z')
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_title(title); ax.grid(True, alpha=0.2)
plt.tight_layout()
save('06_comparison.png')

print("\nГотово! Все графики сохранены рядом со скриптом.")