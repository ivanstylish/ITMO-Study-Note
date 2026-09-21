from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from graphics import make_figures

ROOT = Path(__file__).resolve().parent
FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
MISSING = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
RATES, STEPS = [0.001, 0.01, 0.1, 1.0], [5, 20, 100, 500, 2000]


def sigmoid(z):
    """Устойчивая сигмоида: экспонента всегда имеет неположительный аргумент."""
    z = np.asarray(z, dtype=float)
    e = np.exp(-np.abs(z))
    return np.where(z >= 0, 1 / (1 + e), e / (1 + e))


def log_loss(y, z):
    """Средняя отрицательная логарифмическая правдоподобность по логитам."""
    return float(np.mean(np.logaddexp(0, z) - y * z))


def split(indices, y, fraction, rng):
    """Стратифицированное разбиение: доли классов сохраняются с округлением."""
    train, test = [], []
    for label in (0, 1):
        group = rng.permutation(indices[y[indices] == label])
        n = round(len(group) * fraction)
        test.extend(group[:n])
        train.extend(group[n:])
    return rng.permutation(train), rng.permutation(test)


def prepare(frame, parameters=None):
    """Медианы и масштаб оцениваются только при первом вызове на обучении."""
    X = frame[FEATURES].astype(float).copy()
    X[MISSING] = X[MISSING].replace(0, np.nan)
    if parameters is None:
        medians = X.median()
        filled = X.fillna(medians)
        parameters = medians, filled.mean(), filled.std(ddof=0).replace(0, 1)
    medians, means, scales = parameters
    # Не переоцениваем параметры на проверке и тесте. 中文：验证和测试不能重新计算参数。
    X = ((X.fillna(medians) - means) / scales).to_numpy()
    if not np.isfinite(X).all():
        raise ValueError('После обработки остались некорректные значения')
    return np.column_stack([np.ones(len(X)), X]), parameters


def fit(X, y, rate=0.1, iterations=500, method='gd'):
    """Пакетный градиентный спуск или метод Ньютона с уменьшением шага."""
    if method not in ('gd', 'newton') or not np.isfinite(rate) or rate <= 0 or iterations < 1:
        raise ValueError('Некорректные гиперпараметры')
    weights = np.zeros(X.shape[1])
    history = [log_loss(y, X @ weights)]
    for _ in range(iterations):
        p = sigmoid(X @ weights)
        gradient = X.T @ (p - y) / len(y)
        direction = gradient
        if method == 'newton':
            hessian = (X.T * (p * (1 - p))) @ X / len(y)
            # Решаем систему, не вычисляя обратную матрицу. 中文：解方程而非求逆。
            direction = np.linalg.solve(hessian + 1e-8 * np.eye(X.shape[1]), gradient)
        step = rate
        candidate = weights - step * direction
        if method == 'newton':
            while log_loss(y, X @ candidate) > history[-1] + 1e-12:
                step *= 0.5
                candidate = weights - step * direction
                if step < 1e-12:
                    candidate = weights.copy()
                    break
        weights = candidate
        history.append(log_loss(y, X @ weights))
        if not np.isfinite(history[-1]):
            raise FloatingPointError('Потери неограниченно растут: уменьшите шаг')
    return weights, history


def metrics(y, predicted):
    """Положительный класс — диабет; нулевой знаменатель даёт метрику 0."""
    tp = int(np.sum((y == 1) & (predicted == 1)))
    tn = int(np.sum((y == 0) & (predicted == 0)))
    fp = int(np.sum((y == 0) & (predicted == 1)))
    fn = int(np.sum((y == 1) & (predicted == 0)))
    return dict(accuracy=(tp + tn) / len(y), precision=tp / (tp + fp) if tp + fp else 0,
                recall=tp / (tp + fn) if tp + fn else 0,
                f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0,
                tp=tp, tn=tn, fp=fp, fn=fn)


def main():
    data_path = ROOT / 'pima-indians-diabetes.data.csv'
    out = ROOT / 'output'
    out.mkdir(exist_ok=True)
    data = pd.read_csv(data_path, header=None, names=FEATURES + ['Outcome'])
    if data.shape != (768, 9) or not data.Outcome.isin([0, 1]).all():
        raise ValueError('Ожидается исходный набор Pima: 768 строк и 9 столбцов')
    statistics = data.describe().T
    statistics.to_csv(out / 'statistics_raw.csv')
    cleaned = data[FEATURES].copy()
    cleaned[MISSING] = cleaned[MISSING].replace(0, np.nan)
    cleaned.describe().T.to_csv(out / 'statistics_cleaned.csv')
    cleaned.isna().sum().rename('missing').to_csv(out / 'missing_values.csv')
    y = data.Outcome.to_numpy()
    rng = np.random.default_rng(42)
    development, test = split(np.arange(len(data)), y, 0.2, rng)
    train, validation = split(development, y, 0.25, rng)
    groups = np.full(len(data), 'обучение', dtype=object)
    groups[validation], groups[test] = 'проверка', 'тест'
    pd.DataFrame({'row_id': data.index, 'partition': groups, 'Outcome': y}).to_csv(out / 'split.csv', index=False)
    Xtrain, parameters = prepare(data.iloc[train])
    Xval, _ = prepare(data.iloc[validation], parameters)
    Xtest, _ = prepare(data.iloc[test], parameters)
    rows, curves = [], {}
    for method in ('gd', 'newton'):
        for rate in RATES:
            for iterations in STEPS:
                weights, history = fit(Xtrain, y[train], rate, iterations, method)
                row = dict(method=method, rate=rate, iterations=iterations, train_loss=history[-1])
                for name, X, target in [('val', Xval, y[validation]), ('test', Xtest, y[test])]:
                    row.update({f'{name}_{k}': v for k, v in metrics(target, sigmoid(X @ weights) >= 0.5).items()})
                    row[f'{name}_loss'] = log_loss(target, X @ weights)
                rows.append(row)
                if iterations == max(STEPS):
                    curves[(method, rate)] = history
    results = pd.DataFrame(rows)
    results.to_csv(out / 'hyperparameter_results.csv', index=False)
    # Выбор только по проверочной выборке. 中文：不能根据测试集成绩选择参数。
    best = results.sort_values(['val_f1', 'val_loss', 'iterations', 'method', 'rate'],
                               ascending=[False, True, True, True, True], kind='stable').iloc[0]
    Xdev, parameters = prepare(data.iloc[development])
    Xtest, _ = prepare(data.iloc[test], parameters)
    weights, _ = fit(Xdev, y[development], float(best.rate), int(best.iterations), best.method)
    probabilities = sigmoid(Xtest @ weights)
    final = metrics(y[test], probabilities >= 0.5)
    final['log_loss'] = log_loss(y[test], Xtest @ weights)
    pd.DataFrame({'row_id': test, 'actual': y[test], 'probability': probabilities,
                  'prediction': (probabilities >= 0.5).astype(int)}).to_csv(out / 'test_predictions.csv', index=False)
    pd.DataFrame({'feature': ['intercept'] + FEATURES, 'coefficient': weights,
                  'odds_ratio': np.exp(weights)}).to_csv(out / 'coefficients.csv', index=False)
    np.savez(out / 'model.npz', weights=weights, medians=parameters[0].to_numpy(),
             means=parameters[1].to_numpy(), scales=parameters[2].to_numpy(), features=np.array(FEATURES))
    summary = dict(seed=42, train=len(train), validation=len(validation), test=len(test),
                   selected=dict(method=best.method, rate=float(best.rate), iterations=int(best.iterations)),
                   validation_f1=float(best.val_f1), final=final,
                   baseline=metrics(y[test], np.zeros(len(test))),
                   sha256=hashlib.sha256(data_path.read_bytes()).hexdigest(),
                   numpy=np.__version__, pandas=pd.__version__)
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    make_figures(out, statistics, results, curves)
    print('Выбранные параметры:', summary['selected'])
    print('Метрики на тесте:', final)
    print('Результаты и графики сохранены:', out)


if __name__ == '__main__':
    main()
