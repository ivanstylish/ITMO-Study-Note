# 实验三 模型正则化 Регуляризация моделей

任务书：`СИИ_ЛР_3.docx`。正式俄文报告：[Лабораторная_работа_3.docx](D:/Study-Note/AISystem/Labs/lab3/Лабораторная_работа_3.docx)。

## 精简版和答辩学习

主程序从原来的 374 行精简到当前 173 行，绘图单独放在 92 行的 `graphics.py`。
训练从批量配置改为一次训练一个模型，核心更新集中在 `fit` 函数。
没有省略任务中的划分、预处理、三种正则化、验证选参、四类曲线和测试评价。
78 组参数的选择结果与原版一致，数值差异仅为浮点误差，8 项检查全部通过。

现场答辩先看 [答辩讲述流程_RU_ZH.md](D:/Study-Note/AISystem/Labs/lab3/答辩讲述流程_RU_ZH.md)。它按照报告翻页顺序提供俄语主讲、中文理解、展示位置和过渡句，包含完整路线与约五分钟讲稿。

原理学习和代码细节参见 [学习答辩_RU_ZH.md](D:/Study-Note/AISystem/Labs/lab3/学习答辩_RU_ZH.md)，其中保留公式推导、任务核对和数值检查解释。

答辩主要展示 `regularization.py`、`graphics.py` 和实验结果。
`build_report.py` 是 Word 排版工具，`test_regularization.py` 是数值检查，不属于需要逐行讲解的训练代码。

## 运行

在本目录打开终端，建议使用 Python 3.10 或更新版本：

```powershell
python -m pip install -r requirements.txt
python regularization.py
python -m unittest -v test_regularization.py
```

当前代码也兼容本机现有的 Python 3.6.8、NumPy 1.19.5、Pandas 1.1.5 和 Matplotlib 3.3.4。
已将绘图中的新版接口改为兼容写法。这个已有虚拟环境可以继续使用，无需为了本次运行升级依赖。

```powershell
.\.venv\Scripts\python.exe regularization.py
```

若系统 Python 不可用或版本较旧，可以直接运行：

```powershell
.\run.ps1
```

启动脚本会优先使用 `AISYSTEM_PYTHON` 指定的解释器或项目虚拟环境，然后检查普通
Python，最后尝试本机 Codex 随附的 Python。它会跳过 Python 3.10 以前的解释器。
绘图库已经下载到本实验的 `_qa/dependencies`，
不修改系统 Python 环境。其他电脑使用上面的标准安装方式即可。脚本缺少必要依赖时会给出提示。

数据默认读取 `../lab1/Student_Performance.csv`，沿用实验一的数据文件和三组特征。
实验运行不需要联网。NumPy 和 Pandas 用于手写训练与评价，Matplotlib 只用于绘图，
未使用 sklearn、SciPy 优化器或现成回归模型。

## 实现和实验设置

- 先删除 127 条完全重复记录，保留 9873 个样本，按 seed=42 划分为训练 5923、验证 1975、测试 1975。
- 缺失值填充、均值和标准差只从训练集计算，验证集和测试集使用同一套参数。
- 三组特征与 `lab1/linear_regression.py` 一致，交互特征为学习时间 × 历史成绩 / 100。
- 四种训练方案采用相同的零初始权重、学习率 0.05 和 10000 次更新，不提前停止。
- 目标函数为 `MSE + λ [ρ ||w||₁ + (1−ρ) ||w||₂²/2]`，截距不加入罚项。
- L1 使用近端梯度下降中的软阈值更新，L2 使用平方罚项的梯度，ElasticNet 结合两者。
- 比较 λ=0.001、0.01、0.1、1、10，ElasticNet 比较 ρ=0.2、0.5、0.8，总计 78 组参数。
- 每组模型的各正则化方案独立按验证集 MSE 选参，只有最终 12 个方案接受测试评价。
- 不合并训练集和验证集重新训练，保证最终曲线、系数与测试评价对应相同模型。
- 曲线和评价中的 MSE 不含正则化罚项，R² 按各自数据集的目标均值计算。

其中 ρ=1 是 L1，ρ=0 是 L2，无正则化时 λ=0。罚项的数值尺度取决于上述公式，
不能直接与其他库默认定义下的 λ 比较。

## 主要结果

| 模型 | 无正则化测试 R² | L1 测试 R² | L2 测试 R² | ElasticNet 测试 R² |
|---|---:|---:|---:|---:|
| 模型 1 | 0.146505 | 0.145573 | 0.146320 | 0.143658 |
| 模型 2 | 0.837623 | 0.837619 | 0.837633 | 0.837633 |
| 模型 3 | 0.988622 | 0.988622 | 0.988612 | 0.988620 |

完整特征模型的未正则化测试 MSE 为 4.261926，RMSE 为 2.064443。
弱正则化对预测质量影响很小，选定参数没有严格为零的系数。
以标准化系数绝对值 ≤0.1 为“接近零”的明确判据，模型三的交互特征在无正则化、
L1 和 ElasticNet 下接近零。较强的 λ=10 会让 L1 在三组模型中分别产生 2、1、4 个零系数，
但显著增加验证误差。这些结论基于一个固定划分，不把微小差别解释为稳定提升。

## 输出文件

| 文件 | 内容 |
|---|---|
| `regularization.py` | 主程序，包含数据处理、近端梯度下降、选参、评价和结果保存 |
| `graphics.py` | 独立绘图，训练和选参均不在此文件中进行 |
| `学习答辩_RU_ZH.md` | 报告逐章解释、代码位置、公式、俄语表述和追问答案 |
| `答辩讲述流程_RU_ZH.md` | 按报告翻页的俄语主讲、中文理解、过渡句、代码展示路线和约五分钟讲稿 |
| `test_regularization.py` | 8 项独立数值与结果一致性检查 |
| `build_report.py` | 将标准实验结果写入俄文 Word 报告 |
| `output/metrics.csv` | 12 个最终方案的训练、验证、测试 MSE、R²、RMSE、MAE 和系数统计 |
| `output/hyperparameter_results.csv` | 78 组参数的训练和验证结果，不含测试指标 |
| `output/coefficients.csv` | 最终方案的标准化系数和原始尺度系数 |
| `output/grid_coefficients.csv` | 所有 78 组参数的系数 |
| `output/model_1_history.csv` 等 | 从第 0 次到第 10000 次的训练和验证 MSE、R² |
| `output/figures/` | 12 张独立要求图、3 张曲线组合图、3 张参数比较图和3 张系数图 |
| `output/test_predictions.csv` | 测试集实际值和12 个方案的预测值 |
| `output/split.csv` | 源 CSV 行号与划分，行号从 0 开始，不计表头 |
| `output/summary.json` | 数据校验和、实验设置、选参和训练预处理参数 |
| `output/models.npz` | 系数、标准化参数、特征顺序和方案顺序 |

本版将可调整参数集中在主程序开头。修改 `LAMBDAS` 和 `RATIOS` 可以改变参数网格，
修改 `RATE` 和 `STEPS` 可以改变学习率和迭代次数。`fit` 的 `strength` 和 `ratio` 参数
分别指定单次训练的 λ 和 ρ。保留至少三个 λ 和三个 ElasticNet 比例，以满足任务要求。

只计算结果、不重新绘图时可以运行：

```powershell
python regularization.py --no-plots
```

报告文字描述的是默认实验快照，改变数据或实验设置后，需要同步更新分析文字和正式报告。
`build_report.py` 会拒绝常见的设置变更，避免直接生成与文字不符的报告。
重新生成 Word 另需 `python-docx`，目录可在 Word 中全选后按 F9 更新。
`_qa` 中的预览、依赖和模板检查文件不属于提交材料。
原长版代码与修改前报告保存在 `_qa/previous-implementation`，用于回溯。
当前正式报告和学习答辩文档的正文均不使用中文或英文分号。
