# Lab5 · 反向路径追踪

在 `Lab5` 目录下运行。需要 Python 3.10 或更新版本。

```powershell
python -m pip install -r requirements.txt
python lab5_pathtracing --gui
```

GUI 需要带 Tcl/Tk 的 Python。可以直接运行 `lab5_pathtracing/gui.py`，也可以在 PyCharm 中选择 Lab5 的解释器后运行该文件。

打开后会显示报告中的两张对照图。把鼠标移到图中，两张图会一起标出同一像素，下方给出直接、间接和总线性 RGB。可在左侧选择光源，修改 XYZ 位置和 RGB 强度，再点「Рассчитать」重新计算。答辩时可先点「Быстрый режим」将分辨率、采样数和深度设为 500、1、2，再启动渲染。完整的相机、材质和几何参数可从 JSON 加载。

「Результат отчёта」重新显示原报告的结果。「Сохранить…」将当前图像和数据写到所选位置下的新子目录。

## 命令行

`python lab5_pathtracing` 以默认参数运行命令行渲染（500×500 像素、每像素 36 条路径、最多 4 次命中）。
答辩时可以复制 `lab5_pathtracing/scene.json`，修改相机、光源位置和强度、物体位置或材质，再用低采样预览。下例使用独立输出目录，便于保留报告所用图像。

```powershell
Copy-Item .\lab5_pathtracing\scene.json .\my_scene.json
python lab5_pathtracing --scene .\my_scene.json --samples 1 --depth 2 --output .\preview
python lab5_pathtracing --help
python lab5_pathtracing\verify.py
```

`--depth 1` 只计算首次命中的直接光照。光源的 `intensity` 是三个通道沿灯轴的辐射强度（W/sr），位置与尺寸用米。材质 `kd` 是漫反射系数，`ks` 是 Cook–Torrance 项的逐通道权重，`roughness` 是 Beckmann 粗糙度，`ior` 用于计算微表面 Fresnel 反射。场景材质为不透明反射体。

## 教材与 Python 实现

| 教材位置（纸质页码） | 程序对应 |
| --- | --- |
| `3281.pdf` 第 26 页，式 (2.12) | 接收余弦与距离平方反比 |
| `3281.pdf` 第 47、51、55 页，式 (3.4.5.1)、(3.4.5.7–8)、(3.4.5.9) | Lambert、Fresnel、Cook–Torrance |
| `3275.pdf` 第 107–108 页，式 (4.59–60) | 点光源的 Lambert 发射与半球余弦分布 |
| `3275.pdf` 第 124–127、132–136 页，第 5.2、5.4 节 | 反向路径采样、显式光源连接、阴影可见性与路径权重 |
| `mis_lect05_11.pdf` PDF 第 43–46 页 | 线性 RGB 计算与显示伽马校正 |

微表面分布采用归一化的 Beckmann 分布，几何项采用 Cook–Torrance 的遮挡项。BRDF 分母按教材式 (3.4.5.9) 实现。[Cook 与 Torrance 原文](https://www.graphics.cornell.edu/~westin/consortium-home/cook-tog.pdf)

## 输出与报告

- `results/render.png` 为多次反射图，`results/direct.png` 为同批主射线的直接光照图。两张图共用白点 4 W/(m²·sr) 和 γ=2.2。
- `results/radiance.npz` 保存 `direct`、`indirect` 和 `full` 三组 `float64` 线性 RGB。`results/results.json` 保存场景参数和统计值。
- `report/Lab5.pdf` 为俄语报告。在 `report` 目录执行两次 `xelatex main.tex` 可重编译。报告引用同一批 `results` 图片，字体随 TeX 源码提供。
