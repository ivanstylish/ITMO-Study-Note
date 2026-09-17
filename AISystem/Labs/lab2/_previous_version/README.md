# 实验六 逻辑回归

按任务要求保存在 `Labs/lab2`。保留原俄语学习 Word 文档；中文实验报告为 `output/report.html` 和 `output/report.md`。

## 运行

```powershell
cd D:\Study-Note\AISystem\Labs\lab2
python -m pip install -r requirements.txt
python logistic_regression.py
python -m unittest -v test_logistic_regression.py
```

如果 `python` 不在 PATH 中，请用本机 Python 3.10 或以上版本解释器的完整路径代替。依赖只有 NumPy、Pandas，不使用 sklearn、SciPy 或绘图库。数据已附带，实验运行无需联网。

可选：`python logistic_regression.py --seed 42 --data diabetes.csv --output output`。

`output/report.html` 用浏览器打开即可查看完整图表，也可通过浏览器打印。请保留同级 `figures` 文件夹。报告由实际运行结果自动生成；不要手改报告中的分数。

## 数据来源

- 指定数据说明页：https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database
- 本次 Kaggle API 返回 403，实际 CSV 来自公开镜像：https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv
- 下载日期：2026-09-17。文件无表头，共 768 行，字段顺序在脚本的 FEATURES 中定义，最后一列为 Outcome。
- 实际文件 SHA-256 和运行版本记录在 `output/summary.json`。未对无法下载的 Kaggle 原始文件做字节级一致性认证。

## 实验设计

分层 80/20 开发集与测试集划分，再从开发集中抽取验证集，得到约 60/20/20。零值处理、中位数填补、标准化严格在训练分区拟合。比较 2 种优化器、4 种学习率、5 种迭代次数，共 40 组。每组报告测试集四项指标，但仅按验证 F1 和验证损失选择配置。最终合并训练与验证数据重新训练。

## 输出

- `hyperparameter_results.csv`：40 组参数的训练损失、耗时、验证与测试指标。
- `statistics_raw.csv`、`statistics_cleaned.csv`、`missing_values.csv`：完整描述统计。
- `split.csv`：以 0 起始的原始行号、分区和标签。
- `test_predictions.csv`、`coefficients.csv`：最终预测与系数。
- `model.npz`：权重、填补中位数、标准化均值及标准差、特征名。
- `summary.json`：选择结果、最终测试指标、来源与版本。
- `figures/*.svg`、`report.md`、`report.html`：图表及中文报告。

## 加载最终模型预测

```python
import numpy as np
from logistic_regression import Preprocessor, LogisticRegression, sigmoid, load_data
from pathlib import Path

bundle = np.load('output/model.npz')
frame = load_data(Path('pima-indians-diabetes.data.csv'))
raw = Preprocessor.clean(frame).to_numpy()
filled = np.where(np.isnan(raw), bundle['medians'], raw)
X = (filled - bundle['means']) / bundle['scales']
probabilities = sigmoid(LogisticRegression.design(X) @ bundle['weights'])
predictions = (probabilities >= 0.5).astype(int)
```
