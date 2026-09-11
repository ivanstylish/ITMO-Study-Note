# 计算机图形算法实验一

本文件夹包含可直接上传到 Overleaf 的实验报告、完整 Python 程序、实验结果和中俄双语答辩材料。

## 文件说明

- `lab1.tex`：俄语实验报告 LaTeX 源文件。
- `lab1_report.pdf`：已编译并检查的报告预览。
- `lab1_illumination.py`：带 GUI 和无界面运行模式的完整程序。
- `defense_zh_ru.md`：中俄双语知识点、答辩问题与演示顺序。
- `results/illumination_normalized.png`：按最大值归一化的八位图像。
- `results/illumination_map.png`：带坐标轴和物理量色条的分布图。
- `results/center_section.png`：穿过圆心的水平截面图。
- `results/five_points.csv`：五个控制点的计算结果。
- `results/results.json`：输入参数、统计量和控制点的可复现数据。

## 在 Overleaf 中编译

1. 新建 Blank Project。
2. 上传 `lab1.tex`、`lab1_illumination.py` 和整个 `results` 文件夹。
3. 在 Overleaf 的 Menu 中将 Compiler 设置为 `XeLaTeX`。
4. 修改 `lab1.tex` 开头的以下字段：
   - `\studentname`
   - `\studentgroup`
   - `\teachername`
5. 点击 Recompile。

## 运行 Python 程序

建议使用 Python 3.10 或更高版本，并安装：

```bash
python -m pip install numpy matplotlib pillow
```

启动图形界面：

```bash
python lab1_illumination.py
```

使用报告中的默认参数直接生成所有结果：

```bash
python lab1_illumination.py --no-gui --output results
```

命令行参数可通过下面的命令查看：

```bash
python lab1_illumination.py --help
```

## 默认实验参数

- 图像区域：1000 mm × 1000 mm；
- 分辨率：600 × 600 px；
- 光源：`(200, -150, 800)` mm；
- 轴向辐射强度：100 W/sr；
- 圆心：`(0, 0)` mm；
- 半径：400 mm。

程序输出的物理量是能量辐照度，单位为 W/m²，而不是 lux。
