import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


def f(x, y):
    return 1e-2 * (8*x**2 + 2*x*y + 43*x + 10*y + 15)

def grad_f(x, y):
    dfdx = 1e-2 * (16*x + 2*y + 43)
    dfdy = 1e-2 * (2*x + 10)
    return np.array([dfdx, dfdy])

print("=" * 60)
print("ЗАДАНИЕ 1: Аналитическое исследование функции")
print("=" * 60)
print("f(x,y) = 10^-2 * (8x^2 + 2xy + 43x + 10y + 15)")
print("Область: x in [-20,20], y in [-50,50]")
print()

print("--- Нахождение стационарных точек ---")
print("df/dx = 10^-2 * (16x + 2y + 43) = 0")
print("df/dy = 10^-2 * (2x + 10) = 0")
print("Из df/dy=0: x = -5")
print("Подставляя в df/dx=0: 16*(-5) + 2y + 43 = 0 => y = 18.5")
x_saddle, y_saddle = -5.0, 18.5
print(f"Стационарная точка: ({x_saddle}, {y_saddle})")
print()

print("--- Исследование типа стационарной точки (матрица Гессе) ---")
print("d2f/dx2  = 10^-2 * 16 = 0.16")
print("d2f/dy2  = 10^-2 * 0  = 0.0")
print("d2f/dxdy = 10^-2 * 2  = 0.02")
H = np.array([[0.16, 0.02], [0.02, 0.0]])
D1 = H[0, 0]
D2 = np.linalg.det(H)
print(f"D1 = {D1}, D2 = det(H) = {D2:.6f}")
print("D2 < 0 => матрица Гессе неопределённая => СЕДЛОВАЯ ТОЧКА")
print(f"Седловая точка: ({x_saddle}, {y_saddle}), f = {f(x_saddle, y_saddle):.6f}")
print("Локальных экстремумов нет.")
print()

print("--- Поиск глобального минимума на границе области ---")
x_gmin = 57.0 / 16.0
y_gmin = -50.0
f_gmin = f(x_gmin, y_gmin)
print("Ребро y=-50: f(x,-50) = 10^-2*(8x^2 - 57x - 485)")
print("df/dx = 10^-2*(16x - 57) = 0 => x = 57/16 = 3.5625 (входит в [-20,20])")
print(f"Глобальный минимум: ({x_gmin:.4f}, {y_gmin}), f = {f_gmin:.6f}")
print()

x_vals = np.linspace(-20, 20, 400)
y_vals = np.linspace(-50, 50, 400)
X_grid, Y_grid = np.meshgrid(x_vals, y_vals)
Z_grid = f(X_grid, Y_grid)

fig, ax = plt.subplots(figsize=(8, 6))
levels = np.linspace(Z_grid.min(), Z_grid.max(), 40)
cs = ax.contourf(X_grid, Y_grid, Z_grid, levels=levels, cmap='coolwarm', alpha=0.6)
ax.contour(X_grid, Y_grid, Z_grid, levels=30, colors='black', linewidths=0.5, alpha=0.5)
plt.colorbar(cs, ax=ax)
ax.plot(x_saddle, y_saddle, 'r*', markersize=14, label=f'Седловая точка ({x_saddle},{y_saddle})', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=12, label=f'Глобальный минимум ({x_gmin:.2f},{y_gmin})', zorder=5)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Линии уровня f(x,y), вариант 6')
ax.legend()
plt.tight_layout()
plt.savefig('task1_contours.png', dpi=120)
plt.close()
print("График Task 1 сохранён: task1_contours.png")


# ============================================================
# ЗАДАНИЕ 2: Градиентный спуск и эвристики
# ============================================================

print()
print("=" * 60)
print("ЗАДАНИЕ 2")
print("=" * 60)

x0, y0 = -5.0, 40.0
lr_gd = 0.3
eps = 1e-5
n_target = 100

print("--- 2.1: Обычный градиентный спуск к седловой точке ---")
print(f"Начальное приближение: ({x0}, {y0})")
print(f"Скорость обучения: {lr_gd}")
print(f"Критерий останова: |f(x_k+1) - f(x_k)| < {eps}")


def gradient_descent(x_init, y_init, lr, n_iter, eps=None):
    x, y = x_init, y_init
    history = [(x, y)]
    for i in range(n_iter):
        g = grad_f(x, y)
        x_new = x - lr * g[0]
        y_new = y - lr * g[1]
        history.append((x_new, y_new))
        if eps is not None and abs(f(x_new, y_new) - f(x, y)) < eps:
            print(f"Критерий останова выполнен на итерации {i+1}")
            x, y = x_new, y_new
            break
        x, y = x_new, y_new
    return np.array(history)


hist_gd = gradient_descent(x0, y0, lr_gd, n_target, eps)
n_iters_used = len(hist_gd) - 1
print(f"Итераций выполнено: {n_iters_used}")
print(f"Финальная точка: ({hist_gd[-1,0]:.4f}, {hist_gd[-1,1]:.4f})")
print(f"f = {f(hist_gd[-1,0], hist_gd[-1,1]):.6f}")
print(f"Седловая точка: ({x_saddle}, {y_saddle}), f = {f(x_saddle, y_saddle):.6f}")
print()

fig, ax = plt.subplots(figsize=(8, 6))
ax.contourf(X_grid, Y_grid, Z_grid, levels=40, cmap='coolwarm', alpha=0.5)
ax.contour(X_grid, Y_grid, Z_grid, levels=30, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_gd[:, 0], hist_gd[:, 1], 'r-o', markersize=2, linewidth=1.2, label=f'ГС ({n_iters_used} итер.)')
ax.plot(x0, y0, 'bs', markersize=10, label='Начало', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=14, label='Седловая точка', zorder=5)
ax.set_xlim(-20, 20)
ax.set_ylim(-50, 50)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title(f'Задание 2.1: Градиентный спуск к седловой точке (lr={lr_gd})')
ax.legend()
plt.tight_layout()
plt.savefig('task2_1_gd_to_saddle.png', dpi=120)
plt.close()
print("График Task 2.1 сохранён: task2_1_gd_to_saddle.png")


# ============================================================
# 2.2: Adagrad (вариант 6 — метод Adagrad)
# Формулы из лекции (слайд 16 ЛК7):
#   G_{k+1} = G_k + (∇f(x_k))^2
#   x_{k+1} = x_k - (alpha / sqrt(G_{k+1} + eps)) * ∇f(x_k)
# ============================================================

print("--- 2.2: Реализация Adagrad (вариант 6) ---")
print("Формулы (из лекции):")
print("  G_{k+1} = G_k + (∇f(x_k))^2  (поэлементно)")
print("  x_{k+1} = x_k - (alpha / sqrt(G_{k+1} + eps)) * ∇f(x_k)")
print()


def adagrad(x_init, y_init, lr, n_iter, eps_ada=1e-8):
    x, y = x_init, y_init
    G = np.zeros(2)
    history = [(x, y)]
    for _ in range(n_iter):
        g = grad_f(x, y)
        G = G + g ** 2
        step = lr / np.sqrt(G + eps_ada)
        x = x - step[0] * g[0]
        y = y - step[1] * g[1]
        history.append((x, y))
    return np.array(history)


lr_ada = 0.3
hist_ada = adagrad(x0, y0, lr_ada, n_iters_used)
print(f"Adagrad за {n_iters_used} итераций:")
print(f"Начальная точка: ({x0}, {y0})")
print(f"Финальная точка: ({hist_ada[-1,0]:.4f}, {hist_ada[-1,1]:.4f})")
print(f"f = {f(hist_ada[-1,0], hist_ada[-1,1]):.6f}")
print(f"f глобального минимума = {f_gmin:.6f}")
print()

fig, ax = plt.subplots(figsize=(8, 6))
ax.contourf(X_grid, Y_grid, Z_grid, levels=40, cmap='coolwarm', alpha=0.5)
ax.contour(X_grid, Y_grid, Z_grid, levels=30, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_gd[:, 0], hist_gd[:, 1], 'b-o', markersize=2, linewidth=1.0, label='ГС (к седловой)', alpha=0.7)
ax.plot(hist_ada[:, 0], hist_ada[:, 1], 'r-o', markersize=2, linewidth=1.2, label=f'Adagrad lr={lr_ada}')
ax.plot(x0, y0, 'bs', markersize=10, label='Начало', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=14, label='Седловая точка', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=12, label='Глоб. минимум', zorder=5)
ax.set_xlim(-20, 20)
ax.set_ylim(-50, 50)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title(f'Задание 2.2: Adagrad преодолевает седловую точку')
ax.legend()
plt.tight_layout()
plt.savefig('task2_2_adagrad.png', dpi=120)
plt.close()
print("График Task 2.2 сохранён: task2_2_adagrad.png")


# ============================================================
# 2.3: Подбор области и гиперпараметров (пилообразная / плавная)
# ============================================================

print("--- 2.3: Подбор области и иллюстрация гиперпараметров ---")

x_lo, x_hi = -7.0, 7.0
y_lo, y_hi = -10.0, 41.0

x_zoom = np.linspace(x_lo, x_hi, 300)
y_zoom = np.linspace(y_lo, y_hi, 300)
Xz, Yz = np.meshgrid(x_zoom, y_zoom)
Zz = f(Xz, Yz)

lr_saw = 0.3
lr_smooth = 0.3

hist_saw = adagrad(x0, y0, lr_saw, n_iters_used, eps_ada=1e-4)
hist_smooth = adagrad(x0, y0, lr_smooth, n_iters_used, eps_ada=1e-8)

print(f"Область отображения: x in [{x_lo},{x_hi}], y in [{y_lo},{y_hi}]")
print(f"Пилообразная ломаная: Adagrad lr={lr_saw}, eps_ada=1e-4")
print(f"Плавное направление: Adagrad lr={lr_smooth}, eps_ada=1e-8")
print()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, hist, title in zip(
    axes,
    [hist_saw, hist_smooth],
    [f'Adagrad lr={lr_saw}, eps=1e-4\n(пилообразная ломаная)',
     f'Adagrad lr={lr_smooth}, eps=1e-8\n(плавное направление)']
):
    ax.contourf(Xz, Yz, Zz, levels=40, cmap='coolwarm', alpha=0.5)
    ax.contour(Xz, Yz, Zz, levels=30, colors='black', linewidths=0.4, alpha=0.4)
    h_clip = hist[(hist[:,0] >= x_lo) & (hist[:,0] <= x_hi) & (hist[:,1] >= y_lo) & (hist[:,1] <= y_hi)]
    ax.plot(hist[:, 0], hist[:, 1], 'r-o', markersize=2, linewidth=1.0)
    ax.plot(x0, y0, 'bs', markersize=10, zorder=5)
    ax.plot(x_saddle, y_saddle, 'r*', markersize=14, zorder=5)
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)

plt.suptitle('Задание 2.3: Иллюстрация гиперпараметров Adagrad')
plt.tight_layout()
plt.savefig('task2_3_hyperparams.png', dpi=120)
plt.close()
print("График Task 2.3 сохранён: task2_3_hyperparams.png")


# ============================================================
# 2.4: Готовая реализация Adagrad из PyTorch
# ============================================================

print("--- 2.4: PyTorch Adagrad ---")

solution = torch.tensor([[x0], [y0]], requires_grad=True, dtype=torch.float64)
optimizer_torch = torch.optim.Adagrad([solution], lr=lr_ada)
trace_torch = []

for i in range(n_iters_used):
    optimizer_torch.zero_grad()
    x_t = solution[0]
    y_t = solution[1]
    score = 1e-2 * (8*x_t**2 + 2*x_t*y_t + 43*x_t + 10*y_t + 15)
    score.backward()
    trace_torch.append(solution.clone().detach().numpy())
    optimizer_torch.step()

trace_torch = np.array(trace_torch)
hist_torch = trace_torch[:, :, 0]

print(f"PyTorch Adagrad за {n_iters_used} итераций:")
print(f"Финальная точка: ({hist_torch[-1,0]:.4f}, {hist_torch[-1,1]:.4f})")
print(f"f = {f(hist_torch[-1,0], hist_torch[-1,1]):.6f}")
print()

fig, ax = plt.subplots(figsize=(8, 6))
ax.contourf(Xz, Yz, Zz, levels=40, cmap='coolwarm', alpha=0.5)
ax.contour(Xz, Yz, Zz, levels=30, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_torch[:, 0], hist_torch[:, 1], 'r-o', markersize=2, linewidth=1.2, label='PyTorch Adagrad')
ax.plot(x0, y0, 'bs', markersize=10, label='Начало', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=14, label='Седловая точка', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=12, label='Глоб. минимум', zorder=5)
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title(f'Задание 2.4: PyTorch Adagrad (lr={lr_ada})')
ax.legend()
plt.tight_layout()
plt.savefig('task2_4_pytorch_adagrad.png', dpi=120)
plt.close()
print("График Task 2.4 сохранён: task2_4_pytorch_adagrad.png")


# ============================================================
# ЗАДАНИЕ 3: Нейронная сеть на датасете student_learning_air_quality
# Задача: классификация performance_label (Low, Medium, High)
# ============================================================

print()
print("=" * 60)
print("ЗАДАНИЕ 3: Нейронная сеть на датасете air_quality")
print("=" * 60)

df = pd.read_csv('student_learning_air_quality.csv')
print(f"Датасет: {df.shape[0]} объектов, {df.shape[1]} признаков")
print(f"Целевой признак: performance_label")
print(f"Классы: {df['performance_label'].value_counts().to_dict()}")
print()

cat_cols = ['day', 'period', 'subject', 'grade', 'air_quality_label']
df_enc = df.copy()
le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df_enc[col])
    le_dict[col] = le

le_target = LabelEncoder()
df_enc['performance_label'] = le_target.fit_transform(df_enc['performance_label'])

drop_cols = ['student_id', 'cognitive_impairment', 'performance_label']
feature_cols = [c for c in df_enc.columns if c not in drop_cols]
print(f"Признаки ({len(feature_cols)}): {feature_cols}")
print()

X = df_enc[feature_cols].values.astype(np.float32)
y = df_enc['performance_label'].values.astype(np.int64)

scaler = StandardScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long)
X_test_t = torch.tensor(X_test, dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.long)

train_dataset = TensorDataset(X_train_t, y_train_t)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

n_features = X_train.shape[1]
n_classes = 3


class StudentNet(nn.Module):
    def __init__(self, n_in, n_out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, n_out)
        )

    def forward(self, x):
        return self.net(x)


# ============================================================
# Собственная реализация Adagrad наследованием от torch.optim.Optimizer
# (интеграция незаметная: тот же интерфейс что у torch.optim.Adagrad)
# Формулы из лекции (слайд 16 ЛК7):
#   G_{k+1} = G_k + (∇f(w_k))^2
#   w_{k+1} = w_k - (alpha / sqrt(G_{k+1} + eps)) * ∇f(w_k)
# ============================================================

class MyAdagrad(torch.optim.Optimizer):
    def __init__(self, params, lr=0.01, eps=1e-8):
        defaults = dict(lr=lr, eps=eps)
        super().__init__(params, defaults)

    def step(self, closure=None):
        loss = None
        if closure is not None:
            loss = closure()
        for group in self.param_groups:
            lr = group['lr']
            eps = group['eps']
            for p in group['params']:
                if p.grad is None:
                    continue
                g = p.grad.data
                state = self.state[p]
                if 'G' not in state:
                    state['G'] = torch.zeros_like(p.data)
                G = state['G']
                G.add_(g ** 2)
                step_size = lr / (G.sqrt() + eps)
                p.data.addcmul_(step_size, g, value=-1)
        return loss


def train_model(model, optimizer, n_epochs=50):
    criterion = nn.CrossEntropyLoss()
    loss_history = []
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            out = model(X_batch)
            loss = criterion(out, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        loss_history.append(epoch_loss / len(train_loader))
    return loss_history


def evaluate(model, X_t, y_t):
    model.eval()
    with torch.no_grad():
        logits = model(X_t)
        preds = logits.argmax(dim=1).numpy()
    acc = accuracy_score(y_t.numpy(), preds)
    f1 = f1_score(y_t.numpy(), preds, average='weighted')
    return acc, f1


n_epochs = 60

print("--- Обучение с собственной реализацией MyAdagrad ---")
model_my = StudentNet(n_features, n_classes)
opt_my = MyAdagrad(model_my.parameters(), lr=0.05)
loss_my = train_model(model_my, opt_my, n_epochs)
acc_my, f1_my = evaluate(model_my, X_test_t, y_test_t)
print(f"MyAdagrad  — Accuracy: {acc_my:.4f}, F1: {f1_my:.4f}")

print("--- Обучение с PyTorch Adagrad ---")
model_pt = StudentNet(n_features, n_classes)
opt_pt = torch.optim.Adagrad(model_pt.parameters(), lr=0.05)
loss_pt = train_model(model_pt, opt_pt, n_epochs)
acc_pt, f1_pt = evaluate(model_pt, X_test_t, y_test_t)
print(f"PyTorch Adagrad — Accuracy: {acc_pt:.4f}, F1: {f1_pt:.4f}")

print()
print("--- Сравнение ---")
print(f"MyAdagrad  : Accuracy={acc_my:.4f}, F1={f1_my:.4f}, финальный loss={loss_my[-1]:.4f}")
print(f"PyTorchAda : Accuracy={acc_pt:.4f}, F1={f1_pt:.4f}, финальный loss={loss_pt[-1]:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(loss_my, label='MyAdagrad', color='blue')
axes[0].plot(loss_pt, label='PyTorch Adagrad', color='orange', linestyle='--')
axes[0].set_xlabel('Эпоха')
axes[0].set_ylabel('Кросс-энтропия (Train)')
axes[0].set_title('Задание 3: Кривые обучения')
axes[0].legend()
axes[0].grid(True)

methods = ['MyAdagrad', 'PyTorch Adagrad']
accs = [acc_my, acc_pt]
f1s = [f1_my, f1_pt]
x_pos = np.arange(len(methods))
width = 0.35
axes[1].bar(x_pos - width/2, accs, width, label='Accuracy', color='steelblue')
axes[1].bar(x_pos + width/2, f1s, width, label='F1 (weighted)', color='coral')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(methods)
axes[1].set_ylim(0, 1)
axes[1].set_title('Задание 3: Метрики на тестовой выборке')
axes[1].legend()
axes[1].grid(True, axis='y')

plt.tight_layout()
plt.savefig('task3_nn_results.png', dpi=120)
plt.close()
print("График Task 3 сохранён: task3_nn_results.png")
print()
print("Все задания выполнены.")
