# 实验五：决策树 / Деревья решений

按 `ЛР5_Деревья_решений_задание.docx` 的奇数变体完成全部必做任务。
正式俄文报告：[Лабораторная_работа_5.docx](Лабораторная_работа_5.docx)（10 页）。封面沿用实验一，只把实验号改为 5。
全部 9 道控制问题的中俄双语题目和答案：[学习准备答辩_RU_ZH.md](学习准备答辩_RU_ZH.md)，不放进报告。

## 运行

当前电脑：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\Study-Note\AISystem\Labs\lab5\run.ps1"
```

首次在其他电脑配置，使用 Python 3.10 以上版本（本机已配置 Python 3.12）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\run.ps1
```

依赖已固定版本，包含运行实验和生成报告需要的包。`requirements-lock.txt` 记录本机验证过的全部直接和间接依赖，使用 Python 3.12 重建相同环境时可以改为安装该文件。

`run.ps1` 默认使用实验五自己的 `.venv`，不依赖 Codex 或实验四的目录，也不需要激活环境。
运行时隔离外部 `PYTHONPATH` 和用户包，结束后恢复原环境变量。CSV 已附带，安装依赖后运行无需联网。
`AISYSTEM_PYTHON` 可指定其他已安装依赖的 Python 解释器完整路径。

PyCharm 可选择新增的 **Experiment** 运行配置，它直接使用本项目 `.venv`。
若直接右键运行其他文件，请将项目解释器选为 `.venv/Scripts/python.exe`（Python 3.12），旧的 Python 3.6 配置不再适用。
旧环境保留在 `.venv-python36-backup`，未删除。

直接运行或单独检查：

```powershell
.\.venv\Scripts\python.exe experiment.py
.\.venv\Scripts\python.exe -m unittest -v test_decision_tree.py
.\.venv\Scripts\python.exe -m pip check
```

## 代码结构

| 文件 | 职责 |
|---|---|
| `decision_tree.py` | `Node` 数据类、`DecisionTree` 类，手写熵、ID3、概率预测、重要性和文本树 |
| `metrics.py` | 手写 accuracy、precision、recall、混淆计数、ROC/PR 及梯形 AUC |
| `experiment.py` | 清理数据、一次随机选 5 列、分层划分、运行模型、保存结果 |
| `graphics.py` | 类别分布、重要性、ROC/PR、阈值影响图 |
| `test_decision_tree.py` | 9 项检查，用手算样例和排序概率定义验证，不调用现成树或指标 |
| `build_report.py` | 用实际结果生成报告，检查封面、原样式和模板部件保留 |

仅用 NumPy、Pandas、Matplotlib 实现计算和绘图；sklearn 只使用任务允许的 `train_test_split`。
没有调用 sklearn.tree、sklearn.metrics 或现成曲线、AUC 函数。

## 实验协议与结果

- 数据：[UCI 856 官方来源](https://archive.ics.uci.edu/dataset/856)，原始文件和署名见 `data/README.md`。
- 145 个对象；移除 STUDENT ID、GRADE 后 31 列，所有特征按类别处理。
- `y = (GRADE >= 3)`。全体 0/1 类为 67/78，无缺失值、无完整重复行。
- 潜在缺失值、空字符串和 `?` 编为 `<MISSING>`，不删除样本。
- Seed=42；NumPy `default_rng(42).choice(..., replace=False)` 一次选 `floor(√31)=5` 列。
- 五列按抽取顺序为 `class_attendance`、`parental_status`、`reading_scientific`、`high_school_type`、`course_id`。
- 分层 80/20：train=116（54/62），test=29（13/16）。不重复选特征，不用 test 调参。
- 停止条件严格采用任务要求；浮点误差范围 `1e-12` 内的增益视作零，相同增益按特征顺序决定。
- 预测用叶子正类比例，未知类别返回当前节点比例；`p >= 0.5` 判为 1。
- 深度从根 0 开始：深度 5、31 个叶子、48 个节点。完整树保存在 `output/tree.txt`。
- 重要性按任务定义直接累计节点 IG，不按样本数加权；最大为科学阅读 0.670398。

| 集合 | Accuracy | Precision | Recall | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|
| Train | 0.8362 | 0.9388 | 0.7419 | 46 | 3 | 16 | 51 |
| Test | 0.7586 | 0.8462 | 0.6875 | 11 | 2 | 5 | 11 |

ROC AUC=0.774038，PR AUC=0.843640，均为手写梯形积分。
阈值使用叶子概率唯一值、实际回退分数、0、1；额外 `+∞` 提供“无正预测”的端点。
常规 precision 零分母返回 0；PR 绘图端点采用 precision=1，另存 `curve_precision`，不混淆。
同分对象一起处理，x 稳定排序；PR AUC 不等于 average precision。

FN=5 大于 FP=2。降低阈值能提高 recall，但增加 FP；precision 不保证随阈值单调变化。
训练与测试 accuracy 相差 7.76 个百分点，提示可能过拟合；测试仅 29 条，不能过度解读。

## 输出与报告

`output` 包括数据划分、缺失值计数、训练/测试预测、指标、重要性、完整和预览树、全部阈值点、summary.json；
`output/figures` 包括 4 张图。报告含理论、原始数据说明、特征列表、树结构、指标与图表、
误判和过拟合分析，以及树和指标的完整源码。

实验脚本覆盖本实验的 output；不会修改数据、其他实验或自动更新报告。
报告生成依赖已包含在 requirements.txt 中，执行 `.\.venv\Scripts\python.exe build_report.py`；
正文结论对应 seed=42 的固定实验，生成器会检查数据和模板指纹。

已通过 9 项检查、所有节点的增益和停止条件核对、实际预测与 AUC 核对、10 页逐页排版检查，
并验证封面只修改实验号、原模板样式及其他部件保留。核对记录为 `_qa/acceptance.json` 和 `_qa/verification.json`。

可选附加项 Gini 未实施。`_qa` 内的预览和核对记录不属于提交材料。
