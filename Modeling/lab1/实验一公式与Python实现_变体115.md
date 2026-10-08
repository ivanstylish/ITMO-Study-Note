# 实验一公式与 Python 实现 变体 115

本笔记对照当前实际代码整理。数据为 300 个观测值，变体标题为 115。

- 完整数据分析：`tmp/analysis/analyze_variant115.py`。
- 绘图与模型生成：`create_charts.py`。

以下片段用于解释公式，省略了文件读取和绘图样式；需要先 `import numpy as np`。`x` 是原始样本，`y` 是生成样本，`n=len(x)`。俄文术语便于答辩时对照。

## 1 样本范围与前两个矩

对 n=10、20、50、100、200、300，均取序列的前 n 项：

```python
sample = x[:n]  # 从第 1 个观测值取到第 n 个，保持顺序。
```

第一初始矩与第二初始矩 / Первый и второй начальные моменты：

$$
\widehat m_1=\frac{1}{n}\sum_i x_i=\bar x,
\qquad \widehat m_2=\frac{1}{n}\sum_i x_i^2.
$$

```python
first_moment = np.mean(x)
second_moment = np.mean(x**2)
```

这里第二初始矩是补充的等价写法，现有代码直接使用无偏方差拟合。理论关系为 E[X²]=Var(X)+E[X]²；样本中需区分无偏方差的 n−1 分母和原始二阶矩的 n 分母。

## 2 均值 无偏方差 标准差 变异系数

俄文：Среднее，несмещённая дисперсия，СКО，коэффициент вариации。

$$
\bar x=\frac{1}{n}\sum_i x_i,
\qquad s^2=\frac{\sum_i(x_i-\bar x)^2}{n-1},
\qquad s=\sqrt{s^2},
\qquad v=\frac{s}{\bar x}.
$$

```python
mean = float(np.mean(x))            # 均值，估计数据中心。
variance = float(np.var(x, ddof=1)) # ddof=1 对应分母 n−1，得到无偏样本方差。
std = float(np.sqrt(variance))      # 标准差，与观测值同单位。
cv = float(std / mean)             # 无量纲的相对离散程度；本实验 mean>0。
```

对应 `sample_characteristics()`；绘图脚本在 `fit_and_generate()` 中计算同样的量。

无偏方差的等价形式：

$$
s^2=\frac{n}{n-1}(\widehat m_2-\bar x^2).
$$

该式便于理解矩与方差的联系；直接使用 `np.var(..., ddof=1)` 可避免自行相减大数时的精度问题。

变体 115 的 n=300 结果：均值 19.59075，方差 1184.84974，标准差 34.42165，变异系数 1.75704。

## 3 标准误与置信区间

俄文：Стандартная ошибка，доверительный полуинтервал，доверительный интервал。

$$
SE=\frac{s}{\sqrt n},
\qquad \varepsilon_p=t_p SE,
\qquad I_p=[\bar x-\varepsilon_p;\bar x+\varepsilon_p].
$$

```python
TP = {0.90: 1.643, 0.95: 1.960, 0.99: 2.576}
se = std / np.sqrt(len(x))
ci_half = {str(p): t * se for p, t in TP.items()}
# 以下是从半区间得到完整区间的补充示例。
eps95 = ci_half["0.95"]
interval95 = (mean - eps95, mean + eps95)
```

对应 `sample_characteristics()` 的 `cis`。代码保存半宽，报告表格填写 ±ε。资料中的 t_p 是正态分位数，不能与 Student t 分位数混淆。1.643 按实验资料保留。

样本量增加使 SE 通常下降；置信概率增加使区间变宽。正态近似依赖相应抽样条件，小样本、明显偏态或序列依赖时不保证精确覆盖率。

本变体 SE≈1.98733，95% 半宽≈3.89518，完整区间≈[15.69557;23.48593]。

资料中的均值相对误差 / Относительная погрешность среднего：

$$
\delta_p=\frac{\varepsilon_p}{|\bar x|}\cdot100\%.
$$

```python
relative_error = eps95 / abs(mean) * 100
```

此相对误差为补充公式，当前代码没有单独保存它。它描述区间半宽占均值的比例，与下面“相对参考值的偏差”用途不同。

## 4 两种相对偏差

俄文：Относительное отклонение。

表 1：原始样本与原始 n=300 的同名统计量比较。

$$
\Delta A_n=\frac{A_n-A_{300}}{A_{300}}\cdot100\%.
$$

```python
deviation = (row[key] - ref[key]) / ref[key] * 100
```

对应 `table_characteristics()`；`ref=rows["300"]`。n=300 的相对偏差必为零，参考估计不是已知总体真值。A 可为均值、方差、标准差、变异系数或置信半宽。

表 2：生成与原始序列在相同 n 下比较。

$$
\Delta A_n=\frac{A_n^{gen}-A_n^{orig}}{A_n^{orig}}\cdot100\%.
$$

```python
deviation = (b[key] - a[key]) / a[key] * 100
```

对应完整分析脚本 `main()`；a 为原始统计量，b 为生成统计量。n=300 的均值偏差为 +1.12%，方差偏差为 +10.61%。

## 5 Pearson 相关与自相关

俄文：Коэффициент корреляции Пирсона，автокорреляция。

两个长度相同的向量 a、b 的 Pearson 相关为：

$$
r=\frac{\sum_i(a_i-\bar a)(b_i-\bar b)}
{\sqrt{\sum_i(a_i-\bar a)^2\sum_i(b_i-\bar b)^2}}.
$$

```python
correlation = np.corrcoef(a, b)[0, 1]
```

`corrcoef` 返回 2×2 相关矩阵，非对角元素 [0,1] 为两向量相关系数。

自相关将同一序列截成两个平移的部分：

$$
a_i=x_i,\quad b_i=x_{i+k},\quad i=1,\ldots,n-k,
\qquad r_k=\operatorname{corr}(a,b).
$$

```python
def acf(x):
    return np.array([
        np.corrcoef(x[:-k], x[k:])[0, 1]
        for k in range(1, 11)
    ])
```

对应绘图脚本 `acf()`，以及分析脚本 `lag_correlation()` 和 `acf()`。关键点：两段序列各自减去各自的均值，与统一使用全样本均值的另一种 ACF 定义在有限样本下略有差别。

白噪声假设下，单个滞后的近似 95% 参考界限：

$$
\pm\frac{1.96}{\sqrt n}.
$$

```python
bound = 1.96 / np.sqrt(n)
ax.axhspan(-bound, bound, color="#DCECF7")
```

对应 `plot_acf()`。n=300 时界限约 ±0.11316，原始第 7 阶约 0.15849，生成第 10 阶约 0.13675。参考带不是十个滞后的同时置信带，单次越界不直接证明存在周期。

表 3 使用的相对差约定：

$$
\Delta r_k=\frac{r_k^{gen}-r_k^{orig}}{|r_k^{orig}|}\cdot100\%.
$$

```python
acf_rel = [
    (g - o) / abs(o) * 100 if abs(o) > 1e-12 else None
    for o, g in zip(original_acf, generated_acf)
]
```

对应分析脚本 `main()`。分母取绝对值是当前实现的明确约定。原系数接近零时百分比很大，故需结合原系数解读。

两条完整序列之间的相关：

```python
r_xy = np.corrcoef(original, generated)[0, 1]
```

本变体约 −0.02229，表明线性关系弱；相关接近零不能单独证明独立。

## 6 直方图的组距 频数 频率 密度

俄文：Ширина интервала，частота，относительная частота，плотность。

设组数为 m=18：

$$
h=\frac{x_{max}-x_{min}}{m},
\quad c_j=\#\{x_i\text{ 落在第 }j\text{ 组}\},
\quad p_j=\frac{c_j}{n},
\quad \widehat f_j=\frac{c_j}{nh}.
$$

```python
edges = np.linspace(x.min(), x.max(), 19)  # 19 个边界形成 18 组。
counts, _ = np.histogram(x, bins=edges)
ax.hist(x, bins=edges)                    # 柱高为频数 c_j。
ax.hist(x, bins=edges, density=True)       # 柱高为密度 c_j/(n*h)。
```

最后一组包含右端点，避免遗漏最大观测值。频数之和为 n，密度直方图各柱面积之和为 1。当前图中使用频数和密度；p_j 是便于理解的中间概念。

比较原始与生成样本时统一分组边界：

```python
upper = np.ceil(max(x.max(), y.max()) / 50) * 50
common_edges = np.linspace(0, upper, 19)
```

`upper` 仅是绘图上界向上取整到 50 的倍数，不是统计估计。比较图与单独原始直方图的边界可能不同。

## 7 H₂ 模型的矩匹配参数

俄文：Двухфазное гиперэкспоненциальное распределение，метод моментов。

适用条件 v>1。模型有三个参数 q、t₁、t₂，只用两个矩不能唯一决定三个参数，因此额外选择 q。

$$
0<q<q_{max}=\frac{2}{1+v^2},
$$

$$
t_1=\bar x\left[1+\sqrt{\frac{1-q}{2q}(v^2-1)}\right],
\qquad
t_2=\bar x\left[1-\sqrt{\frac{q}{2(1-q)}(v^2-1)}\right].
$$

```python
q_max = 2 / (1 + cv**2)
q = min(0.3, 0.8 * q_max)  # 额外选择 q，并保证严格低于上界。
t1 = mean * (1 + np.sqrt((1-q) * (cv**2-1) / (2*q)))
t2 = mean * (1 - np.sqrt(q * (cv**2-1) / (2*(1-q))))
```

对应分析脚本 `choose_hyperexp()` 和绘图脚本 `fit_and_generate()`。取严格不等号可保证 t₂>0；上界相等时 t₂=0，是退化边界。

本变体 q_max≈0.48934，q=0.3，t₁≈50.16134，t₂≈6.48907。

理论矩检验：

$$
E[X]=qt_1+(1-q)t_2,
\qquad E[X^2]=2[qt_1^2+(1-q)t_2^2],
$$

$$
\operatorname{Var}(X)=2[qt_1^2+(1-q)t_2^2]-E[X]^2.
$$

```python
model_mean = q*t1 + (1-q)*t2
model_variance = 2*(q*t1**2 + (1-q)*t2**2) - model_mean**2
np.testing.assert_allclose(model_mean, mean)
np.testing.assert_allclose(model_variance, variance)
```

绘图代码已包含等价断言，验证参数能重现原始估计的均值和方差。理论模型的矩完全匹配，不意味着生成的有限样本统计量也完全一致。

## 8 理论密度与随机数逆变换

H₂ 密度 / Плотность H₂，z≥0：

$$
f(z)=\frac{q}{t_1}e^{-z/t_1}+\frac{1-q}{t_2}e^{-z/t_2}.
$$

```python
grid = np.linspace(0, upper, 500)
density = q/t1*np.exp(-grid/t1) + (1-q)/t2*np.exp(-grid/t2)
ax.plot(grid, density)
```

对应绘图脚本 `main()`。t₁、t₂ 为指数分量均值，速率分别为 1/t₁、1/t₂。

单个指数分量的分布函数及逆变换 / Метод обратной функции：

$$
F(z)=1-e^{-z/t},\qquad U=F(X)\Longrightarrow X=-t\ln(1-U).
$$

H₂ 用第一个均匀数选择分量，第二个生成该分量的观测：

$$
X=\begin{cases}
-t_1\ln(1-U_2), & U_1<q,\\
-t_2\ln(1-U_2), & U_1\ge q.
\end{cases}
$$

```python
rng = np.random.Generator(np.random.PCG64(11501))
u1, u2 = rng.random(len(x)), rng.random(len(x))
scales = np.where(u1 < q, t1, t2)
generated = scales * (-np.log1p(-u2))
```

对应 `fit_and_generate()` 和 `generate_hyperexp()`。`np.where` 逐项选分量，`np.log1p(-u2)` 计算 ln(1−u₂)，对小 u₂ 更稳定。两个分量是混合选择，不能把两个指数变量相加。固定种子、生成器和调用顺序使结果可复现。

## 9 补充 KS 诊断

当前分析脚本额外计算 KS 统计量，实验报告没有将其列为必要步骤。

$$
F_n(z)=\frac{\#\{x_i\le z\}}{n},\qquad
G_m(z)=\frac{\#\{y_i\le z\}}{m},\qquad
D_{KS}=\max_z|F_n(z)-G_m(z)|.
$$

```python
grid = np.sort(np.concatenate([x, y]))
fx = np.searchsorted(np.sort(x), grid, side="right") / len(x)
fy = np.searchsorted(np.sort(y), grid, side="right") / len(y)
ks_stat = np.max(np.abs(fx - fy))
```

对应 `ks_two_sample()`。`side="right"` 将等于 z 的观测也计入经验分布。

独立连续两样本下，5% 水平常用渐近临界值：

$$
D_{crit}\approx1.36\sqrt{\frac{n+m}{nm}}.
$$

```python
ks_critical = 1.36 * np.sqrt((len(x)+len(y))/(len(x)*len(y)))
```

本实验的生成模型参数由原始样本估计，两组数据并非满足标准检验所需的全部独立条件，因此此临界值比较只作为补充诊断，不能直接给出正式拟合检验结论。

## 10 如何把公式变成图像

| 图像 | 公式或数据来源 | Python 实现 |
|---|---|---|
| 原始序列图 | 保留观测顺序的 x_i | `ax.plot(np.arange(1, len(x)+1), x)` |
| 原始自相关图 | r_k，k=1,...,10 | `ax.plot(range(1, 11), acf(x), "o-")` |
| 原始频数直方图 | c_j，18 个等宽区间 | `ax.hist(x, bins=edges)` |
| 生成序列图 | H₂ 逆变换生成的 y_i | `ax.plot(np.arange(1, len(y)+1), y)` |
| 生成自相关图 | 对 y 计算 r_k | `ax.plot(range(1, 11), acf(y), "o-")` |
| 密度比较图 | 两组密度直方图和理论 f(z) | `ax.hist(..., density=True)` 加 `ax.plot(grid, density)` |

同轴序列比较可将 x、y 的两次 `ax.plot` 放入同一个坐标系；当前 `create_charts.py` 输出上述六张图，未输出独立的同轴序列比较图。

## 11 代码中未自动完成的理论判断

- 分布选择的其他候选包括均匀、指数、埃尔朗及亚指数分布；当前脚本针对变体 115，仅实现 v>1 时的 H₂。
- 由图判断趋势、周期、右偏和长尾，需要结合图像解释，代码没有自动返回这些结论。
- 近零相关、单次自相关越界、两个矩匹配均需按统计含义解释，不能当作完全独立或完整分布相同的证明。
- 标准误、完整区间、相对误差和初始矩的部分片段是由代码已有结果推导的学习示例，前文已注明，未改动现有脚本。
