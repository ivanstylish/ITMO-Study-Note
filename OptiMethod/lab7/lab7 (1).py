import os
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def save_fig(name):
    path = os.path.join(SCRIPT_DIR, name)
    plt.savefig(path, dpi=120)
    plt.close()
    print(f"Сохранён: {path}")


def f(x, y):
    return 1e-2 * (8 * x ** 2 + 2 * x * y + 43 * x + 10 * y + 15)


def grad_f(x, y):
    dfdx = 1e-2 * (16 * x + 2 * y + 43)
    dfdy = 1e-2 * (2 * x + 10)
    return np.array([dfdx, dfdy])


print("=" * 60)
print("ЗАДАНИЕ 1")
print("=" * 60)
print("f(x,y) = 10^-2*(8x^2 + 2xy + 43x + 10y + 15)")
print("Область: x in [-20,20], y in [-50,50]")
print()
print("Стационарные точки:")
print("  df/dx = 10^-2*(16x + 2y + 43) = 0")
print("  df/dy = 10^-2*(2x + 10) = 0")
print("  Из df/dy=0: x = -5")
print("  Из df/dx=0 при x=-5: y = 18.5")
x_saddle, y_saddle = -5.0, 18.5
print(f"  Стационарная точка: ({x_saddle}, {y_saddle})")
print()

# 驻点/海森矩阵分析，解析证明鞍点的存在
print("Матрица Гессе:")
H = np.array([[0.16, 0.02], [0.02, 0.0]])
D1 = H[0, 0]
D2 = np.linalg.det(H)
print(f"  H = 10^-2 * [[16,2],[2,0]],  D1={D1},  D2={D2:.6f} < 0")
print("  Гессиан знаконеопределён => СЕДЛОВАЯ ТОЧКА. Локальных экстремумов нет.")
print()
print("Глобальный минимум на границе:")
x_gmin, y_gmin = 57.0 / 16.0, -50.0
f_gmin = f(x_gmin, y_gmin)
print(f"  y=-50: df/dx=0 => x=57/16=3.5625, f(3.5625,-50) = {f_gmin:.6f}")
print(f"  Глобальный минимум: ({x_gmin:.4f}, {y_gmin}), f = {f_gmin:.6f}")
print()

x_vals = np.linspace(-20, 20, 400)
y_vals = np.linspace(-50, 50, 400)
X_grid, Y_grid = np.meshgrid(x_vals, y_vals)
Z_grid = f(X_grid, Y_grid)

fig, ax = plt.subplots(figsize=(9, 7))
cs = ax.contourf(X_grid, Y_grid, Z_grid, levels=45, cmap='coolwarm', alpha=0.65)
ax.contour(X_grid, Y_grid, Z_grid, levels=35, colors='black', linewidths=0.5, alpha=0.5)
plt.colorbar(cs, ax=ax, label='f(x,y)')
ax.plot(x_saddle, y_saddle, 'r*', markersize=16, label=f'Седловая ({x_saddle},{y_saddle})', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=13, label=f'Глоб. минимум ({x_gmin:.2f},{y_gmin})', zorder=5)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title('Задание 1. Линии уровня f(x,y), вариант 6', fontsize=13)
ax.legend(fontsize=10)
plt.tight_layout()
save_fig('task1_contours.png')

## 任务二 标准的梯度下降函数
print("=" * 60)
print("ЗАДАНИЕ 2")
print("=" * 60)

x0, y0 = 5.0, 20.0  # начальная точка
lr_gd = 0.3  # шаг (learning rate) 步长
eps_stop = 1e-15  # порог для критерия останова 停止准则的阙值
print(f"Начальное приближение: ({x0}, {y0})")
print(f"Скорость обучения: alpha = {lr_gd}")
print(f"Критерий останова: |f(x_k+1) - f(x_k)| < {eps_stop}")
print()


# 梯度下降法
def gradient_descent(x_init, y_init, lr, n_max, eps):
    x, y = x_init, y_init
    history = [(x, y)]
    n_stop = n_max
    for i in range(n_max):
        g = grad_f(x, y)
        xn = x - lr * g[0]
        yn = y - lr * g[1]
        history.append((xn, yn))
        if abs(f(xn, yn) - f(x, y)) < eps:
            n_stop = i + 1
            x, y = xn, yn
            break
        x, y = xn, yn
    return np.array(history), n_stop


hist_gd, n_iters_used = gradient_descent(x0, y0, lr_gd, 200, eps_stop)
print(f"--- 2.1: Градиентный спуск ---") # 标准梯度下降
print(f"Итераций: {n_iters_used}, финал: ({hist_gd[-1, 0]:.4f}, {hist_gd[-1, 1]:.4f})")
print(f"f(финал) = {f(hist_gd[-1, 0], hist_gd[-1, 1]):.6f}")
print(f"Расстояние до седловой: {np.sqrt((hist_gd[-1, 0] - x_saddle) ** 2 + (hist_gd[-1, 1] - y_saddle) ** 2):.4f}")
print()

fig, ax = plt.subplots(figsize=(9, 7))
ax.contourf(X_grid, Y_grid, Z_grid, levels=45, cmap='coolwarm', alpha=0.5)
ax.contour(X_grid, Y_grid, Z_grid, levels=35, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_gd[:, 0], hist_gd[:, 1], 'r-o', markersize=2, linewidth=1.2, label=f'ГС ({n_iters_used} итер.)')
ax.plot(x0, y0, 'bs', markersize=11, label=f'Старт ({x0},{y0})', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=16, label=f'Седловая ({x_saddle},{y_saddle})', zorder=5)
ax.set_xlim(-20, 20)
ax.set_ylim(-50, 50)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title(f'Задание 2.1. ГС к седловой (alpha={lr_gd}, eps={eps_stop})', fontsize=12)
ax.legend(fontsize=10)
plt.tight_layout()
save_fig('task2_1_gd_to_saddle.png')

# 自适应梯度算法！！
def adagrad(x_init, y_init, lr, n_iter, eps_ada=1e-8):
    pos = np.array([x_init, y_init], dtype=float)
    G = np.zeros(2)
    history = [pos.copy()]

    for _ in range(n_iter):
        g = grad_f(pos[0], pos[1])  # Вектор градиента
        G = G + g ** 2  # Накопление квадрата градиента 梯度平方的乘积
        step = lr / np.sqrt(G + eps_ada)  # Вычисление шага 步长计算
        pos = pos - step * g  # Векторное обновление x и y 向量x，y更新
        history.append(pos.copy())

    return np.array(history)


lr_ada = 0.3
hist_ada = adagrad(x0, y0, lr_ada, n_iters_used)
print(f"--- 2.2: Adagrad ---") # 自定义 Adagrad 算法
print(f"G_{{k+1}} = G_k + (grad_f(x_k))^2   (поэлементно)")
print(f"x_{{k+1}} = x_k - (alpha/sqrt(G_{{k+1}}+eps)) * grad_f(x_k)")
print(f"alpha={lr_ada}, eps_ada=1e-8, итераций={n_iters_used}")
print(f"Финал: ({hist_ada[-1, 0]:.4f}, {hist_ada[-1, 1]:.4f}), f={f(hist_ada[-1, 0], hist_ada[-1, 1]):.6f}")
print(f"f глобального минимума = {f_gmin:.6f}")
print()

fig, ax = plt.subplots(figsize=(9, 7))
ax.contourf(X_grid, Y_grid, Z_grid, levels=45, cmap='coolwarm', alpha=0.5)
ax.contour(X_grid, Y_grid, Z_grid, levels=35, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_gd[:, 0], hist_gd[:, 1], 'b-o', markersize=2, linewidth=1.0, label='ГС (к седловой)', alpha=0.7)
ax.plot(hist_ada[:, 0], hist_ada[:, 1], 'r-o', markersize=2, linewidth=1.4, label=f'Adagrad alpha={lr_ada}')
ax.plot(x0, y0, 'bs', markersize=11, label=f'Старт ({x0},{y0})', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=16, label='Седловая', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=13, label='Глоб. минимум', zorder=5)
ax.set_xlim(-20, 20)
ax.set_ylim(-50, 50)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title('Задание 2.2. Adagrad преодолевает седловую точку', fontsize=12) # 预测鞍点
ax.legend(fontsize=10)
plt.tight_layout()
save_fig('task2_2_adagrad.png')

x_lo, x_hi = -15.0, 10.0
y_lo, y_hi = -10.0, 25.0
x_zoom = np.linspace(x_lo, x_hi, 300)
y_zoom = np.linspace(y_lo, y_hi, 300)
Xz, Yz = np.meshgrid(x_zoom, y_zoom)
Zz = f(Xz, Yz)

# --- ИДЕАЛЬНЫЕ ГИПЕРПАРАМЕТРЫ --- 理想超参数
# Чтобы получить пилу (прыжки через овраг), нужен огромный шаг
lr_saw = 12.0
# Для плавного скольжения по дну оврага - маленький шаг
lr_smooth = 1.5

hist_saw    = adagrad(x0, y0, lr_saw, n_iters_used, eps_ada=1e-8)
hist_smooth = adagrad(x0, y0, lr_smooth, n_iters_used, eps_ada=1e-8)

print(f"--- 2.3: Область [{x_lo},{x_hi}]x[{y_lo},{y_hi}] ---") # 超参数影响分析 (Saw-tooth vs Smooth)
print(f"Пилообразная: alpha={lr_saw}")
print(f"Плавная:      alpha={lr_smooth}")
print()

fig, axes = plt.subplots(1, 2, figsize=(18, 6))

x_lo, x_hi = -15.0, 10.0
y_lo, y_hi = -10.0, 25.0
x_zoom = np.linspace(x_lo, x_hi, 300)
y_zoom = np.linspace(y_lo, y_hi, 300)
Xz, Yz = np.meshgrid(x_zoom, y_zoom)
Zz = f(Xz, Yz)

# Большой шаг вызывает "пилу" (прыжки через овраг)
lr_saw = 12.0
# Маленький шаг обеспечивает плавный спуск по склону
lr_smooth = 1.5

hist_saw = adagrad(x0, y0, lr_saw, n_iters_used, eps_ada=1e-8)
hist_smooth = adagrad(x0, y0, lr_smooth, n_iters_used, eps_ada=1e-8)

print(f"--- 2.3: Область [{x_lo},{x_hi}]x[{y_lo},{y_hi}] ---")
print(f"Пилообразная: alpha={lr_saw}")
print(f"Плавная:      alpha={lr_smooth}")
print()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

for ax, hist, title, style in zip(
        axes,
        [hist_saw, hist_smooth],
        [f'Adagrad alpha={lr_saw}\n(пилообразная ломаная)',
         f'Adagrad alpha={lr_smooth}\n(плавное направление)'],
        ['r-o', 'g-o']  # Красный для пилы, зеленый для плавного спуска
):
    ax.contourf(Xz, Yz, Zz, levels=40, cmap='coolwarm', alpha=0.55)
    ax.contour(Xz, Yz, Zz, levels=30, colors='black', linewidths=0.4, alpha=0.4)

    # Отрисовка траектории
    ax.plot(hist[:, 0], hist[:, 1], style, markersize=3, linewidth=1.5)

    # Отрисовка точек
    ax.plot(x0, y0, 'bs', markersize=10, zorder=5, label=f'Старт ({x0},{y0})')
    ax.plot(x_saddle, y_saddle, 'r*', markersize=14, zorder=5, label='Седловая')

    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)
    ax.set_xlabel('x', fontsize=11)
    ax.set_ylabel('y', fontsize=11)
    ax.set_title(title, fontsize=12)
    ax.legend(fontsize=10, loc='lower right')

plt.suptitle('Задание 2.3. Иллюстрация гиперпараметров Adagrad', fontsize=14, fontweight='bold')
plt.tight_layout()
save_fig('task2_3_hyperparams.png')

print(f"--- 2.4: PyTorch Adagrad ---") # PyTorch 官方实现验证
solution = torch.tensor([[float(x0)], [float(y0)]], requires_grad=True, dtype=torch.float64)
# 启用自动微分 requires_grad=True — включить автодифференцирование
optimizer_torch = torch.optim.Adagrad([solution], lr=lr_ada)
# 官方Adagrad实现 Встроенная реализация Adagrad в PyTorch
trace_torch = []
for i in range(n_iters_used):
    optimizer_torch.zero_grad()
    # 清除上次梯度 Обнуление градиентов перед каждым шагом
    x_t = solution[0]
    y_t = solution[1]
    score = 1e-2 * (8 * x_t ** 2 + 2 * x_t * y_t + 43 * x_t + 10 * y_t + 15)
    score.backward()
    # 反向传播，自动计算 ∂score/∂solution Вычисляет производные через backprop автоматически
    trace_torch.append(solution.clone().detach().numpy())
    optimizer_torch.step()
    # 按选定算法更新参数 Обновление параметров по выбранному алгоритму
trace_torch = np.array(trace_torch)
hist_torch = trace_torch[:, :, 0]
print(f"Финал: ({hist_torch[-1, 0]:.4f}, {hist_torch[-1, 1]:.4f}), f={f(hist_torch[-1, 0], hist_torch[-1, 1]):.6f}")
print()

fig, ax = plt.subplots(figsize=(9, 7))
ax.contourf(Xz, Yz, Zz, levels=40, cmap='coolwarm', alpha=0.55)
ax.contour(Xz, Yz, Zz, levels=30, colors='black', linewidths=0.4, alpha=0.4)
ax.plot(hist_torch[:, 0], hist_torch[:, 1], 'r-o', markersize=2, linewidth=1.4,
        label=f'PyTorch Adagrad (alpha={lr_ada})')
ax.plot(x0, y0, 'bs', markersize=11, label=f'Старт ({x0},{y0})', zorder=5)
ax.plot(x_saddle, y_saddle, 'r*', markersize=16, label='Седловая', zorder=5)
ax.plot(x_gmin, y_gmin, 'g^', markersize=13, label='Глоб. минимум', zorder=5)
ax.set_xlim(x_lo, x_hi)
ax.set_ylim(y_lo, y_hi)
ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title(f'Задание 2.4. PyTorch Adagrad (alpha={lr_ada}, {n_iters_used} итер.)', fontsize=12)
ax.legend(fontsize=10)
plt.tight_layout()
save_fig('task2_4_pytorch_adagrad.png')


### 任务三
print()
print("=" * 60)
print("ЗАДАНИЕ 3: Нейронная сеть — матчи АПЛ (results.csv)") # 读取csv文件内容
print("=" * 60)

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.csv')
df_apl = pd.read_csv(DATA_PATH, encoding='latin1')
print(f"Датасет: {df_apl.shape[0]} матчей, {df_apl.shape[1]} столбцов")
print(f"Сезоны: {df_apl['Season'].min()} — {df_apl['Season'].max()}")

required_cols = ['HS', 'AS', 'HST', 'AST', 'HC', 'AC', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR',
                 'HTR', 'HTHG', 'HTAG', 'FTR', 'HomeTeam', 'AwayTeam']
df_apl = df_apl.dropna(subset=required_cols).copy()
print(f"После удаления пропусков: {df_apl.shape[0]} матчей (>=100 OK)")
print(f"Целевой признак FTR: {df_apl['FTR'].value_counts().to_dict()}")
print()

numeric_features = ['HTHG', 'HTAG', 'HS', 'AS', 'HST', 'AST', 'HC', 'AC', 'HF', 'AF', 'HY', 'AY', 'HR', 'AR']
cat_features = ['HTR', 'HomeTeam', 'AwayTeam']

df_enc = df_apl.copy()
le_dict = {}
for col in cat_features:
    le = LabelEncoder() 
    # 类别特征编码
    # Нейронные сети могут обрабатывать только числа, а не текст.
    df_enc[col] = le.fit_transform(df_enc[col].astype(str))
    le_dict[col] = le

feature_cols = numeric_features + cat_features
print(f"Признаки:  {feature_cols}")

le_target = LabelEncoder()
df_enc['FTR_enc'] = le_target.fit_transform(df_enc['FTR'])
print(f"Классы: {dict(zip(le_target.classes_, range(len(le_target.classes_))))}")
print()

X = df_enc[feature_cols].values.astype(np.float32)
y = df_enc['FTR_enc'].values.astype(np.int64)
scaler = StandardScaler() # 标准化特征 Стандартизировать числовые характеристики
# 加快梯度下降的收敛速度。
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long)
X_test_t = torch.tensor(X_test, dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.long)
train_dataset = TensorDataset(X_train_t, y_train_t)
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

n_features_nn = X_train.shape[1]
n_classes = 3

# 深度学习模块定义了深度学习中的Полносвязный слой（nn.Linear）
# 和非线性激活函数нелинейные функции активации (nn)（nn.ReLU） Класс нейронной сети
class MatchNet(nn.Module):
    def __init__(self, n_in, n_out):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, 128), nn.ReLU(),
            nn.Linear(128, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, n_out)
            # 四层结构
        )

    def forward(self, x): return self.net(x)


# 优化器封装 (Optimizer Integration)，自定义优化
class MyAdagrad(torch.optim.Optimizer):
    def __init__(self, params, lr=0.01, eps=1e-8):
        defaults = dict(lr=lr, eps=eps)
        super().__init__(params, defaults)

    def step(self, closure=None):
        loss = None
        if closure is not None: loss = closure()
        for group in self.param_groups:
            lr = group['lr']
            eps = group['eps']
            for p in group['params']:
                if p.grad is None: continue
                g = p.grad.data
                state = self.state[p]
                if 'G' not in state:
                    state['G'] = torch.zeros_like(p.data)
                G = state['G']
                G.add_(g ** 2)
                step_size = lr / (G.sqrt() + eps)
                p.data.addcmul_(step_size, g, value=-1)
        return loss

# 如何预测和分类
# 训练与损失计算
def train_model(model, optimizer, n_epochs=60):
    criterion = nn.CrossEntropyLoss() 
    # 用于多分类任务的最小化目标 。 Цель минимизации для задач многоклассовой классификации.
    loss_history = []
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(X_batch), y_batch)
            loss.backward()
            # 自动完成全部反向传播计算。loss.backward() в PyTorch автоматически вычисляет все градиенты.
            optimizer.step()
            epoch_loss += loss.item()
        loss_history.append(epoch_loss / len(train_loader))
    return loss_history


def evaluate(model, X_t, y_t): # 评估
    model.eval()
    with torch.no_grad():
        preds = model(X_t).argmax(dim=1).numpy() # 预测逻辑（Победа хозяев, ничья, победа гостей）
    return accuracy_score(y_t.numpy(), preds), f1_score(y_t.numpy(), preds, average='weighted')
    # 计算预测正确的比赛占总比赛的比例

n_epochs = 60

print("--- MyAdagrad ---")
torch.manual_seed(42)
model_my = MatchNet(n_features_nn, n_classes)
opt_my = MyAdagrad(model_my.parameters(), lr=0.05)
loss_my = train_model(model_my, opt_my, n_epochs)
acc_my, f1_my = evaluate(model_my, X_test_t, y_test_t)
print(f"MyAdagrad       — Accuracy: {acc_my:.4f}, F1: {f1_my:.4f}")
# 用于评估模型在测试集上的泛化能力 。 Используется для оценки способности модели к обобщению на тестовом наборе данных.

print("--- PyTorch Adagrad ---")
torch.manual_seed(42)
model_pt = MatchNet(n_features_nn, n_classes)
opt_pt = torch.optim.Adagrad(model_pt.parameters(), lr=0.05)
loss_pt = train_model(model_pt, opt_pt, n_epochs)
acc_pt, f1_pt = evaluate(model_pt, X_test_t, y_test_t)
print(f"PyTorch Adagrad — Accuracy: {acc_pt:.4f}, F1: {f1_pt:.4f}")

delta = abs(acc_my - acc_pt)
print(f"Разница Accuracy: {delta:.4f} — {'идентичный' if delta < 0.01 else 'близкий'} результат")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].plot(loss_my, label='MyAdagrad', color='steelblue', linewidth=2.0)
axes[0].plot(loss_pt, label='PyTorch Adagrad', color='darkorange', linewidth=2.0, linestyle='--')
axes[0].set_xlabel('Эпоха', fontsize=12)
axes[0].set_ylabel('CrossEntropyLoss', fontsize=11) # 损失函数
axes[0].set_title('Задание 3. Кривые обучения (АПЛ, FTR)', fontsize=12)
axes[0].legend(fontsize=11)
axes[0].grid(True, alpha=0.4)

methods = ['MyAdagrad', 'PyTorch\nAdagrad']
accs = [acc_my, acc_pt]
f1s = [f1_my, f1_pt]
x_pos = np.arange(len(methods))
width = 0.32
axes[1].bar(x_pos - width / 2, accs, width, label='Accuracy', color='steelblue', alpha=0.85)
axes[1].bar(x_pos + width / 2, f1s, width, label='F1 (weighted)', color='coral', alpha=0.85)
for i, (a, fi) in enumerate(zip(accs, f1s)):
    axes[1].text(i - width / 2, a + 0.005, f'{a:.3f}', ha='center', va='bottom', fontsize=10)
    axes[1].text(i + width / 2, fi + 0.005, f'{fi:.3f}', ha='center', va='bottom', fontsize=10)
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(methods, fontsize=11)
axes[1].set_ylim(0, 1)
axes[1].set_title('Задание 3. Метрики на тестовой выборке', fontsize=12)
axes[1].legend(fontsize=11)
axes[1].grid(True, axis='y', alpha=0.4)
plt.tight_layout()
save_fig('task3_nn_results.png')
print("Все задания выполнены.")