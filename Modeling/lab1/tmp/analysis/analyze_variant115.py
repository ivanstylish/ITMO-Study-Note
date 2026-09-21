from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import openpyxl


ROOT = Path(r"D:\Study-Note\Modeling\lab1")
SOURCE = ROOT / "!_УИР1_Варианты_с — копия.xlsx"
OUT = ROOT / "tmp" / "analysis" / "variant115"
OUT.mkdir(parents=True, exist_ok=True)

# 实验流程：读取变体 → 估计统计量 → 拟合 H₂ → 生成样本 → 比较 → 保存绘图数据。
# 各样本量均取原序列的前 n 项，保留观测顺序，不重新抽样或排序。
SAMPLE_SIZES = [10, 20, 50, 100, 200, 300]
# 资料中的 t_p 实际为双侧区间的正态分位数，不是 Student t 分位数。
# 0.90 对应的 1.643 按实验资料保留；小样本且明显偏态时区间仅为近似。
TP = {0.90: 1.643, 0.95: 1.960, 0.99: 2.576}
# 固定种子由变体 115 和实验 01 组成；相同生成器及调用顺序下可复现结果。
RNG_SEED = 11501


def load_variant() -> np.ndarray:
    # 按首行标题 115 定位变体，不是取工作表的第 115 个物理列。
    # data_only=True 读取 Excel 公式已缓存的结果，本程序不负责重算工作簿。
    wb = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    ws = wb["101-150"]
    column = None
    for cell in ws[1]:
        if cell.value == 115:
            column = cell.column
            break
    if column is None:
        raise RuntimeError("Variant 115 was not found in row 1")
    # 第 1 行是变体编号，第 2 至 301 行为 300 个观测值。
    values = [ws.cell(row=r, column=column).value for r in range(2, 302)]
    wb.close()
    if len(values) != 300 or any(v is None for v in values):
        raise RuntimeError(f"Expected 300 numeric values, got {len(values)}")
    return np.asarray(values, dtype=float)


def sample_characteristics(x: np.ndarray) -> dict:
    # 均值 x̄ = Σx_i/n：估计数学期望，描述样本的中心位置。
    mean = float(np.mean(x))
    # 无偏方差 s² = Σ(x_i-x̄)²/(n-1)。ddof=1 将分母从 n 改为 n-1，
    # 补偿使用同一组数据估计均值所消耗的一个自由度。
    variance = float(np.var(x, ddof=1))
    # 标准差 s=√s²，与原始观测值同量纲。
    std = float(np.sqrt(variance))
    # 变异系数 v=s/x̄，无量纲；本实验均值为正，可用于分布选择。
    cv = float(std / mean)
    # 均值标准误 SE=s/√n；置信半区间 ε_p=t_p·SE。
    # 返回的是半宽 ε_p；完整区间为 [mean-ε_p, mean+ε_p]。
    cis = {str(p): float(t * std / np.sqrt(len(x))) for p, t in TP.items()}
    return {
        "n": int(len(x)),
        "mean": mean,
        "variance": variance,
        "std": std,
        "cv": cv,
        "ci_half": cis,
    }


def table_characteristics(x: np.ndarray) -> dict:
    # 表 1：不同样本量与本序列 n=300 时的估计比较。
    # 300 项估计只是本实验的参考值，不是已知总体真值。
    rows = {str(n): sample_characteristics(x[:n]) for n in SAMPLE_SIZES}
    ref = rows["300"]
    for n in SAMPLE_SIZES:
        row = rows[str(n)]
        # 有符号相对偏差 ΔA=(A_n-A_300)/A_300×100%，正号表示高于参考值。
        row["rel_vs_300_pct"] = {
            key: float((row[key] - ref[key]) / ref[key] * 100.0)
            for key in ("mean", "variance", "std", "cv")
        }
        row["ci_rel_vs_300_pct"] = {
            p: float((row["ci_half"][p] - ref["ci_half"][p]) / ref["ci_half"][p] * 100.0)
            for p in row["ci_half"]
        }
    return rows


def lag_correlation(x: np.ndarray, lag: int) -> float:
    # 滞后 k：配对 (x_1,...,x_{n-k}) 与 (x_{1+k},...,x_n)。
    # corrcoef 计算 Pearson 相关：Σ(a-ā)(b-b̄)/√[Σ(a-ā)²Σ(b-b̄)²]。
    # 两个截取序列分别减去各自均值；这与统一减去全样本均值的 ACF 定义
    # 在有限样本下不完全相同。公式图片 eq_acf.png 对应这里的实现。
    return float(np.corrcoef(x[:-lag], x[lag:])[0, 1])


def acf(x: np.ndarray) -> list[float]:
    # 实验要求检查 1 至 10 阶；不包含恒为 1 的零阶相关。
    return [lag_correlation(x, lag) for lag in range(1, 11)]


def ks_two_sample(x: np.ndarray, y: np.ndarray) -> float:
    # 补充诊断：两样本 KS 统计量 D=max_z|F_n(z)-G_m(z)|。
    # 经验分布 F_n(z)=样本中不大于 z 的个数/n，故使用 side="right"。
    # 在两组观测组成的全部跳跃点上取最大差，比较整体分布而非只比较均值。
    grid = np.sort(np.concatenate([x, y]))
    fx = np.searchsorted(np.sort(x), grid, side="right") / len(x)
    fy = np.searchsorted(np.sort(y), grid, side="right") / len(y)
    return float(np.max(np.abs(fx - fy)))


def choose_hyperexp(mean: float, cv: float) -> dict:
    # 二相超指数 H₂ 是两个指数分布的混合，适合矩匹配时 v>1 的情形。
    # 前两个矩不能唯一决定三个参数 q、t1、t2，因此需额外选择 q。
    if cv <= 1.0:
        raise RuntimeError(f"CV={cv:.6f}; hyperexponential law is not applicable")
    # 由 t2>0 可得 0<q<2/(1+v²)；取到上界时 t2=0，成为退化边界。
    q_max = 2.0 / (1.0 + cv * cv)
    # 本变体取 q=0.3；0.8*q_max 保证一般情况下也严格小于上界。
    q = min(0.30, 0.80 * q_max)
    # 矩匹配条件：E[X]=q*t1+(1-q)*t2=mean；
    # Var(X)=2[q*t1²+(1-q)*t2²]-mean²=mean²*cv²。
    # 解得 t1=mean·[1+√((1-q)(v²-1)/(2q))]，
    #      t2=mean·[1-√(q(v²-1)/(2(1-q)))]。
    a = np.sqrt((1.0 - q) * (cv * cv - 1.0) / (2.0 * q))
    b = np.sqrt(q * (cv * cv - 1.0) / (2.0 * (1.0 - q)))
    t1 = mean * (1.0 + a)
    t2 = mean * (1.0 - b)
    if t2 <= 0:
        raise RuntimeError("Calculated second exponential mean is non-positive")
    return {"q": float(q), "q_max": float(q_max), "t1": float(t1), "t2": float(t2)}


def generate_hyperexp(params: dict, n: int = 300) -> np.ndarray:
    # 使用固定种子的伪随机生成器；复现时也要保持下面的批量调用顺序。
    rng = np.random.default_rng(RNG_SEED)
    # U1 选择混合分量，U2 做逆分布变换；两批随机数用于模拟独立均匀变量。
    u1 = rng.random(n)
    u2 = rng.random(n)
    # 以概率 q 选择均值 t1，否则选择 t2；不是把两个指数随机值相加。
    scales = np.where(u1 < params["q"], params["t1"], params["t2"])
    # 指数分布 F(x)=1-exp(-x/t) 的逆变换：X=-t*ln(1-U2)。
    # log1p(-u2) 等于 ln(1-u2)，在 u2 接近零时计算更稳定。
    return scales * (-np.log1p(-u2))


def main():
    original = load_variant()
    original_table = table_characteristics(original)
    original_acf = acf(original)
    params = choose_hyperexp(original_table["300"]["mean"], original_table["300"]["cv"])
    generated = generate_hyperexp(params)
    generated_table = table_characteristics(generated)
    generated_acf = acf(generated)

    # 表 2：生成序列与相同 n 下的原始序列比较，基准不同于表 1。
    for n in SAMPLE_SIZES:
        a = original_table[str(n)]
        b = generated_table[str(n)]
        b["rel_vs_original_pct"] = {
            key: float((b[key] - a[key]) / a[key] * 100.0)
            for key in ("mean", "variance", "std", "cv")
        }
        b["ci_rel_vs_original_pct"] = {
            p: float((b["ci_half"][p] - a["ci_half"][p]) / a["ci_half"][p] * 100.0)
            for p in b["ci_half"]
        }

    # 表 3：这里约定用 |原自相关| 作分母，保留“生成值减原值”的方向。
    # 原系数接近零时百分比会很大；若近乎为零则记为 None，避免除零。
    # 此指标不能单独作为分布拟合质量或独立性的判断依据。
    acf_rel = [
        float((g - o) / abs(o) * 100.0) if abs(o) > 1e-12 else None
        for o, g in zip(original_acf, generated_acf)
    ]
    # 两条完整序列的 Pearson 相关；接近零只说明线性联系弱，不证明独立。
    corr = float(np.corrcoef(original, generated)[0, 1])
    ks_stat = ks_two_sample(original, generated)
    # 独立连续两样本下，5% 显著性水平的常用渐近临界值为 1.36√((n+m)/(nm))。
    # 本例模型参数由原样本拟合，标准独立两样本检验条件并不直接成立，
    # 因而此结果仅作补充诊断；不能直接当作经过校准的正式拟合检验结论。
    ks_critical = float(1.36 * np.sqrt((len(original) + len(generated)) / (len(original) * len(generated))))
    # 白噪声假设下单个滞后自相关的近似 95% 界限 ±1.96/√n。
    # 这不是同时覆盖全部 10 个滞后的区间，偶尔越界不等于存在周期。
    conf = float(1.96 / np.sqrt(300))

    # 19 个边界定义 18 个等宽区间，组距 h=(max-min)/18。
    # numpy 默认左闭右开，最后一个区间包含最右端点，确保最大观测不遗漏。
    source_bins = np.linspace(float(original.min()), float(original.max()), 19)
    source_freq, source_edges = np.histogram(original, bins=source_bins)

    # 保存原始/生成序列、统计表、模型参数和直方图数据。
    # create_charts.cjs 从 results.json 读取这些结果，避免绘图时重复拟合。
    result = {
        "source": str(SOURCE),
        "variant": 115,
        "rng_seed": RNG_SEED,
        "sample_sizes": SAMPLE_SIZES,
        "normal_quantiles": {str(k): v for k, v in TP.items()},
        "original": original.tolist(),
        "original_stats": original_table,
        "generated": generated.tolist(),
        "generated_stats": generated_table,
        "hyperexponential": params,
        "original_acf": original_acf,
        "generated_acf": generated_acf,
        "acf_relative_difference_pct": acf_rel,
        "acf_95_bound": conf,
        "pair_correlation": corr,
        "ks_two_sample": {"statistic": ks_stat, "critical_0_05": ks_critical, "passes_0_05": ks_stat < ks_critical},
        "histogram": {"edges": source_edges.tolist(), "frequencies": source_freq.tolist()},
    }
    (OUT / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "variant": 115,
        "source_n": len(original),
        "source_min": float(original.min()),
        "source_max": float(original.max()),
        "source_300": original_table["300"],
        "params": params,
        "generated_300": generated_table["300"],
        "original_acf": original_acf,
        "generated_acf": generated_acf,
        "acf_bound": conf,
        "pair_correlation": corr,
        "ks": result["ks_two_sample"],
        "histogram": result["histogram"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
