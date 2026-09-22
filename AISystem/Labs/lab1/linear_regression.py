from pathlib import Path
import sys

import matplotlib
import numpy as np
import pandas as pd

SHOW_PLOTS = "--no-show" not in sys.argv
if not SHOW_PLOTS:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output_explained"
TARGET = "Performance Index"
CATEGORY = "Extracurricular Activities"
NUMERIC = ["Hours Studied", "Previous Scores", "Sleep Hours",
           "Sample Question Papers Practiced"]
INTERACTION = "Study Interaction"
MODELS = {
    "Модель 1": ["Hours Studied", "Sleep Hours", "Sample Question Papers Practiced"],
    "Модель 2": ["Previous Scores", CATEGORY],
    "Модель 3": NUMERIC + [CATEGORY, INTERACTION],
}
SHORT_NAMES = ["Учёба", "Прошлые баллы", "Сон", "Практика", "Индекс"]


def read_and_split():
    # 读取同目录数据，删除完全重复行；目标缺失的行无法监督训练。
    # читаем данные, удаляем дубликаты и строки без целевого значения.
    raw = pd.read_csv(ROOT / "Student_Performance.csv")
    data = raw.drop_duplicates().dropna(subset=[TARGET]).reset_index(drop=True)
    print("1. ДАННЫЕ")
    print("Исходных строк:", len(raw), "Дубликатов:", raw.duplicated().sum())
    print("Строк после очистки:", len(data))
    print("Пропуски до заполнения:\n", data.isna().sum())
    if len(data) < 10:
        raise ValueError("Слишком мало наблюдений для разделения данных.")

    # 固定种子保证可复现；所有模型使用同一份 80%/20% 划分。
    # фиксируем seed; все модели используют одно разбиение 80%/20%.
    order = np.random.default_rng(42).permutation(len(data))
    cut = int(0.8 * len(data))
    train = data.iloc[order[:cut]].copy()
    test = data.iloc[order[cut:]].copy()
    print("Обучение:", len(train), "Тест:", len(test))
    return data, train, test


def preprocess(train, test):
    # 填充值只从训练集计算，避免测试集信息泄漏。
    # параметры заполнения определяем только по обучающей выборке.
    medians = train[NUMERIC].median()
    modes = train[CATEGORY].mode()
    if medians.isna().any() or modes.empty:
        raise ValueError("В обучающей выборке есть полностью пустой признак.")
    for frame in (train, test):
        frame[NUMERIC] = frame[NUMERIC].fillna(medians)
        frame[CATEGORY] = frame[CATEGORY].fillna(modes.iloc[0])
        if not frame[CATEGORY].isin(["Yes", "No"]).all():
            raise ValueError("Ожидаются категории Yes/No.")
        # 合成特征表示学习时间与历史成绩的交互。
        # кодируем Yes/No; добавляем взаимодействие времени и прошлых баллов.
        frame[CATEGORY] = frame[CATEGORY].map({"No": 0, "Yes": 1})
        frame[INTERACTION] = frame["Hours Studied"] * frame["Previous Scores"] / 100
    return train, test


def design_matrices(train, test, features):
    # 测试集使用训练集的参数。
    # z=(x-mean)/std, параметры стандартизации берём из train.
    x_train = train[features].to_numpy(dtype=float)
    x_test = test[features].to_numpy(dtype=float)
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0] = 1
    x_train = (x_train - mean) / std
    x_test = (x_test - mean) / std
    # 第一列全为 1，对应截距 b；预测公式为 y_hat = X @ theta。
    # столбец единиц задаёт свободный член b; прогноз: y_hat = X @ theta.
    return (np.column_stack([np.ones(len(x_train)), x_train]),
            np.column_stack([np.ones(len(x_test)), x_test]))


def fit(x, y, learning_rate=0.05, max_steps=30000):
    # 手写最小二乘优化。MSE=SSE/n，两者的最优系数相同。
    # вручную минимизируем MSE=SSE/n; минимум совпадает с минимумом SSE.
    theta = np.zeros(x.shape[1])
    losses = []
    for step in range(max_steps):
        prediction = x @ theta
        error = prediction - y
        losses.append(float(np.mean(error ** 2)))
        # 梯度 = 2/n * X.T @ error；沿负梯度更新系数。
        # градиент = 2/n * X.T @ error; обновляем коэффициенты против градиента.
        gradient = 2 / len(y) * (x.T @ error)
        new_theta = theta - learning_rate * gradient
        if not np.isfinite(new_theta).all():
            raise ValueError("Расходимость: уменьшите learning_rate.")
        converged = np.max(np.abs(new_theta - theta)) < 1e-10
        theta = new_theta
        if converged:
            break
    if not converged:
        print("Предупреждение: достигнут предел итераций.")
    return theta, losses


def evaluate(actual, prediction):
    # R^2=1-SSE/SST；1 为完美预测，负数表示不如测试集均值基线。
    # R^2=1-SSE/SST; 1 — идеально, R^2<0 — хуже среднего тестовой выборки.
    error = actual - prediction
    sst = np.sum((actual - actual.mean()) ** 2)
    r2 = 1 - np.sum(error ** 2) / sst if sst > 0 else np.nan
    return {"R2": r2, "RMSE": np.sqrt(np.mean(error ** 2)),
            "MAE": np.mean(np.abs(error))}


def save_figure(fig, filename):
    fig.tight_layout()
    fig.savefig(OUTPUT / filename, dpi=160, bbox_inches="tight")
    if not SHOW_PLOTS:
        plt.close(fig)


def plot_statistics(data):
    # 统计表和图包含数量、均值、标准差、最值及四分位数。
    # таблица и графики: count, mean, std, min, max и квартили.
    stats = data[NUMERIC + [TARGET]].describe().T
    stats.to_csv(OUTPUT / "statistics.csv", encoding="utf-8-sig")
    print("\n2. ОПИСАТЕЛЬНАЯ СТАТИСТИКА\n", stats.round(2).to_string())
    fig, ax = plt.subplots(figsize=(13, 4))
    ax.axis("off")
    table = ax.table(cellText=stats.round(2).to_numpy(), rowLabels=SHORT_NAMES,
                     colLabels=stats.columns, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    ax.set_title("Описательная статистика: очищенные данные")
    save_figure(fig, "01_statistics.png")

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes[0, 0].hist(data[TARGET], bins=20, edgecolor="white")
    axes[0, 0].set(title="Распределение успеваемости", xlabel="Индекс", ylabel="Количество")

    axes[0, 1].boxplot([data[c].dropna() for c in NUMERIC + [TARGET]])
    axes[0, 1].set_xticks(range(1, 6))
    axes[0, 1].set_xticklabels(SHORT_NAMES, rotation=15)
    axes[0, 1].set_title("Медианы, квартили и разброс")
    counts = data[CATEGORY].fillna("Пропуск").value_counts()
    axes[1, 0].bar(counts.index, counts.values)
    axes[1, 0].set(title="Внеучебная активность", ylabel="Количество")
    corr = data[NUMERIC + [TARGET]].corr().to_numpy()
    img = axes[1, 1].imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    axes[1, 1].set_xticks(range(5))
    axes[1, 1].set_yticks(range(5))
    axes[1, 1].set_xticklabels(SHORT_NAMES, rotation=30, ha="right")
    axes[1, 1].set_yticklabels(SHORT_NAMES)
    for i in range(5):
        for j in range(5):
            axes[1, 1].text(j, i, "{:.2f}".format(corr[i, j]), ha="center", va="center")
    axes[1, 1].set_title("Корреляции числовых признаков")
    fig.colorbar(img, ax=axes[1, 1])
    save_figure(fig, "02_data.png")


def plot_models(results, y_test):
    # 比较测试集 R^2，并查看每个模型的训练误差是否收敛。
    # сравниваем R^2 на тесте и сходимость ошибки на обучении.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    names = list(results)
    values = [results[name]["metrics"]["R2"] for name in names]
    axes[0].bar(names, values, color=["#8CA6C0", "#4C9A8A", "#3568A8"])
    for i, value in enumerate(values):
        axes[0].text(i, value, "{:.4f}".format(value), ha="center", va="bottom")
    axes[0].set(title="Сравнение на тестовой выборке", ylabel="R^2")
    axes[0].margins(y=0.15)
    for name, result in results.items():
        axes[1].semilogy(result["losses"], label=name)
    axes[1].set(title="Градиентный спуск", xlabel="Итерация", ylabel="MSE (лог. шкала)")
    axes[1].legend()
    save_figure(fig, "03_training.png")

    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    for i, (name, result) in enumerate(results.items()):
        pred = result["prediction"]
        low, high = min(y_test.min(), pred.min()), max(y_test.max(), pred.max())
        axes[0, i].scatter(y_test, pred, s=8, alpha=0.3)
        axes[0, i].plot([low, high], [low, high], "r--")
        axes[0, i].set(title=name, xlabel="Факт", ylabel="Прогноз")
        axes[1, i].scatter(pred, y_test - pred, s=8, alpha=0.3)
        axes[1, i].axhline(0, color="red", linestyle="--")
        axes[1, i].set(xlabel="Прогноз", ylabel="Остаток: факт − прогноз")
    save_figure(fig, "04_predictions.png")


def main():
    OUTPUT.mkdir(exist_ok=True)
    data, train, test = read_and_split()
    plot_statistics(data)
    train, test = preprocess(train, test)
    y_train = train[TARGET].to_numpy(dtype=float)
    y_test = test[TARGET].to_numpy(dtype=float)
    results, rows, coefficients = {}, [], []
    print("\n3. ОБУЧЕНИЕ И ОЦЕНКА")
    for name, features in MODELS.items():
        x_train, x_test = design_matrices(train, test, features)
        theta, losses = fit(x_train, y_train)
        prediction = x_test @ theta
        scores = evaluate(y_test, prediction)
        results[name] = {"prediction": prediction, "losses": losses, "metrics": scores}
        rows.append(dict(model=name, iterations=len(losses), **scores))
        print("\n" + name + ": " + ", ".join(features))
        print("R^2={R2:.4f}, RMSE={RMSE:.4f}, MAE={MAE:.4f}".format(**scores))
        for feature, weight in zip(["Intercept"] + features, theta):
            coefficients.append({"model": name, "feature": feature, "weight": weight})
        # 标准化系数的绝对值可辅助比较影响，但相关特征会影响解释，非因果关系
        # модули стандартизованных весов помогают сравнению, но не доказывают причинность
        ranked = sorted(zip(features, theta[1:]), key=lambda pair: abs(pair[1]), reverse=True)
        print("Наибольшие |веса|:", ", ".join("{} ({:.3f})".format(f, w) for f, w in ranked[:2]))
    pd.DataFrame(rows).to_csv(OUTPUT / "metrics.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(coefficients).to_csv(OUTPUT / "coefficients.csv", index=False, encoding="utf-8-sig")
    predictions = pd.DataFrame({"actual": y_test})
    for name in results:
        predictions[name] = results[name]["prediction"]
    predictions.to_csv(OUTPUT / "predictions.csv", index=False, encoding="utf-8-sig")
    plot_models(results, y_test)
    best = max(results, key=lambda name: results[name]["metrics"]["R2"])
    print("\nЛучшая из трёх моделей по тестовому R^2:", best)
    print("Таблицы и 4 изображения сохранены в:", OUTPUT)
    if SHOW_PLOTS:
        plt.show()


if __name__ == "__main__":
    main()
