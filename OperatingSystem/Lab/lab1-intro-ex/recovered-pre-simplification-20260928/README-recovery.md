# Intro-Exp：恢复版完整运行顺序

此目录是可运行的增强恢复副本。原始历史备份仍单独保存在 `script-backups/before-simplification-20260928-233854`；当前正式目录和原始备份都不由本套脚本改写。请从 Ubuntu 家目录运行，避免 `/mnt/d` 上的跨系统文件访问干扰测量。

## 先了解实验要完成什么

你的变体为 `Read/Write, Cache, 10M, Seq`。最终正式数据包含四组：`read_lseek/read`、`read_lseek/write`、`mmap/read`、`mmap/write`。每次运行均使用 10 MiB 顺序图、相同的遍历次数和热 page cache；`--write` 是任务参数，`--no-cache` 不用于正式系列。

正式采集脚本每一轮交错运行这四组，并轮换组的起始位置。这样一次收集出手册要求的四组数据，同时减少温度、频率和后台任务随时间漂移造成的偏差。诊断阶段单独保存，不会混入正式 `series-*` 数据。

## 按实验手册顺序完成

### 1. 检查并准备 Linux 环境

在 Ubuntu WSL 终端关闭不必要的 Windows/Ubuntu 应用和同步任务，确认电脑不会睡眠。WSL 中 governor、Turbo、温度或物理磁盘信息可能不可见；脚本会记录能读到的值，报告中如实说明不可用的项目。选一个当前可用的逻辑 CPU；下面示例沿用 `CORE=2`，若不可用请换成 `lscpu -e` 显示的 CPU 编号。

```bash
cd ~/course-code/lab/intro-exp-pre-simplification-20260928
```

首次运行准备脚本会编译两个程序、生成 10 MiB 顺序图和随机图，并留存两个拓扑、两种实现、读/写和热/禁用缓存组合的单次 baseline 记录。baseline 是认识程序行为的探索性数据，不并入统计样本。

```bash
CORE=2 BASELINE_SCOPE=full BASELINE_ITER=1 bash prepare_experiment.sh
```

如果之前已成功生成两张图且只需补齐变体正式运行所依赖的四个顺序/热缓存 baseline，可指定 `BASELINE_SCOPE=variant`。第一次建议 `full`，因为手册的 ознакомительные baseline 包括顺序图与随机图、读写与 no-cache。

结果在 `results/preparation-时间戳/`，检查 `baseline.csv`、`meta_before.txt`、`meta_after.txt`、生成器日志和各次运行日志。若运行无效，不要继续正式测量，先查对应日志。

### 2. 完成诊断工具与背景负载对照

需要 `strace`、`/usr/bin/time`、`taskset`、`timeout`、`setsid`、`python3`；`perf` 若被 WSL/内核权限限制会被标记为 unavailable，不会伪装成零计数。缺少工具时可安装：

```bash
sudo apt update
sudo apt install gcc python3 time strace stress-ng util-linux
```

本恢复版背景压力由脚本启动一个绑定到同一 CPU 的忙循环，不依赖 `stress-ng`；`stress-ng` 可用于额外对照。完整诊断默认包含：四种 API×读写组合的 bare、`/usr/bin/time -v`、`strace -c`，可用时的 `perf stat`；以及 `read_lseek` 和 `mmap` 两种读取实现的 quiet/CPU-load 配对比较。负载进程由脚本启动并在每次测量后清理。

```bash
CORE=2 ITER=20 REPS=3 TOOLS_REPS=3 STAGE=all bash run_diagnostics.sh
```

检查新建的 `results/diag-时间戳/` 中的 `measurements.csv`、`load.csv`、`summary.csv`、`protocol.txt`、`unavailable.txt`（若存在）和 `logs/`。默认 3 轮用于诊断和估计工具开销；这不是正式样本 N。诊断运行较慢是正常的，因为 `strace`/`perf` 重复启动程序且每轮都恢复文件。不要在正式系列同时运行诊断或其他重负载任务。

如果需要分阶段排错，可以分别设置 `STAGE=tools` 或 `STAGE=noise`，但完整提交前应有一次覆盖两部分的 `STAGE=all` 结果。

### 3. 先写假设与实验计划，再看正式结果

打开 `experiment-plan.md`，把实际使用的 CPU 编号、正式 `N`、每次运行的 `ITER`、预热次数、测量指标、缓存策略、异常值规则和 N 的依据写清楚。可先用 baseline/诊断数据估计标准差 `s`，设定目标误差半宽 `E`，按 `N ≈ (t*s/E)^2` 估算，再检查正式数据的 CI 半宽。初始建议是每组 `N=30`、每次 `ITER=20`、每组丢弃 `WARMUP=2` 次预热；如果实测时长过长，可以先调整 ITER 并在确认计划前固定下来。不要因为看到正式结果再改假设、N 或异常值规则。

确认计划后，把文件顶部状态从 `STATUS: DRAFT` 改为 `STATUS: CONFIRMED`。正式采集脚本会拒绝在计划未确认时运行。确认前不要运行正式采集。

### 4. 固定环境并采集正式四组数据

确认 Ubuntu 终端仍在家目录、目标 CPU 可用、没有运行诊断或其他高负载任务。脚本会对每个配置先复制原始图、`sync`、读完整个工作图以预热 page cache，然后开始计时；每组预热运行会丢弃。它在正式数据前后保存环境快照，并保留逐次原始 CSV、日志、参数和脚本副本。

```bash
CORE=2 N=30 ITER=20 WARMUP=2 bash run_series.sh
```

正式测量过程中不要启动诊断、编译、复制大文件或进行其他重负载操作；不要改时间或手工编辑 CSV。若电脑休眠、WSL 重启、进程失败或节点数校验失败，先保留这份记录并说明，再判断是否需要重新采集。

脚本结束时会打印正式 CSV 的完整路径，例如 `.../results/series-时间戳/results.csv`。没有成功完成且四组行数相等的数据，不应进入统计分析。

### 5. 统计处理、作图并形成结论

将上一步打印的实际路径传给唯一的独立分析程序：

```bash
python3 analyze_results.py ~/course-code/lab/intro-exp/results/series-实际时间戳/results.csv
```

分析器只使用 Python 标准库，在相同 `series-*` 目录生成 `analysis/summary.csv`、`analysis/comparisons.csv`、`analysis/analysis.md`、`analysis/means-ci.svg` 和 `analysis/run-order.svg`。它会验证四组数据、计算均值/样本标准差/95% Student t 置信区间、中位数/IQR、配对的 write-read 差值与相对变化，并估计达到 5% 相对半宽所需的 N。成功但较慢的数据点保留；失败行或节点数不对会让分析停止；`cpu_check=bad` 会保留并计数，需回看日志后在报告中说明。

主文报告应给出四组表格和均值+95% CI 图；说明 N、预热与异常值规则、热缓存方法、系统环境局限、诊断工具开销及背景负载结果；据数据判断读写差异是否支持假设、CI 是否足够窄、增加 N 会怎样。诊断 CSV、运行日志和完整脚本放附录/附件即可，不要把长日志贴进正文。

## 只需记住的运行顺序

1. `prepare_experiment.sh`：编译、生成两种图并做 baseline。
2. `run_diagnostics.sh`：工具开销、诊断计数和两种 API 的背景负载对照。
3. 填好并确认 `experiment-plan.md`：固定假设、N、预热、缓存与异常值规则。
4. `run_series.sh`：在安静环境下采集正式四组数据。
5. `analyze_results.py`：统计、配对比较、图表和结果摘要。
6. 根据数据完成报告讨论与答辩；脚本生成的摘要是计算依据，不替代你解释操作系统机制。

正式测量会持续一段时间；不要为了缩短时间减少到 1–3 次并把它当作正式统计样本。可先缩短诊断轮数，或在正式计划确认前降低 ITER，并报告实测参数。
