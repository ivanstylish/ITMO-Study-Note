"""Logistic regression from scratch; only NumPy/Pandas plus Python stdlib."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import platform
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
            'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
ZERO_MISSING = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
KAGGLE = 'https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database'
MIRROR = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv'


def sigmoid(z):
    """Stable sigmoid, including very large positive/negative logits."""
    z = np.asarray(z, dtype=float)
    e = np.exp(-np.abs(z))
    return np.where(z >= 0, 1 / (1 + e), e / (1 + e))


def log_loss(y, logits):
    """Binary cross entropy from logits, without log(0) or exp overflow."""
    return float(np.mean(np.logaddexp(0, logits) - y * logits))


def metrics(y, predicted):
    y, predicted = np.asarray(y), np.asarray(predicted)
    tp = int(np.sum((y == 1) & (predicted == 1)))
    tn = int(np.sum((y == 0) & (predicted == 0)))
    fp = int(np.sum((y == 0) & (predicted == 1)))
    fn = int(np.sum((y == 1) & (predicted == 0)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return dict(accuracy=(tp + tn) / len(y), precision=precision, recall=recall,
                f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
                tp=tp, tn=tn, fp=fp, fn=fn)


class Preprocessor:
    """Fit medians, means and population SD only on the training partition."""
    @staticmethod
    def clean(frame):
        result = frame[FEATURES].astype(float).copy()
        result[ZERO_MISSING] = result[ZERO_MISSING].replace(0, np.nan)
        return result

    def fit(self, frame):
        cleaned = self.clean(frame)
        self.medians = cleaned.median()
        if self.medians.isna().any():
            raise ValueError('A training feature has no observed values.')
        filled = cleaned.fillna(self.medians)
        self.means = filled.mean()
        self.scales = filled.std(ddof=0).replace(0, 1)
        return self

    def transform(self, frame):
        filled = self.clean(frame).fillna(self.medians)
        return ((filled - self.means) / self.scales).to_numpy()


class LogisticRegression:
    def __init__(self, learning_rate=0.1, n_iter=500, optimizer='gd'):
        if not np.isfinite(learning_rate) or learning_rate <= 0:
            raise ValueError('learning_rate must be finite and positive')
        if not isinstance(n_iter, int) or n_iter < 1:
            raise ValueError('n_iter must be a positive integer')
        if optimizer not in ('gd', 'newton'):
            raise ValueError('optimizer must be gd or newton')
        self.learning_rate, self.n_iter, self.optimizer = learning_rate, n_iter, optimizer

    @staticmethod
    def design(X):
        return np.column_stack([np.ones(len(X)), X])

    def fit(self, X, y):
        A = self.design(X)
        y = np.asarray(y, dtype=float)
        if len(y) != len(A) or not len(y) or not np.isin(y, [0, 1]).all():
            raise ValueError('y must be a nonempty binary vector aligned with X')
        if not np.isfinite(A).all():
            raise ValueError('X must contain finite values')
        self.weights = np.zeros(A.shape[1])
        self.loss_history = [log_loss(y, A @ self.weights)]
        self.backtracks = 0
        for _ in range(self.n_iter):
            p = sigmoid(A @ self.weights)
            gradient = A.T @ (p - y) / len(y)
            if self.optimizer == 'gd':
                candidate = self.weights - self.learning_rate * gradient
            else:
                hessian = (A.T * (p * (1 - p))) @ A / len(y)
                # Tiny numerical damping for solving H delta = gradient; no L2 penalty.
                direction = np.linalg.solve(hessian + 1e-8 * np.eye(A.shape[1]), gradient)
                step = self.learning_rate
                candidate = self.weights - step * direction
                while log_loss(y, A @ candidate) > self.loss_history[-1] + 1e-12:
                    step *= 0.5
                    self.backtracks += 1
                    candidate = self.weights - step * direction
                    if step < 1e-12:
                        candidate = self.weights.copy()
                        break
            self.weights = candidate
            loss = log_loss(y, A @ self.weights)
            if not np.isfinite(loss):
                raise FloatingPointError('Nonfinite loss; reduce learning rate')
            self.loss_history.append(loss)
        return self

    def predict_proba(self, X):
        return sigmoid(self.design(X) @ self.weights)

    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)


def stratified_split(indices, y, fraction, rng):
    """Return remaining and holdout indices, preserving both class proportions."""
    remaining, holdout = [], []
    for label in (0, 1):
        group = rng.permutation(indices[y[indices] == label])
        n = int(round(len(group) * fraction))
        holdout.extend(group[:n])
        remaining.extend(group[n:])
    return rng.permutation(remaining), rng.permutation(holdout)


def load_data(path):
    first = path.open(encoding='utf-8-sig').readline()
    frame = pd.read_csv(path) if 'Outcome' in first else pd.read_csv(path, header=None, names=FEATURES + ['Outcome'])
    if list(frame.columns) != FEATURES + ['Outcome']:
        raise ValueError('Expected the eight Pima features followed by Outcome')
    frame = frame.apply(pd.to_numeric, errors='raise')
    if len(frame) < 20 or not frame.Outcome.isin([0, 1]).all() or frame.Outcome.nunique() != 2:
        raise ValueError('Expected both binary classes and at least 20 rows')
    if np.isinf(frame.to_numpy()).any():
        raise ValueError('Infinite values are not supported')
    return frame


def table(frame, digits=4):
    def value(x):
        return f'{x:.{digits}f}' if isinstance(x, (float, np.floating)) else str(x)
    rows = [[value(x) for x in row] for row in frame.itertuples(index=False, name=None)]
    return '\n'.join(['| ' + ' | '.join(map(str, frame.columns)) + ' |',
                      '| ' + ' | '.join(['---'] * len(frame.columns)) + ' |'] +
                     ['| ' + ' | '.join(row) + ' |' for row in rows])


def svg_chart(path, title, labels, series, ylabel='', logx=False):
    """Dependency-free labeled line chart, readable in browsers and Markdown."""
    width, height = 1000, 480
    left, right, top, bottom = 95, 740, 65, 370
    values = np.concatenate([np.asarray(s[1], dtype=float) for s in series])
    lo, hi = float(values.min()), float(values.max())
    pad = (hi - lo) * 0.12 if hi > lo else max(abs(hi) * 0.1, 1)
    lo, hi = lo - pad, hi + pad
    xs = np.log10(np.asarray(labels, float)) if logx else np.arange(len(labels), dtype=float)
    xs = left + (xs - xs.min()) / max(float(np.ptp(xs)), 1e-12) * (right - left)
    def yy(v):
        return bottom - (v - lo) / (hi - lo) * (bottom - top)
    esc = html.escape
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<g font-family="Arial,Microsoft YaHei,sans-serif" font-size="13" fill="#172b4d">',
             f'<text x="30" y="30" font-size="21">{esc(title)}</text>',
             f'<text x="15" y="53">{esc(ylabel)}</text>']
    for v in np.linspace(lo, hi, 6):
        y = yy(v)
        parts += [f'<path d="M{left},{y} H{right}" stroke="#e0e5ec"/>',
                  f'<text x="85" y="{y + 4}" text-anchor="end">{v:.3g}</text>']
    step = max(1, len(labels) // 8)
    short_labels = {'BloodPressure': 'BloodPress', 'SkinThickness': 'SkinFold',
                    'DiabetesPedigreeFunction': 'Pedigree'}
    for i in range(0, len(labels), step):
        label = short_labels.get(str(labels[i]), str(labels[i]))
        parts.append(f'<text transform="translate({xs[i]},395) rotate(18)" text-anchor="start">{esc(label)}</text>')
    palette = ['#1764a0', '#c74832', '#258457', '#8056a5', '#b47b00']
    for j, (name, vals) in enumerate(series):
        color = palette[j % len(palette)]
        points = ' '.join(f'{x:.2f},{yy(v):.2f}' for x, v in zip(xs, vals))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        if len(vals) <= 10:
            parts.extend(f'<circle cx="{x}" cy="{yy(v)}" r="4" fill="{color}"/>' for x, v in zip(xs, vals))
        parts += [f'<rect x="765" y="{74 + j * 28}" width="18" height="3" fill="{color}"/>',
                  f'<text x="790" y="{80 + j * 28}">{esc(name)}</text>']
    path.write_text('\n'.join(parts) + '</g></svg>', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT / 'pima-indians-diabetes.data.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'output')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    out = args.output.resolve()
    figures = out / 'figures'
    figures.mkdir(parents=True, exist_ok=True)
    data = load_data(args.data)
    y = data.Outcome.to_numpy(dtype=int)
    rng = np.random.default_rng(args.seed)
    development, test = stratified_split(np.arange(len(data)), y, 0.2, rng)
    train, validation = stratified_split(development, y, 0.25, rng)
    partition = np.full(len(data), 'train', dtype=object)
    partition[validation], partition[test] = 'validation', 'test'
    pd.DataFrame({'row_id': np.arange(len(data)), 'partition': partition, 'Outcome': y}).to_csv(out / 'split.csv', index=False)
    raw_stats = data.describe().T
    clean = Preprocessor.clean(data)
    clean_stats = clean.describe().T
    raw_stats.to_csv(out / 'statistics_raw.csv')
    clean_stats.to_csv(out / 'statistics_cleaned.csv')
    missing = pd.DataFrame({'feature': FEATURES, 'zero_count': (data[FEATURES] == 0).sum().values,
                            'missing_after_cleaning': clean.isna().sum().values})
    missing.to_csv(out / 'missing_values.csv', index=False)
    prep = Preprocessor().fit(data.iloc[train])
    Xtrain, Xval, Xtest = [prep.transform(data.iloc[idx]) for idx in (train, validation, test)]
    results, histories = [], {}
    for optimizer in ['gd', 'newton']:
        for lr in [0.001, 0.01, 0.1, 1.0]:
            for iterations in [5, 20, 100, 500, 2000]:
                start = perf_counter()
                model = LogisticRegression(lr, iterations, optimizer).fit(Xtrain, y[train])
                row = dict(optimizer=optimizer, learning_rate=lr, iterations=iterations,
                           seconds=perf_counter() - start, train_loss=model.loss_history[-1], backtracks=model.backtracks)
                for label, X, yy in [('validation', Xval, y[validation]), ('test', Xtest, y[test])]:
                    row.update({label + '_' + k: v for k, v in metrics(yy, model.predict(X)).items()})
                    row[label + '_loss'] = log_loss(yy, model.design(X) @ model.weights)
                results.append(row)
                if iterations == 2000:
                    histories[(optimizer, lr)] = model.loss_history
    grid = pd.DataFrame(results)
    grid.to_csv(out / 'hyperparameter_results.csv', index=False)
    # Selection NEVER sorts or filters using the test-set metrics.
    selected = grid.sort_values(['validation_f1', 'validation_loss', 'iterations', 'optimizer', 'learning_rate'],
                                ascending=[False, True, True, True, True], kind='stable').iloc[0]
    final_prep = Preprocessor().fit(data.iloc[development])
    final = LogisticRegression(float(selected.learning_rate), int(selected.iterations), str(selected.optimizer))
    final.fit(final_prep.transform(data.iloc[development]), y[development])
    final_Xtest = final_prep.transform(data.iloc[test])
    final_metrics = metrics(y[test], final.predict(final_Xtest))
    final_metrics['log_loss'] = log_loss(y[test], final.design(final_Xtest) @ final.weights)
    baseline = metrics(y[test], np.zeros(len(test), dtype=int))
    pd.DataFrame({'row_id': test, 'actual': y[test], 'probability': final.predict_proba(final_Xtest),
                  'prediction': final.predict(final_Xtest)}).to_csv(out / 'test_predictions.csv', index=False)
    pd.DataFrame({'feature': ['intercept'] + FEATURES, 'coefficient': final.weights,
                  'odds_ratio': np.exp(final.weights)}).to_csv(out / 'coefficients.csv', index=False)
    np.savez(out / 'model.npz', weights=final.weights, medians=final_prep.medians.to_numpy(),
             means=final_prep.means.to_numpy(), scales=final_prep.scales.to_numpy(), features=np.array(FEATURES))
    summary = dict(seed=args.seed, shape=list(data.shape), sha256=hashlib.sha256(args.data.read_bytes()).hexdigest(),
                   data_path=str(args.data.resolve()), kaggle=KAGGLE, mirror=MIRROR,
                   train=len(train), validation=len(validation), test=len(test), development=len(development),
                   selected=dict(optimizer=str(selected.optimizer), learning_rate=float(selected.learning_rate), iterations=int(selected.iterations)),
                   final_metrics=final_metrics, baseline=baseline,
                   versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__))
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    for statistic in ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']:
        slug = statistic.replace('%', 'pct')
        svg_chart(figures / f'stats_{slug}.svg', f'Raw dataset: {statistic}', list(raw_stats.index),
                  [(statistic, raw_stats[statistic].values)], 'Raw units')
    for optimizer in ['gd', 'newton']:
        subset = grid[grid.optimizer == optimizer]
        for metric in ['accuracy', 'precision', 'recall', 'f1']:
            svg_chart(figures / f'{optimizer}_{metric}.svg', f'{optimizer}: test {metric} vs iterations',
                      [5, 20, 100, 500, 2000],
                      [(f'lr={lr}', subset[subset.learning_rate == lr]['test_' + metric].values)
                       for lr in [0.001, 0.01, 0.1, 1.0]], metric, logx=True)
        steps = np.unique(np.r_[0, np.geomspace(1, 2000, 140).astype(int)])
        svg_chart(figures / f'{optimizer}_loss.svg', f'{optimizer}: training log loss', steps.tolist(),
                  [(f'lr={lr}', np.array(histories[(optimizer, lr)])[steps]) for lr in [0.001, 0.01, 0.1, 1.0]], 'Log loss')
    svg_chart(figures / 'classes.svg', 'Class counts', ['Outcome 0', 'Outcome 1'],
              [('samples', [(y == 0).sum(), (y == 1).sum()])])
    svg_chart(figures / 'missing.svg', 'Missing values after zero replacement', FEATURES,
              [('missing', clean.isna().sum().values)])
    build_report(out, data, raw_stats, clean_stats, missing, grid, selected, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('Report:', out / 'report.html')


def build_report(out, data, raw, clean, missing, grid, best, summary):
    blocks = []
    def text(body):
        blocks.append(('text', body))
    def heading(body):
        blocks.append(('heading', body))
    def tbl(frame):
        blocks.append(('table', frame))
    def fig(name, caption):
        blocks.append(('figure', (name, caption)))
    m = summary['final_metrics']
    heading('实验六 逻辑回归实验报告')
    text(f'本实验选择 Pima Indians Diabetes 数据集，用 NumPy 和 Pandas 从零实现逻辑回归，比较梯度下降与阻尼牛顿法的 40 组超参数。固定随机种子 {summary["seed"]}，按验证集 F1 选择 {best.optimizer}、学习率 {best.learning_rate:g}、迭代 {int(best.iterations)} 次；在开发集重新训练后，测试 accuracy={m["accuracy"]:.4f}，precision={m["precision"]:.4f}，recall={m["recall"]:.4f}，F1={m["f1"]:.4f}。')
    heading('一 实验目的与理论依据')
    text('目标是完成数据清洗、描述统计与图形展示、数据划分、模型实现、超参数比较和分类评价。随附学习文档《логистическая_регрессия.docx》第 14 章介绍二元响应的伯努利分布、logit 联系函数与最大似然估计。本实验采用其中的二分类建模思路，不直接调用现成分类器。')
    text('设 z = b + xᵀw，p = sigmoid(z) = 1 / (1 + exp(−z))，log(p/(1−p)) = z。标签 y∈{0,1}，预测阈值固定为 0.5。平均负对数似然 L = −Σ[y log p + (1−y) log(1−p)]/n。代码用等价形式 mean(logaddexp(0,z)−y·z) 保证数值稳定。')
    text('在设计矩阵 X 增加全 1 截距列后，梯度 g=Xᵀ(p−y)/n，Hessian H=Xᵀdiag(p(1−p))X/n。梯度下降更新 θ←θ−αg；牛顿法解 (H+10⁻⁸I)δ=g，再更新 θ←θ−αδ。牛顿法若损失上升则将步长减半；这个极小的对角阻尼只用于数值求解，不是损失函数中的 L2 正则项。两种方法均从零权重开始，执行指定次数，不使用提前停止。牛顿法的学习率是牛顿方向的步长系数，两种算法的同值步长不代表相同移动距离。')
    heading('二 数据来源与预处理')
    text(f'数据说明页：{KAGGLE} 。该页面说明样本来自至少 21 岁的 Pima 族女性。本次 Kaggle 下载接口返回 HTTP 403，实际下载使用公开镜像：{MIRROR} 。本地 CSV 无表头，字段顺序在代码中显式定义；未声称与无法下载的 Kaggle 文件逐字节相同。')
    text(f'本次数据共 {len(data)} 行、8 个特征和 1 个标签；Outcome=0 有 {int((data.Outcome == 0).sum())} 条，Outcome=1 有 {int((data.Outcome == 1).sum())} 条。完全重复行数为 {int(data.duplicated().sum())}；原始显式空值数为 {int(data.isna().sum().sum())}。SHA-256：{summary["sha256"]}。')
    tbl(pd.DataFrame({'字段': FEATURES + ['Outcome'], '含义': ['怀孕次数', '血糖浓度', '舒张压', '肱三头肌皮褶厚度', '两小时血清胰岛素', '体质指数 BMI', '糖尿病家族遗传函数', '年龄', '是否患糖尿病 0或1']}))
    text('Glucose、BloodPressure、SkinThickness、Insulin、BMI 的零值按该数据集常用处理视为缺失。Pregnancies=0 表示未怀孕，予以保留；标签 0 不处理为缺失。不根据测试集删除异常样本或修改阈值。先划分数据，再仅用训练集各列中位数填补，按训练集均值与总体标准差进行 z-score 标准化；标准差为零时使用 1。')
    tbl(missing)
    fig('classes.svg', '类别数量；折线仅连接类别计数，不表示连续变化。')
    fig('missing.svg', '将不合理零值转换为缺失后，各特征缺失数量。')
    heading('三 描述性统计与图形展示')
    text('以下为原始数据统计，包含零值。count 为非空记录数，std 为样本标准差（ddof=1），25%、50%、75% 为四分位数。不同字段单位不同，图中绝对高度不用于衡量特征重要性。清洗后的统计仅将上述零值置空，没有用全数据拟合填补或缩放参数；这些总体统计仅用于描述。')
    tbl(raw.reset_index(names='feature'))
    for name in ['count', 'mean', 'std', 'min', '25pct', '50pct', '75pct', 'max']:
        fig(f'stats_{name}.svg', f'原始数据统计 {name.replace("pct", "%")}')
    text('将异常零值置为缺失后的描述统计如下；计数下降反映有效观测减少。')
    tbl(clean.reset_index(names='feature'))
    heading('四 划分方案与实验设计')
    text(f'先进行分层 80/20 划分，开发集 {summary["development"]} 条，测试集 {summary["test"]} 条；再从开发集中分层抽取约 25% 作验证集，实际训练 {summary["train"]} 条、验证 {summary["validation"]} 条，整体约 60/20/20。逐类四舍五入造成比例微小偏差。split.csv 保存原始行号及分区，随机数生成器为 NumPy default_rng。')
    text('网格为优化器 {gd,newton} × 学习率 {0.001,0.01,0.1,1.0} × 迭代次数 {5,20,100,500,2000}，共 40 组。按照作业要求，对每组都计算测试集 accuracy、precision、recall、F1；参数选择只依赖验证集 F1，平局时依次选择验证损失更小、迭代更少及固定排序靠前的配置。不得根据表中的测试结果反复改变网格、阈值或选择规则。')
    text('选定配置后，在训练集与验证集合并的开发集上重新拟合预处理和模型，再作最终测试。网格表使用约 60% 数据训练，最终模型使用约 80%，因此两者测试分数可能不同。测试集已被报告多次，这不是盲测流程；验证集选择避免直接按测试指标挑参数，但仍应在新的独立数据上验证泛化能力。')
    heading('五 评价指标与超参数实验结果')
    text('正类为 Outcome=1。accuracy=(TP+TN)/N；precision=TP/(TP+FP)；recall=TP/(TP+FN)；F1=2TP/(2TP+FP+FN)。分母为零时对应指标定义为 0。类别不均衡时只看准确率可能掩盖正类识别不足，故以验证 F1 作为预先固定的选参指标。')
    for optimizer in ['gd', 'newton']:
        heading(f'{optimizer} 的测试集指标')
        cols = ['learning_rate', 'iterations', 'validation_f1', 'test_accuracy', 'test_precision', 'test_recall', 'test_f1', 'train_loss']
        tbl(grid[grid.optimizer == optimizer][cols])
        for metric in ['accuracy', 'precision', 'recall', 'f1']:
            fig(f'{optimizer}_{metric}.svg', f'{optimizer} 各学习率的测试 {metric}；横轴为对数迭代次数。')
        fig(f'{optimizer}_loss.svg', f'{optimizer} 训练损失曲线，展示实际计算的迭代点。')
    heading('六 最终模型与结果分析')
    tbl(pd.DataFrame([{'model': 'majority baseline', **{k: summary['baseline'][k] for k in ['accuracy','precision','recall','f1']}},
                      {'model': 'selected and refit', **{k: m[k] for k in ['accuracy','precision','recall','f1']}}]))
    tbl(pd.DataFrame({'真实类别': ['0', '1'], '预测0': [m['tn'], m['fn']], '预测1': [m['fp'], m['tp']]}))
    text(f'最终模型测试 log loss={m["log_loss"]:.6f}，漏报 FN={m["fn"]}，误报 FP={m["fp"]}。混淆矩阵行是真实类别、列是预测类别。多数类基线全部预测 0，其 F1 为 0，说明仅靠多数类可以获得一定准确率，却不能识别正类。')
    for optimizer in ['gd', 'newton']:
        s = grid[grid.optimizer == optimizer]
        a = s[(s.learning_rate == 0.001) & (s.iterations == 5)].iloc[0]
        b = s[(s.learning_rate == 1) & (s.iterations == 2000)].iloc[0]
        c = s[(s.learning_rate == 1) & (s.iterations == 20)].iloc[0]
        text(f'{optimizer}：学习率 0.001、5 次时训练损失为 {a.train_loss:.6f}，测试 F1={a.test_f1:.4f}；学习率 1、2000 次时训练损失为 {b.train_loss:.6f}，测试 F1={b.test_f1:.4f}。学习率 1、20 次的损失为 {c.train_loss:.6f}，与 2000 次差值为 {abs(c.train_loss-b.train_loss):.6g}。这些结果直接反映步长与迭代次数共同决定的收敛程度；训练损失更低并不保证测试 F1 更高。')
    text(f'验证集选择结果是 {best.optimizer}、α={best.learning_rate:g}、{int(best.iterations)} 次，验证 F1={best.validation_f1:.4f}、验证损失={best.validation_loss:.6f}。这里的“最佳”仅指固定划分、给定网格及既定排序规则下的结果，不能声称是所有数据划分上的全局最佳。')
    converged = grid[(grid.optimizer == 'newton') & (grid.learning_rate == 1) & (grid.iterations == 20)].iloc[0]
    runner_up = grid.sort_values(['validation_f1', 'validation_loss'], ascending=[False, True]).iloc[1]
    text(f'选中配置的训练损失为 {best.train_loss:.6f}，而牛顿法 α=1、20 次的训练损失为 {converged.train_loss:.6f}。当前选择规则可能偏好尚未完全收敛的模型：迭代预算限制带来类似提前停止的效果，并不意味着其优化更充分。验证 F1 与排序第二配置的差距仅为 {best.validation_f1-runner_up.validation_f1:.6f}，没有足够证据声称这种微小优势具有统计显著性。网格中最高测试 F1 为 {grid.test_f1.max():.4f}，但未据此更换最终配置。')
    text('牛顿法利用曲率，通常需要更少迭代达到相近训练损失，但每一步需构造 Hessian 并解线性方程组；本实验仅有 9 个参数，计算规模较小。梯度下降单步成本较低，小学习率需要更多迭代。迭代增多后各方法可能接近同一未正则化目标的解；分类阈值带来离散变化，准确率和 F1 不必随损失下降而单调提高。本次不使用正则化、类别重加权或阈值搜索，避免把额外因素混入三项指定超参数的比较。')
    text('完整耗时和损失见 hyperparameter_results.csv。耗时是单次运行的墙钟时间，受环境影响，不能仅据此作严格速度排名。数据规模较小，单次划分存在抽样波动；后续可使用分层交叉验证。样本限定人群，实验结论不能直接外推到其他人群。')
    heading('七 可复现运行与文件说明')
    text('在 Labs/lab2 中运行：python -m pip install -r requirements.txt，然后运行 python logistic_regression.py。无需联网下载数据。可选参数为 --seed、--data、--output；--data 支持 Kaggle 带表头 CSV 或当前无表头镜像，需保持规定字段顺序。')
    text('代码中 LogisticRegression 为模型，Preprocessor 为仅在训练分区拟合的预处理，metrics 为手写指标。第三方依赖仅 NumPy 和 Pandas，SVG 图表、HTML 和 Markdown 均使用标准库生成。test_logistic_regression.py 验证极端数值、梯度、Hessian、两类优化器及数据划分隔离。')
    text('output 包含完整网格结果、原始和清洗后统计、缺失统计、划分记录、最终模型 model.npz、系数与赔率比、测试预测、summary.json、全部 SVG 图表及本报告。模型参数包括截距，系数对应标准化特征；exp(w) 是其他特征不变时增加一个训练标准差的赔率倍数，不是概率倍数，也不是因果效应。')
    text('运行环境：' + json.dumps(summary['versions'], ensure_ascii=False) + '。核心脚本直接运行会重新生成本次实验的全部结果和报告。')
    heading('八 结论')
    text(f'逻辑回归已完成从概率假设、稳定交叉熵到两类数值优化的实现。本次验证集支持使用 {best.optimizer}、学习率 {best.learning_rate:g}、{int(best.iterations)} 次迭代，重训后测试 F1 为 {m["f1"]:.4f}。小步长与少迭代可能导致收敛不足，而继续训练在收敛后收益有限；优化器效率与最终泛化指标必须分别讨论。结论以实际运行结果为依据，全部 40 组测试指标均可查验。')
    md, web = [], []
    for kind, body in blocks:
        if kind == 'heading':
            md.append('## ' + body)
            web.append('<h2>' + html.escape(body) + '</h2>')
        elif kind == 'text':
            md.append(body)
            web.append('<p>' + html.escape(body) + '</p>')
        elif kind == 'table':
            md.append(table(body))
            web.append('<div class="table">' + body.to_html(index=False, border=0, float_format=lambda x: f'{x:.4f}') + '</div>')
        else:
            name, caption = body
            md.append(f'![{caption}](figures/{name})')
            web.append(f'<figure><img src="figures/{name}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>')
    (out / 'report.md').write_text('\n\n'.join(md) + '\n', encoding='utf-8')
    style = 'body{max-width:1150px;margin:40px auto;padding:0 24px;font:16px/1.8 "Microsoft YaHei",sans-serif;color:#172b4d}h2{color:#111;margin-top:36px}p{overflow-wrap:anywhere}.table{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:7px;border:1px solid #dce2e8;text-align:right}th{background:#eef3f8}figure{margin:28px 0}img{width:100%}figcaption{color:#536279;font-size:14px}@media print{body{margin:0;font-size:11pt}figure, tr{break-inside:avoid}}'
    (out / 'report.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>实验六 逻辑回归实验报告</title><style>' + style + '</style><body>' + '\n'.join(web) + '</body></html>', encoding='utf-8')


if __name__ == '__main__':
    main()
