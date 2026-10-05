# 计算数学：15 分钟速查 / Численные методы

[课程入口](readme.md) · [原 Lab1 双语题单](Questions/lab1.md) · [答辩入口](../study/defense.md)

核心说明以仓库 Lab1 变体 15 的 Java 实现为准。后面提供其他现有算法的源码入口，不将其当作已完成的双语答案。

## 0–5 分钟：Jacobi 公式与收敛条件

对于 Ax=b，且 aᵢᵢ≠0：

$$
x_i^{(k+1)}
=\frac{b_i-\sum_{j\ne i}a_{ij}x_j^{(k)}}{a_{ii}},
\qquad x^{(k+1)}=Gx^{(k)}+c.
$$

**Jacobi / метод Якоби** 每一项只使用完整旧向量。**Gauss–Seidel / метод Гаусса–Зейделя** 在同一轮立即使用已更新的分量；当前 SimpleIteration 实现的是前者。

$$
q=\|G\|_\infty
=\max_i\sum_{j\ne i}\left|\frac{a_{ij}}{a_{ii}}\right|.
$$

q<1 是收敛的充分条件。严格行对角占优意味着这里的 q<1；q≥1 只表示这个充分判据不能保证收敛，不能直接断言发散。

## 5–10 分钟：把公式指到代码

| 文件 / 函数 | 实际行为 |
|---|---|
| [Main](Lab1/src/main/java/org/example/Main.java) | 选择键盘或文件输入；读精度与最大迭代数；调用计算并打印结果。 |
| [FormulaUtils.isDiagonal / isReorderRows](Lab1/src/main/java/org/example/FormulaUtils.java) | 检查严格行对角占优；尝试交换方程行达到要求。交换行不改变未知数顺序。 |
| [FormulaUtils.iterMatNorm](Lab1/src/main/java/org/example/FormulaUtils.java) | 计算上面的迭代矩阵无穷范数。 |
| [SimpleIteration.compute](Lab1/src/main/java/org/example/SimpleIteration.java) | 从零向量开始，先由 xOld 求全部 xNew，再整体复制；以相邻向量最大分量变化小于 eps 停止。 |
| [FormulaUtils.printResidual](Lab1/src/main/java/org/example/FormulaUtils.java) | 输出各分量绝对残差及最大值，在主程序成功分支中调用。 |

代码无法通过换行达到对角占优时会返回失败；这不等于数学上证明 Ax=b 无解。达到最大迭代数也只说明这次算法未达到所设停止条件。

## 10–15 分钟：步差、残差、解误差

| 量 / Термин | 定义与用途 |
|---|---|
| 步差 / разность приближений | Δₖ=‖x⁽ᵏ⁾−x⁽ᵏ⁻¹⁾‖∞；当前代码的停止判据。 |
| 残差 / невязка | r=b−Ax̂；检查近似解代回原方程后的不满足程度。 |
| 解误差 / погрешность решения | e=x*−x̂；精确解未知时通常不能直接计算。 |

q<1 时，Jacobi 的后验误差界为：

$$
\|x^*-x^{(k)}\|_\infty
\le\frac{q}{1-q}\|x^{(k)}-x^{(k-1)}\|_\infty.
$$

因此代码中的“步差 < eps”不能自动解释成“真实解误差 < eps”。若 A 可逆，由 Ae=r 得：

$$
\|e\|\le\|A^{-1}\|\,\|r\|.
$$

原题单第 12 题将 ‖r‖/‖A‖ 写为误差上界，这一表述需要纠正：由 ‖r‖≤‖A‖‖e‖ 得到的是下界。矩阵病态时，小残差仍可能对应较大的解误差；结合条件数解释。

## 俄语 30 秒

> В первой работе реализован метод Якоби для решения Ax=b. Все новые компоненты вычисляются только по предыдущему вектору. Программа проверяет строгое диагональное преобладание, при необходимости переставляет строки и вычисляет норму матрицы итераций. Остановка задана по разности соседних приближений, а невязка проверяется отдельно. Малый шаг или малая невязка сами по себе не гарантируют малую ошибку решения.

## 其他已有源码入口

| 目录 | 真实入口 | 读代码时重点 |
|---|---|---|
| Lab3 数值积分 | [Methods](Lab3/lab3/Methods.py)、[Integrator](Lab3/lab3/Integrator.py) | 方法、划分与精度控制。 |
| Lab4 最小二乘逼近 | [least_squares](Lab4/lab4/core/least_squares.py)、[approximations](Lab4/lab4/models/approximations.py) | 模型形式、系数和拟合误差。 |
| Lab5 插值 | [Interpolator](Lab5/lab5/Interpolator.py)、[FiniteDiffTable](Lab5/lab5/FiniteDiffTable.py) | 节点、差分与插值表达式。 |
| Lab6 常微分方程 | [Euler](Lab6/lab6/methods/Euler.py)、[RungeKutta4](Lab6/lab6/methods/RungeKutta4.py)、[Adams](Lab6/lab6/methods/Adams.py) | 初值、步长、方法阶数与误差。 |

实验状态：✓ 已通过。实现与公式可对照本页复习。

[返回课程入口](readme.md) · [继续原双语题单](Questions/lab1.md)

