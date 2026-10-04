# 计算机图形算法实验二

依据 `Lab2/АКГ_лр2.docx` 完成球面亮度计算。俄语报告沿用实验一的 ITMO 封面、字体、页边距、页眉、目录与章节风格。题目要求 Word 或 PowerPoint，因此提供 **Word 正式报告**，另附 Overleaf 源文件。

## 文件

- `lab2_report.docx`：Word 报告，含题目、理论公式、详细算法、实际结果、三点绝对亮度、极值、检查与结论。
- `lab2_report.pdf`：由 Word 导出的报告预览，已检查分页；并非 LaTeX 编译结果。
- `lab2.tex`：Overleaf 报告源文件；本次环境未提供原生 LaTeX 编辑器或编译工具，尚未实际编译。
- `lab2_sphere.py`：完整程序，关键公式和理论实现附中文注释，界面与图表使用俄语。
- `parameters.json`：报告使用的参数，可直接修改后运行。
- `test_lab2.py`：八项计算、几何、参数与导出检查。
- `requirements.txt`：运行所需依赖。
- `results/sphere_normalized.png`：600×600 单通道八位球面图像。
- `results/brightness_map.png`：带绝对亮度色条的分布图。
- `results/center_section.png`：穿过球心投影的水平截面，分开显示漫反射和镜面反射。
- `results/three_points.csv`、`results/results.json`：三点计算值、输入参数与极值。
- `results/radiance_data.npz`：未归一化的亮度、反射分量、交点坐标及掩码。
- `results/sphere_mask.png`：球面命中掩码，可区分零亮度球面与背景。

## 运行

建议在带 tkinter 的完整 Python 3.10 或更高版本中运行：

```bash
python -m pip install -r requirements.txt
python lab2_sphere.py
```

界面可修改屏幕大小与分辨率、观察者位置与方向、屏幕距离、球心与半径、材质系数，以及任意数量光源。每个光源一行：`x y z I0`。点击“Рассчитать”计算，“Сохранить результаты”保存。

无界面生成报告参数对应的结果：

```bash
python lab2_sphere.py --no-gui --config parameters.json --output results
```

执行检查：

```bash
python test_lab2.py
```

八项自动检查均已通过；另已使用隐藏窗口验证 GUI 计算与保存。首次启动可能稍慢，因为需要构建字体缓存。

## 模型约定

采用透视投影，默认观察者为 `(0,0,2500)` mm，朝向 `-Z`，屏幕位于 `z=0`，球心为 `(0,0,600)` mm，半径 350 mm。两个朗伯点光源的发射光轴均为 `-Z`。

按照题目图中的经验 Blinn–Phong 反射函数计算：

```text
E_i = I0_i * max(l_i.z,0) * max(n·l_i,0) / r_i²
h_i = normalize(l_i + v)
L = Σ E_i * [kd + ks * max(n·h_i,0)^m]
G = round(255 * L / Lmax_visible)
```

`r_i` 使用米。`kd`、`ks` 在本报告中按 `sr^-1` 解释，输出为能量亮度 `W/(m²·sr)`。这是题目采用的经验模型，不声称满足能量守恒；没有额外加入不同的反射归一化系数，也没有添加环境光、伽马校正或色调映射。

球体必须完整位于视锥内，像素必须为正方形，观察者和光源必须在球体外。参数改变导致球体超出屏幕时，程序提示错误。

## 报告结果

| 项目 | 绝对亮度 W/(m²·sr) |
|---|---:|
| P1 `(0,0,950)` mm | 17.674237094 |
| P2 `(-210,0,880)` mm | 14.117132488 |
| P3 `(210,0,880)` mm | 17.089102346 |
| 可见球面最小值 | 0.000000000 |
| 可见球面最大值 | 79.375576373 |

三点直接代入理论公式计算，不从最近像素读取。主要极值按可见球面的像素中心计算，背景不参与统计。报告额外给出全球面角度网格的采样极值；它们与图像网格不同，均不是连续球面最大值的精确解。

## Overleaf

1. 上传 `lab2.tex` 与整个 `results` 文件夹，可同时附上 Python 源码。
2. 编译器选择 **XeLaTeX**，主文档选择 `lab2.tex`。
3. 封面沿用实验一的姓名 `Чжун Ц. Су Л.`；提交前填写 `\studentgroup` 和 `\teachername`。Word 版也需填写组号与教师。
4. Word 和 Overleaf 源文件内容一致，最终页码会因排版引擎而有所不同。

本次生成数值结果所用环境：Python 3.12.10、NumPy 2.5.3、Matplotlib 3.11.2、Pillow 12.3.0。报告的 PDF 由 Microsoft Word 16.0 导出。
