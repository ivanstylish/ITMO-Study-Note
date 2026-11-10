# Lab4：从 RGB 重建光谱

仅实现任务 A/B/C。GUI 沿用 lab3 的左侧参数分组、右侧结果标签页，报告沿用 lab3 的俄文 LaTeX 结构。

## 启动

项目位置：`D:\Study-Note\ComputerGraphicsAlgo\Lab4`。本机已准备 `.venv`，双击 `run_lab4.cmd`。命令行也可以执行：

```powershell
.\.venv\Scripts\python.exe -m lab4_spectrum
.\.venv\Scripts\python.exe -m lab4_spectrum --no-gui
.\.venv\Scripts\python.exe test_lab4.py
```

换电脑时新建 Python 3.12+ 环境，再执行 `python -m pip install -r requirements.txt`。Tkinter 由 Windows 官方 Python 安装器提供。本机环境复用了现有 lab3 已安装的依赖，没有下载额外依赖。


## Lab4 相比 Lab3 新在哪里

| 内容 | Lab3 | Lab4 |
|---|---|---|
| 输入和目标 | 已知光谱场景，对比先光谱后RGB与直接RGB | 从 CIE RGB 反求光谱，再计算 image_A |
| 算法新增 | 光谱→XYZ→CIE RGB、RGB场景计算 | XYZ三基谱，解 C a=M RGB，保持目标颜色 |
| 必须新增的结果 | image_1 / image_2 及白光和彩光实验 | 原谱/重建谱表格和曲线、A/1/2对比及误差 |
| 继续保留 | 相机、屏幕、球体、光源轴、三点亮度、极值 | 复用并校验，不另造几何模型 |
| 当前实际项目的差别 | 已保存白光图的球是绿色，采用双接收余弦、分段sRGB编码 | 任务指定白球，按教材单接收余弦、讲义γ=2.2 |

`comparison.png` 是同几何、白材质、教材照明和曝光的三路径比较。下排分别给绝对 CIE RGB 误差、光度亮度差和辐亮度差，所以不会因三张 PNG 看起来一致而遗漏谱差异。

`lab3_comparison.png` 对照真正的 lab3 原图。它不是单纯的重建误差，材质、接收余弦和显示编码都不同，元数据记录原图 SHA-256，原始文件未被覆盖。

如果在 GUI 修改了光源 RGB，`image_2` 使用当前输入直接计算，`image_1` 仍代表真实原光谱。此时 `input_matches_original=false`，GUI、图注和 JSON 都提示原谱对照的输入颜色已经不同，不虚构一个未知的“真实原谱”。光谱表列出所有光源。

## 为什么代码里出现 sRGB，计算不是 CIE RGB 吗

**计算仍是 CIE RGB 1931。** 该坐标用于 RGB→XYZ→光谱重建以及绝对浮点结果。sRGB 的原色与 CIE RGB 不同，是屏幕和普通图像文件的显示空间。

程序最后才执行 `绝对CIE RGB → XYZ → 线性sRGB → 共同曝光 → 色域裁剪 → γ=2.2 → 0～255`。`XYZ_TO_LINEAR_SRGB` 和 `cie_rgb_to_linear_srgb` 只属于这个显示阶段，不参与重建、光谱积分或绝对亮度。删除它会把 CIE RGB 坐标直接当作屏幕 RGB 解释，造成颜色错误。gamma=2.2 是课程显示近似，不冒充标准 sRGB 的精确分段编码。

## 任务原图如何落实到代码

原图 c 是波长或颜色向量，光谱时为 41 维，CIE RGB 时为 3 维。`light_geometry` 共用于实际渲染和 `geometry_check.csv`，依次计算 I=I₀ max(cosθ,0)、E=I max(cosσ,0)/r²、E/π。`scene_geometry.png` 和 GUI 的“Геометрия задания”根据本次输入画出相机、屏幕、球体、光源及轴、P1、外法线与入射射线，并给每盏灯的距离、角度和数值。

任务图自身把接收 cosσ 同时写入 E 和 f，还把入射向量的符号与外法线混用。报告保留两张完整任务原图并说明矛盾，主模型仍采用教材印刷47页 L=kd E/π 和表面指向光源的接收方向，不增加切换模式。教材印刷66页图4.6作为三基谱/同色异谱的原始图示纳入报告。

## 实验边界

- 输入是绝对 **CIE RGB 1931**，不是 PNG 的 sRGB 0～255。光源 RGB 为单位积分光谱的颜色，I₀ 单独表示可见波段总强度 W/sr。
- 光源按讲义三基谱法恢复。取 F₁=x̄、F₂=ȳ、F₃=z̄，建立 Cᵢₖ=∑wⱼc̄ᵢ(λⱼ)Fₖ(λⱼ)，解 C a=M RGB，再计算 S=F a。恢复函数只接收 RGB，不读取原 D65。若选定基谱给出负光谱则报错，不裁剪、不换算法。
- 讲义只约束 XYZ/RGB，不约束能量积分。**重建谱不再归一化**。输入 I₀ 是原场景的积分强度，在重建计算中作为原有幅值尺度，实际重建积分强度为 I₀×∑wS，已记录在 results.json。
- lab4 要求白色漫反射球，因此固定 `kd(λ)=1`，RGB 反射系数 `(1,1,1)`。未添加彩色材质、彩光模式、额外反射模型、JSON 编辑器。
- **lab3 白光结果实际使用绿色球。** `results/image_1.png`、`image_2.png` 是将 lab3 的光谱与 RGB 两条计算序列按相同白球、教材照明模型、统一显示方式重算的受控基准。`lab4_spectrum/assets/lab3_*` 保存真正的原 lab3 图片和参数，另作直接对照，不把重算图冒充原图。
- 按教材公式 (3.4.5.1) 计算 L=kd·E/π，接收余弦只出现一次。旧版余弦平方模式已删除。
- 380～780 nm，步长 10 nm，41 通道，梯形积分。毫米输入在平方反比公式中转换为米。绝对光谱和 RGB 始终用浮点数，只有显示输出归一到 0～255。
- 三图共享最大通道归一化，按讲义 5 使用 γ=2.2 的显示近似。背景用独立 mask 排除统计。整球极值是 181×360 网格的离散估计，不声称是连续极值。

## 教材与实现对应

先读取并核对以下本地材料，再实现算法。报告引用了相同的书名、章节、页码和公式。

| 内容 | 教材位置 | 实现 |
|---|---|---|
| 三基谱、C a=M RGB、负光谱限制 | `../Lecture/mis_lect04_11.pdf` PDF 第 35～42 页 | `reconstruction.py` |
| D65 由标准观察者曲线重建、同色异谱 | `../Lecture/3281.pdf` 印刷第 64～66 页，图 4.6 | 选定 XYZ 观察者三基谱 |
| L=kd·E/π | `3281.pdf` 印刷第 47 页，式 (3.4.5.1) | `core/geometry.py` |
| CIE RGB→XYZ 数值矩阵 | `3281.pdf` 印刷第 70 页 | `core/color_conversion.py`，逆矩阵由同一矩阵求逆 |
| XYZ→线性 sRGB 矩阵 | `3281.pdf` 印刷第 77 页 | `core/color_conversion.py` |
| 线性空间计算，显示 γ=2.2 | `mis_lect05_11.pdf` PDF 第 43～46 页 | `monitor_encode` |

`3281.pdf` 的 PDF 页码比印刷页码大 1。基谱具体选型与梯形积分是依据任务采样网格落实的选择，不声称教材指定了唯一基谱。讲义 4 第 41 页的矩阵图有重复的波长下标，代码按前一页的积分定义形成矩阵。显示采用讲义 5 明示的 γ=2.2，不使用教材第 77 页排版有误的分段传递公式。

## 输出和报告

`results` 中包含：

- `image_A.png`：恢复光谱后计算的结果。
- `image_1.png`、`image_2.png`：同一白球的 lab3 光谱与 RGB 路径。
- `spectra_comparison.csv` 和 `.png`：41 波长原始和恢复谱、差值，以及材料曲线。
- `three_points.csv`：三点坐标、绝对辐亮度、光度亮度、XYZ/RGB。
- `results.json`：场景、当前与原始RGB、基准适用性、物理/显示误差、极值、单位和原图来源校验。
- `comparison.png`、`lab3_comparison.png`：受控三路径/绝对误差，以及真实原 Lab3 对照。
- `scene_geometry.png`、`geometry_check.csv`：任务图对应的实际场景与逐光源几何核对。
- `points_comparison.csv`：三点 A/1/2 的光度亮度，以及 A/1 的辐亮度。直接 RGB 不能唯一确定辐亮度，不虚报该列。
- `absolute_data.npz`：float64 `spectral_A[H,W,41]`、绝对 XYZ/RGB、mask、辐亮度、光度亮度、恢复谱和输入 RGB。

`overleaf/main.tex` 是手写维护的主报告。`lab4_overleaf.zip` 可上传 Overleaf，选择 **XeLaTeX** 编译。姓名、组号、教师沿用 lab3。更改场景后应同步更新报告的静态表格、图片和数字。

原始要求写 Word 或 PowerPoint，本次按用户要求交付 LaTeX。当前机器未找到 LaTeX 编译器，未声称 PDF 编译通过。

## 验证与实测

`test_lab4.py` 包含 8 项检查，覆盖 RGB 保持、线性缩放、已知三基谱组合、非法输入、能量积分不强制为 1、单余弦独立解析点、辐射量与光度量、文件重读，以及真实 Tk 事件循环中的计算、标签页、光源增删和导出。测试场景 200×200，交付结果单独运行 600×600。

默认光谱 RMSE 约 0.0014188447 /nm，RGB 最大重建误差约 1.11e-16，重建谱积分约 0.62955566。三张默认受控 PNG 像素一致，但辐亮度不同。这是同色异谱，不表示恢复了真实 D65。新增回归检查覆盖修改 RGB 后的正确直接 RGB 基准、显示与物理数组隔离、任务图中的轴向/背向/距离平方关系。

## 代码来源

代码按职责放入 `lab4_spectrum` 包，没有新增管理类或继承层：

```text
lab4_spectrum/
  __main__.py               GUI / 命令行入口，默认输出定位到项目 results
  reconstruction.py         RGB → 光谱重建
  experiment.py             场景与实验计算、对照
  output.py                 图表、摘要与文件导出
  gui.py                    App 界面类
  visualization.py          三路误差图、实际场景几何与原 Lab3 对照
  assets/                   任务原图、教材图及实际 Lab3 参考数据
  core/                     相机、几何、渲染、颜色转换及 CSV 数据
    data/
test_lab4.py                 数值、导出和真实 GUI 测试
results/                    实验数据
overleaf/                   LaTeX 报告
```

`lab4_spectrum/core` 复用 lab3 的相机、求交和校验，照明、光谱尺度及颜色转换已按教材修正。旧版求解器、双余弦模式、彩色材质预设、JSON/光谱编辑加载器和重复导出代码已删除。只保留这一个包版本，入口统一为 `python -m lab4_spectrum`，没有恢复旧的根目录单文件实现。lab1～lab3 未修改，运行不依赖原 lab3 源码目录。

CIE XYZ 表由 lab3 从教师 XLS 抽样得到，D65 表来自 [CIE 数据](https://cie.co.at/datatable/cie-standard-illuminant-d65)，DOI `10.25039/CIE.DS.hjfjmt59`，继承 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)。保留来源并按相同许可共享数据。
