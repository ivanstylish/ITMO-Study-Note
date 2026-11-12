# 实验四：k 近邻方法 / Метод k-ближайших соседей

已按 `ЛР4_Метод_kNN_задание.docx` 完成 Wine 分类和 Diabetes 回归。
最新俄文报告：[Лабораторная_работа_4_更新版.docx](Лабораторная_работа_4_更新版.docx)（13 页）。封面沿用实验一，只将实验号改为 4。
原报告在 Word 中打开，无法覆盖，因此本次另存为“更新版”。报告代码注释和提示文字均为俄语。
目录按住 Ctrl 单击条目即可跳转，页码使用章节引用；7 组公式为可直接编辑的 Word 原生公式。
8 道控制问题的中俄对照题目与答案：[学习准备答辩_RU_ZH.md](学习准备答辩_RU_ZH.md)。

## 运行

当前电脑可以直接在 PowerShell 运行，脚本也会执行检查：

```powershell
powershell -ExecutionPolicy Bypass -File "D:\Study-Note\AISystem\Labs\lab4\run.ps1"
```

也可在本目录直接使用已经配置好的 Python 环境，无需激活环境：

```powershell
.\.venv\Scripts\python.exe experiment.py
.\.venv\Scripts\python.exe -m unittest -v test_knn.py
```

当前电脑使用本机 Python 3.12.10（64 位）创建了本实验专用的 `.venv`，依赖已安装并验证，
运行不依赖 Codex 的 Python 或 `_qa/dependencies`。编辑器的解释器请选择
`D:\Study-Note\AISystem\Labs\lab4\.venv\Scripts\python.exe`。
`requirements.txt` 固定了本次验证的依赖版本。数据集随 scikit-learn 提供，不需要另外下载数据。

如果以后删除或迁移环境，在本目录重新创建（使用 Python 3.12）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

运行脚本默认使用本目录的 `.venv`；环境变量 `AISYSTEM_PYTHON` 可显式指定另一套已安装依赖的 Python。

## 代码结构

| 文件 | 职责 |
|---|---|
| `knn.py` | `KNN` 类：`__init__`、`fit`、`predict`，52 行 |
| `metrics.py` | 手写分类指标、混淆矩阵、MAE、MSE、R²，45 行 |
| `experiment.py` | 加载数据、划分、标准化、24 组验证实验、最终测试、保存结果 |
| `graphics.py` | 生成统计图、验证曲线、混淆矩阵图、回归预测图 |
| `test_knn.py` | 7 项检查，采用手算样例，不使用现成算法或指标作答案 |
| `build_report.py` | 从保存结果生成报告，并验证封面、页面设置和原模板部件未被误改 |

算法与指标只使用 NumPy；Pandas 整理结果，Matplotlib 绘图。
scikit-learn 仅用于 `load_wine`、`load_diabetes(scaled=False)` 和 `train_test_split`。
核心代码有中文注释，未加入任务之外的界面或框架。
报告中的源码摘录单独转换为俄语注释和提示文字，算法与本地源码一致。

## 数据来源

按照任务书指定的加载方式，实际使用 scikit-learn 自带的数据：

- 分类：[`load_wine()`](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html)，178 条样本、13 个特征、3 个类别。
- 回归：[`load_diabetes(scaled=False)`](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_diabetes.html)，442 条样本、10 个特征、连续目标值；加载原始特征后只用 train 计算标准化参数。

本次实验没有从 Kaggle 下载数据。用户提供的两个 Kaggle 页面未能读取到数据文件，
尚未核实它们与本次数据是否逐项一致，不能直接将其列为本实验实际使用的数据来源。

## 实验设置

- 固定 `random_state=42`；两步划分得到约 60% / 20% / 20%。
- Wine 分层划分：train 106、validation 36、test 36；Diabetes：265、88、89。
- 均值和标准差仅由 train 计算，标准化使用 `ddof=0`；目标值不标准化。
- 原始数据无缺失值、无完整重复行，不需要填补或删除。
- `k = 3, 5, 10, 15`，分别使用欧氏、曼哈顿、切比雪夫距离。
- 分类按验证集 macro F1 最大选择；回归按验证集 MSE 最小选择。
- 主指标相同时，先选择较小的 k，再按欧氏、曼哈顿、切比雪夫的顺序选择。
- 分类票数相同，比较该类邻居的距离之和，再相同则选较小类别编号。
- 第 k 位邻居等距时按训练数据原顺序选择，结果可复现。
- 选参后保留原 train，不合并 validation；每个任务只预测一次 test。
- 指标中零分母的类别 precision/recall/F1 取 0；常数目标的 R² 返回 NaN。

## 实际结果

| 任务 | 验证集选出的参数 | 测试结果 |
|---|---|---|
| Wine 分类 | k=15，欧氏距离；验证 macro F1=0.9743 | Accuracy=0.9722，Precision macro=0.9667，Recall macro=0.9778，F1 macro=0.9710 |
| Diabetes 回归 | k=15，切比雪夫距离；验证 MSE=2915.4694 | MAE=46.5213，MSE=3175.5054，R²=0.4510 |

Wine 测试集 36 个样本中预测正确 35 个；唯一错误是将一个类别 1 预测为类别 2。
Diabetes 的最小验证 MAE 对应另一组参数，但选参使用任务预先确定的 MSE。
结果只对应这一次固定划分和规定的参数网格，不能据此认定某种距离对所有数据都最好。

## 输出和报告

`output` 保存两个数据集的原始数据 CSV、描述统计、划分索引、各 12 组验证结果、
测试预测、Wine 混淆矩阵以及 `summary.json`。`output/figures` 中有 6 张图。
描述统计中的 SD 使用 `ddof=1`，与训练标准化中的总体标准差定义不同。

报告包含实验目标、理论与公式、描述统计及可视化、无泄漏的划分方法、
两张完整验证表、验证曲线、最终测试结果、KNN 和指标完整源码、结论。
控制问题及答案已从报告中移至独立的中俄双语答辩准备文档。
已在本机独立环境中通过完整实验和 7 项检查；依赖检查无冲突，24 组结果与报告一致。
报告已完成 13 页排版和封面保留检查；本机 Word 识别到 11 个目录链接、11 个有效章节书签和 7 组可编辑公式，页码均与目标章节一致。

报告生成依赖也已安装，重新生成时执行 `.\.venv\Scripts\python.exe build_report.py`。
若原报告仍在 Word 中打开，生成器会另存为 `Лабораторная_работа_4_更新版.docx`；关闭原报告后，下一次生成会更新原文件。
生成器使用实验一报告作为封面模板；若改变种子、数据或参数，需要同步更新分析文字，
重新生成并检查报告。运行 `experiment.py` 会覆盖本实验的 `output`，不会自动更新报告。
`_qa` 中的依赖、预览和检查文件不属于提交材料。
