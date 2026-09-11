"""Краткая версия программы для защиты лабораторной работы."""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 1. 读取并清洗数据：删除重复行，类别特征 Yes/No 编码为 1/0
data = pd.read_csv(ROOT.parent / "lab1" / "Student_Performance.csv")
data = data.drop_duplicates().reset_index(drop=True)
data["Extracurricular Activities"] = data["Extracurricular Activities"].map({"No": 0, "Yes": 1})

# 缺失值处理：数值列使用中位数（本数据集实际没有缺失值）
data = data.fillna(data.median(numeric_only=True))

# 2. 奖金任务：构造“学习效率”合成特征
data["Study Efficiency"] = data["Hours Studied"] * data["Previous Scores"] / 100

# 3. 固定随机种子，按 80%/20% 划分训练集和测试集
rng = np.random.default_rng(42)
order = rng.permutation(len(data))
cut = int(0.8 * len(data))
train, test = order[:cut], order[cut:]
y_train = data.loc[train, "Performance Index"].to_numpy(float)
y_test = data.loc[test, "Performance Index"].to_numpy(float)


def prepare(features):
    """Стандартизация признаков по параметрам обучающей выборки."""
    x = data[features].to_numpy(float)
    mean, std = x[train].mean(axis=0), x[train].std(axis=0)
    std[std == 0] = 1
    # 只用训练集参数标准化，避免测试集信息泄漏
    return (x[train] - mean) / std, (x[test] - mean) / std


def fit(x, y, rate=0.05, steps=30000):
    """Ручной градиентный спуск для минимизации квадратичной ошибки."""
    # 添加截距列并初始化回归系数
    x = np.column_stack([np.ones(len(x)), x])
    theta = np.zeros(x.shape[1])
    # 核心公式：theta = theta - 学习率 * 损失函数梯度
    for _ in range(steps):
        gradient = 2 / len(y) * x.T @ (x @ theta - y)
        new_theta = theta - rate * gradient
        if np.max(np.abs(new_theta - theta)) < 1e-10:
            theta = new_theta
            break
        theta = new_theta
    return theta


def evaluate(features):
    """Обучение модели и расчет R², RMSE и MAE."""
    x_train, x_test = prepare(features)
    theta = fit(x_train, y_train)
    pred = np.column_stack([np.ones(len(x_test)), x_test]) @ theta
    error = y_test - pred
    # R² 越接近 1，模型对数据变化的解释能力越强
    r2 = 1 - np.sum(error**2) / np.sum((y_test - y_test.mean()) ** 2)
    rmse = np.sqrt(np.mean(error**2))
    mae = np.mean(np.abs(error))
    return float(r2), float(rmse), float(mae), pred


# 4. 三个模型分别考察学习行为、历史成绩和全部特征
models = {
    "Модель 1": ["Hours Studied", "Sleep Hours", "Sample Question Papers Practiced"],
    "Модель 2": ["Previous Scores", "Extracurricular Activities"],
    "Модель 3": [
        "Hours Studied", "Previous Scores", "Extracurricular Activities",
        "Sleep Hours", "Sample Question Papers Practiced", "Study Efficiency",
    ],
}

results = {name: evaluate(features) for name, features in models.items()}
print(data.describe().T)
for name, (r2, rmse, mae, _) in results.items():
    print(f"{name}: R²={r2:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}")

# 5. 可视化统计分布和三种模型的 R²
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(data["Performance Index"], bins=20, color="#3568A8")
axes[0].set(title="Распределение Performance Index", xlabel="Индекс", ylabel="Частота")
axes[1].bar(results.keys(), [value[0] for value in results.values()], color="#4C9A8A")
axes[1].set(title="Сравнение моделей", ylabel="R²")
fig.tight_layout()
fig.savefig(ROOT / "output" / "defense_summary.png", dpi=180)
