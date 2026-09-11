"""Лабораторная работа 3. Линейная регрессия без готовых ML-моделей."""

from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".matplotlib"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA = ROOT.parent / "lab1" / "Student_Performance.csv"
OUT = ROOT / "output"
FIG = OUT / "figures"
TARGET = "Performance Index"
SEED = 42

# 三个模型使用不同的特征组合；第三个模型包含奖金任务中的合成特征
MODELS = {
    "Модель 1": ["Hours Studied", "Sleep Hours", "Sample Question Papers Practiced"],
    "Модель 2": ["Previous Scores", "Extracurricular Activities"],
    "Модель 3": [
        "Hours Studied",
        "Previous Scores",
        "Extracurricular Activities",
        "Sleep Hours",
        "Sample Question Papers Practiced",
        "Study Efficiency",
    ],
}


def gradient_descent(x, y, rate=0.05, steps=30000, eps=1e-10):
    """Минимизация средней суммы квадратов ошибок методом градиентного спуска."""
    # 在特征矩阵前加一列常数，用来学习截距 theta_0
    x = np.column_stack([np.ones(len(x)), x])
    theta = np.zeros(x.shape[1])

    # 手写批量梯度下降，不使用 sklearn、statsmodels 或线性方程求解器
    for step in range(1, steps + 1):
        error = x @ theta - y
        gradient = 2 / len(y) * (x.T @ error)
        new_theta = theta - rate * gradient
        if np.max(np.abs(new_theta - theta)) < eps:
            theta = new_theta
            break
        theta = new_theta
    return theta, step


def predict(x, theta):
    # 预测时使用与训练阶段相同的截距列
    return np.column_stack([np.ones(len(x)), x]) @ theta


def metrics(y, pred):
    # R² 是实验要求的主要指标；RMSE 和 MAE 作为辅助解释
    residual = y - pred
    sse = np.sum(residual**2)
    r2 = 1 - sse / np.sum((y - y.mean()) ** 2)
    return float(r2), float(np.sqrt(np.mean(residual**2))), float(np.mean(np.abs(residual)))


def prepare_model(data, features, train_idx, test_idx):
    part = data[features].copy()

    # 缺失值处理：数值列用中位数，类别列用众数
    for col in part.columns:
        if pd.api.types.is_numeric_dtype(part[col]):
            part[col] = part[col].fillna(part.loc[train_idx, col].median())
        else:
            part[col] = part[col].fillna(part.loc[train_idx, col].mode().iloc[0])

    # 类别特征独热编码，例如 Yes/No 转换为 0/1
    part = pd.get_dummies(part, drop_first=True, dtype=float)
    x_train = part.loc[train_idx].to_numpy(float)
    x_test = part.loc[test_idx].to_numpy(float)

    # 只用训练集的均值和标准差完成标准化，避免测试集信息泄漏
    mean, std = x_train.mean(axis=0), x_train.std(axis=0)
    std[std == 0] = 1
    return (x_train - mean) / std, (x_test - mean) / std, part.columns.tolist()


def make_eda_plots(data):
    # 一张图集中展示直方图、箱线图、类别频数和相关矩阵
    numeric = [
        "Hours Studied",
        "Previous Scores",
        "Sleep Hours",
        "Sample Question Papers Practiced",
        TARGET,
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    axes[0, 0].hist(data[TARGET], bins=20, color="#3568A8", edgecolor="white")
    axes[0, 0].axvline(data[TARGET].mean(), color="#B13F45", label=f"Среднее = {data[TARGET].mean():.2f}")
    axes[0, 0].set(title="Распределение индекса успеваемости", xlabel=TARGET, ylabel="Частота")
    axes[0, 0].legend()

    axes[0, 1].boxplot([data[c] for c in numeric], tick_labels=["Часы", "Прошлые\nбаллы", "Сон", "Работы", "Индекс"])
    axes[0, 1].set_title("Разброс числовых признаков")

    counts = data["Extracurricular Activities"].value_counts().sort_index()
    axes[1, 0].bar(counts.index, counts.values, color="#4C9A8A")
    axes[1, 0].set(title="Внеучебная активность", xlabel="Участие", ylabel="Количество")

    corr = data[numeric].corr().to_numpy()
    image = axes[1, 1].imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    short = ["Hours", "Previous", "Sleep", "Papers", "Index"]
    axes[1, 1].set_xticks(range(len(short)), short, rotation=35, ha="right")
    axes[1, 1].set_yticks(range(len(short)), short)
    axes[1, 1].set_title("Корреляционная матрица")
    for i in range(len(short)):
        for j in range(len(short)):
            axes[1, 1].text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(image, ax=axes[1, 1], fraction=0.046, pad=0.04)

    fig.tight_layout()
    fig.savefig(FIG / "01_eda.png", dpi=180)
    plt.close(fig)


def make_result_plots(results):
    # 比较三种特征组合，并单独展示最佳模型的真实值与预测值
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    names = [r["model"] for r in results]
    r2_values = [r["R2"] for r in results]
    bars = axes[0].bar(names, r2_values, color=["#8CA6C0", "#4C9A8A", "#3568A8"])
    axes[0].set(title="Сравнение моделей", ylabel="R² на тестовой выборке")
    for bar, value in zip(bars, r2_values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value, f"{value:.3f}", ha="center", va="bottom")

    best = max(results, key=lambda item: item["R2"])
    y, pred = best["actual"], best["predicted"]
    low, high = min(y.min(), pred.min()), max(y.max(), pred.max())
    axes[1].scatter(y, pred, s=14, alpha=0.45, color="#3568A8")
    axes[1].plot([low, high], [low, high], "--", color="#B13F45")
    axes[1].set(title=f"{best['model']}: факт и прогноз", xlabel="Фактический индекс", ylabel="Предсказанный индекс")

    fig.tight_layout()
    fig.savefig(FIG / "02_models.png", dpi=180)
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)

    # 读取课程提供的数据；删除完全重复的记录，原始 CSV 保持不变
    raw = pd.read_csv(DATA)
    duplicates = int(raw.duplicated().sum())
    data = raw.drop_duplicates().reset_index(drop=True)
    missing_before = int(data.isna().sum().sum())

    # 奖金任务：构造“学习效率”交互特征
    data["Study Efficiency"] = data["Hours Studied"] * data["Previous Scores"] / 100

    # 固定随机种子，按 80%/20% 划分训练集和测试集
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(data))
    cut = int(len(data) * 0.8)
    train_idx, test_idx = order[:cut], order[cut:]
    y_train = data.loc[train_idx, TARGET].to_numpy(float)
    y_test = data.loc[test_idx, TARGET].to_numpy(float)

    results, coefficient_tables = [], []
    for model, features in MODELS.items():
        x_train, x_test, encoded_names = prepare_model(data, features, train_idx, test_idx)
        theta, steps = gradient_descent(x_train, y_train)
        pred = predict(x_test, theta)
        r2, rmse, mae = metrics(y_test, pred)

        results.append({
            "model": model,
            "features": ", ".join(features),
            "R2": r2,
            "RMSE": rmse,
            "MAE": mae,
            "iterations": steps,
            "actual": y_test,
            "predicted": pred,
        })
        coefficient_tables.append(pd.DataFrame({
            "model": model,
            "feature": ["intercept", *encoded_names],
            "coefficient": theta,
        }))

    # 保存答辩时可核对的统计量、指标、系数和预测结果
    data.drop(columns=["Study Efficiency"]).describe().T.to_csv(OUT / "summary_statistics.csv", encoding="utf-8-sig")
    pd.DataFrame([
        {k: v for k, v in r.items() if k not in {"actual", "predicted"}}
        for r in results
    ]).to_csv(OUT / "model_metrics.csv", index=False, encoding="utf-8-sig")
    pd.concat(coefficient_tables).to_csv(OUT / "coefficients.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame({
        "actual": y_test,
        **{r["model"]: r["predicted"] for r in results},
    }).to_csv(OUT / "test_predictions.csv", index=False, encoding="utf-8-sig")

    make_eda_plots(data)
    make_result_plots(results)

    print(f"Исходных строк: {len(raw)}; удалено дубликатов: {duplicates}")
    print(f"Пропусков до обработки: {missing_before}")
    print(f"Обучающая выборка: {len(train_idx)}; тестовая выборка: {len(test_idx)}")
    for r in results:
        print(f"{r['model']}: R²={r['R2']:.4f}, RMSE={r['RMSE']:.4f}, MAE={r['MAE']:.4f}")


if __name__ == "__main__":
    main()
