# 实验六 / Распознавание рукописных цифр MNIST

NumPy 手写网络、反向传播、Adam 和 IDX 加载器。所有计算代码在 `mnist_lab` 包内，入口是 `python -m mnist_lab`。仅使用 CPU，无需 CUDA。

## 本机直接运行

独立环境已放在本目录 `.venv`，PowerShell 中可以从任意工作目录运行：

```powershell
& 'D:\Study-Note\AISystem\Labs\lab6\run.ps1' -Mode Check
& 'D:\Study-Note\AISystem\Labs\lab6\run.ps1' -Mode Notebook
& 'D:\Study-Note\AISystem\Labs\lab6\run.ps1' -Mode Predict -Image 'D:\图片\我的数字.png'
```

Notebook 模式打开 JupyterLab，双击 `defense.ipynb`，选择 Python 3 内核，逐格运行。启动器使用本实验 `.venv` 的 Jupyter；第一格会打印实际解释器路径。不要选择其他实验或系统 Python 的内核。

如 PowerShell 阻止执行脚本，可用：

```powershell
powershell -ExecutionPolicy Bypass -File 'D:\Study-Note\AISystem\Labs\lab6\run.ps1' -Mode Check
```

## 首次安装与其他电脑

安装 64 位 Python **3.12**。复制整个 lab6 目录，包括 data 和 output，但不复制 `.venv`、`.cache`、`_qa`。进入复制后的目录：

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

如果没有 `py` 启动器，指定实际 Python 路径：

```powershell
.\setup.ps1 -Python 'C:\Users\26771\AppData\Local\Programs\Python\Python312\python.exe'
.\run.ps1 -Mode Check
```

`setup.ps1` 创建独立环境并优先安装 `requirements-lock.txt` 中已验证的完整版本；`requirements.txt` 记录直接依赖。首次安装依赖需要网络；MNIST 文件已缓存时，训练和预测无需联网。缺少原始数据时，训练自动下载四个 IDX gzip 文件并核对 MD5。下载失败应检查网络，或按 `data/README.md` 放置原始文件，不能改用现成数据加载器。

PyCharm：打开 lab6，解释器选择本目录 `.venv\Scripts\python.exe`。直接运行采用模块模式 `mnist_lab`，参数 `train` 或 `predict "图片完整路径"`，工作目录为 lab6；或使用 PowerShell 启动脚本。包内文件通过相对导入协作，不要右键单独运行 `layers.py`、`training.py`。

## 运行模式

| Mode | 行为 |
|---|---|
| Check（默认） | 依赖检查、10 项 unittest |
| Train | 从头执行四组、每组 15 个 epoch，覆盖本实验训练结果 |
| Predict -Image 路径 | 加载最佳权重，打印十类概率，保存 output/prediction.png |
| Notebook | 启动本环境 JupyterLab |
| Drawings | 评价 drawings 内本人手绘图片，保存图和真实结果 |
| Report | 根据现有结果生成俄文 Word 报告 |

训练不会改动原始数据或其他实验。重新训练会覆盖 output 内同名权重、曲线和指标；如需保留旧结果，先复制 output。外部图片不被修改。笔记本不含训练步骤。

## 结构

| 位置 | 职责 |
|---|---|
| mnist_lab/data.py | 下载、校验、手写 IDX 解析、one-hot |
| mnist_lab/layers.py | 五种网络层与联合损失 |
| mnist_lab/model.py | 层组合、Adam、npz 保存加载 |
| mnist_lab/training.py | mini-batch、验证、选最佳 epoch、最终测试 |
| mnist_lab/graphics.py | 样例、类别分布、曲线、混淆矩阵、误判图 |
| mnist_lab/inference.py | 外部图片预处理、概率预测、手绘评价 |
| test_mnist.py | 数值梯度、Adam、Dropout、数据和推理检查 |
| defense.ipynb | 无需重新训练的答辩演示 |
| build_report.py | 读取实际结果，保留封面并生成报告 |
| 学习准备答辩_RU_ZH.md | 控制问题和逐步答辩准备 |

## 结果与本人手绘图

实际指标在 `output/summary.json`，每轮记录在 `history_A.csv` 等文件，最佳权重为 `output/best_model.npz`。四组使用相同 seed=42、54,000/6,000 划分、batch=128、Adam lr=0.001。每组最佳 epoch 由 val accuracy 决定，同分比较 val loss；最终只评价所选模型的官方测试集。

用 Paint 准备 2–3 张单个数字的图片，放在 `drawings`，命名如 `2.png`、`7.png`、`9.png`。白底黑笔、适中粗细，避免文字、多位数字、边框。执行 Drawings 后再执行 Report。报告在不足两张本人手绘图或前三张均识别错误时使用 `_проект` 后缀。控制问题只在独立 MD 中。

本实验不实现选做 CNN。一个 seed 的架构比较不代表统计显著性；高 MNIST 测试准确率不能保证任意外部图片正确。

本次真实训练：最佳 D，val 98.0833%，test **98.24%**（176/10000 个错误），训练与全量评估合计约 173 秒。十项检查通过，干净内核执行笔记本通过，本机 JupyterLab 页面已验证 HTTP 200。本人手绘 2、6、7 已实测，结果为 2→2、6→5、7→7，正确 2/3，满足实践要求。正式报告为 Лабораторная_работа_6.docx，已补入三张原图、处理图、概率和误判分析。旧 _проект 文件仅供历史参考。
