# 实验答辩 / Подготовка к защите

[主页](../README.md) · [知识关联](../knowledge/index.md) · [复习入口](revision.md)

按“任务 → 原理 → 代码 → 结果 → 限制”准备口述。实验状态见[实验索引](../navigation/labs.md)，讲解材料与实现可在下面对照阅读。

## 先找到本次实验

| 课程与实验 | 双语解释 / 核心资料 | 演示时打开 | 必须说清的区别 |
|---|---|---|---|
| 操作系统 Intro Exp | [最终学习与答辩](../OperatingSystem/Lab/lab1-intro-ex/Intro-Exp-最终学习与答辩.md)、[15 分钟复习](../OperatingSystem/quick-review.md) | [read/lseek](../OperatingSystem/Lab/lab1-intro-ex/course-code/lab/intro-exp/src/graph_traverse.c)、[mmap](../OperatingSystem/Lab/lab1-intro-ex/course-code/lab/intro-exp/src/graph_traverse_mmap.c) | 4×30 次运行与每次 20 遍；页缓存与 CPU 缓存；perf 未得到计数器与数值为零 |
| 人工智能：线性回归 | [中俄理论与追问](../AISystem/Labs/lab1/Lab1_AI_Linear_Regression.md)、[公式速查](../AISystem/cheatsheet.md) | [linear_regression.py](../AISystem/Labs/lab1/linear_regression.py)：预处理 → 设计矩阵 → fit → evaluate | 截距列、标准化、MSE 梯度与测试指标 |
| 人工智能：逻辑回归 | [Защита_RU_ZH](../AISystem/Labs/lab2/Защита_RU_ZH.md)、[实验说明](../AISystem/Labs/lab2/README.md) | [logistic_regression.py](../AISystem/Labs/lab2/logistic_regression.py)：prepare → fit → metrics → main | 训练 / 验证 / 测试；梯度下降 / 牛顿法；F1 选参与测试评价 |
| 建模实验一：变体 115 | [双语学习笔记](../Modeling/lab1/实验一学习笔记_中俄双语_变体115.md) | 笔记中的统计量、置信区间、图表与分布拟合说明 | 正态分位数与 Student t；原始序列和生成序列的比较基准 |
| 建模实验二：变体 15/15/10 | [双语答辩](../Modeling/lab2/УИР2_defense.md)、[复核说明](../Modeling/lab2/УИР2_复核说明.md) | [lab2_variant15.py](../Modeling/lab2/lab2_variant15.py)、[WinMark 项目说明](../Modeling/lab2/Calculation_data/WinMark/README.md) | 公共 / 独立缓冲区；超指数相位；稳态方程和所采用的调度规则 |
| 计算机体系结构：Wrench Lab3 | [实验要求](../ComputerArchitecture/Lab3/readme.md)、[问答](../ComputerArchitecture/Lab3/ans.md)、[速查](../ComputerArchitecture/quick-review.md) | [Acc32](../ComputerArchitecture/Lab3/task1/acc32.md)、[F32a](../ComputerArchitecture/Lab3/task2/f32a.md)、[M68k](../ComputerArchitecture/Lab3/task3/m68k.md)、[RISC-IV](../ComputerArchitecture/Lab3/task4/risc-iv.md) | ISA 与微架构；不同操作数组织；按对应模拟器说明解释指令 |
| 软件工程 OPI Lab4：JMX | [报告](../OPI/Lab4/readme.md)、[问答](../OPI/Lab4/ans.md) | [PointsCounter](../OPI/Lab4/src/main/java/org/coordinate/mbean/PointsCounter.java)、[JMXRegistration](../OPI/Lab4/src/main/java/org/coordinate/mbean/JMXRegistration.java) | MBean 属性 / 操作 / 通知；监控与性能分析 |
| 数据库 Lab1–4 | [课程实验目录](../Database/readme.md)、[Lab3 问答](../Database/labs/lab3/questions.md)、[Lab4 问答](../Database/labs/lab4/questions.md) | [Lab1 SQL](../Database/labs/lab1/lab1.sql)、[Lab2 SQL](../Database/labs/lab2/lab2.sql)、[函数](../Database/labs/lab3/function.sql)、[Lab4 SQL](../Database/labs/lab4/lab4.sql) | 主键 / 外键；规范化；EXPLAIN 估计与 EXPLAIN ANALYZE 实测 |
| Web：理论与实验解释 | [HTTP/前端](../WebProgramming/Ans/answer1.md)、[Servlet/JSP](../WebProgramming/Ans/answer2.md)、[JSF/JPA](../WebProgramming/Ans/answer3.md)、[Spring](../WebProgramming/Ans/answer4.md) | [Servlet 代码解读](../WebProgramming/Ans/code3.md)、[分层代码解读](../WebProgramming/Ans/code4.md) | 会话生命周期；MVC 各层；框架版本与实际实验对应 |
| 信息系统 Lab1：City Registry | [中俄九题答案](../InformationSystem/Lab1/DEFENSE_QA_ZH_RU.md) | [ApiController](../InformationSystem/Lab1/Lab1/src/main/java/edu/lab/city/web/ApiController.java) → [CityService](../InformationSystem/Lab1/Lab1/src/main/java/edu/lab/city/service/CityService.java) → [ObjectRepository](../InformationSystem/Lab1/Lab1/src/main/java/edu/lab/city/repository/ObjectRepository.java) | Spring / Spring Boot；JPA / EclipseLink；事务、验证与依赖注入 |
| 图形学 Lab1 / Lab2 | [Lab1 中俄问答](../ComputerGraphicsAlgo/Lab1/defense_zh_ru.md)、[Lab2 模型与报告说明](../ComputerGraphicsAlgo/Lab2/lab2_overleaf_project/README.md) | [平面照度代码](../ComputerGraphicsAlgo/Lab1/lab1_overleaf_project/lab1_illumination.py)、[球面亮度代码](../ComputerGraphicsAlgo/Lab2/lab2_overleaf_project/lab2_sphere.py) | 物理量单位；两个余弦因子；绝对值与归一化；离散极值 |
| 计算数学 Lab1：Jacobi | [15 分钟速查](../ComputationalMath/cheatsheet.md)、[原双语题单](../ComputationalMath/Questions/lab1.md) | [SimpleIteration](../ComputationalMath/Lab1/src/main/java/org/example/SimpleIteration.java)、[FormulaUtils](../ComputationalMath/Lab1/src/main/java/org/example/FormulaUtils.java) | 全部使用旧迭代向量；对角占优；停止阈值与真实误差 |

人工智能的逻辑回归在目录中保留为 lab2，正式任务说明称实验 6；请按[原说明](../AISystem/Labs/lab2/README.md)解释编号，不改动目录。

## 一次 20 分钟练习

1. **3 分钟：任务。** 不看笔记，用中文说研究对象、输入、输出、变体；再说对应俄语关键词。
2. **5 分钟：原理。** 推导一条核心公式或画出请求 / 状态 / 数据流；说明适用条件。
3. **5 分钟：代码。** 打开上表链接，指出入口、关键计算、输出位置。不要把生成报告的脚本当作算法实现。
4. **4 分钟：结果。** 只讲当前资料中保留的数据。解释表格列、单位、样本量、评价指标与参数。
5. **3 分钟：追问。** 练“为什么选这个方法”“什么条件下结论不成立”“如何复现”。将不会解释的点带回原笔记核对。

俄语口述顺序：**Задача → метод → реализация → результат → ограничения**。这些词分别对应任务、方法、实现、结果、限制；完整答案使用表中的现有中俄材料。

## 答辩时需要保持的范围

操作系统材料明确记录了 perf 平台限制、两种时钟不一致以及事后样本量评估；不能把置信区间当成消除了系统误差。建模实验二的结论依赖给定负载和调度约定。图形学 Lab2 区分像素网格极值与连续球面精确极值。上述限定已在对应原资料说明，练习时与结论一起讲。

[返回主页](../README.md) · [跨课程知识](../knowledge/index.md) · [继续复习](revision.md)

