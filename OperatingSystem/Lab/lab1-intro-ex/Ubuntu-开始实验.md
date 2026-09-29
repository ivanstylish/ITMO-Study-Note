# Ubuntu 上完成你的 Intro Exp

你的变体是 **Read vs Write, Cache, 10M, Seq**，即在系统缓存启用、10 MiB 顺序图条件下，比较读取与修改顶点的时间。配图中第三排右侧对应你的题目。

## 1. 直接使用已有 Ubuntu

如果你在开机时可以选择进入 Ubuntu，这是本机原生 Linux，可以直接完成实验，不用额外安装 WSL 或虚拟机。如果 Ubuntu 安装在虚拟机或 WSL 中，也可以使用；报告中如实记录环境。

把下面的 `course-code` 文件夹复制到 Ubuntu 的家目录，例如 `~/course-code`。双系统时，先从 Windows 分区复制到 Ubuntu 自己的文件系统，再测试。不要直接在 Windows 的 NTFS 分区、WSL 的 `/mnt/c`/`/mnt/d` 或虚拟机共享目录上运行文件性能测试。

```
wsl -l -v
```

```
uname -a
lscpu
free -h
gcc --version
findmnt -T ~/course-code/lab/intro-exp/graph-seq.bin
```
验证使用的wsl linux ubuntu发行版本

## 2. 本地文件分别做什么

`course-code` 是从 `secs-dev/os-course` 下载的相关文件子集，保留原相对目录，不是整个课程仓库。原始程序没有修改；来源和 Git blob 校验值见 `course-code/SOURCE-MANIFEST.json`。

| 相对 `course-code` 的路径 | 用途 |
|---|---|
| `lab/util/graphgen.py` | 生成实验图文件 |
| `lab/intro-exp/src/graph_traverse.c` | 用 `lseek/read/write` 遍历和修改顶点 |
| `lab/intro-exp/src/graph_io.h` | 上述程序必需的公共文件 I/O 实现 |
| `lab/intro-exp/src/graph_traverse_mmap.c` | 用 `mmap` 遍历和修改顶点 |
| `lab/intro-exp/README.md` | 课程实验原文 |
| `doc/experiments/` | 环境、监控和统计方法原文 |
| `doc/report.md`、`doc/process.md` | 报告与提交要求 |

应以课程提供的程序作为被测对象。你需要编写并解释自己的数据采集与统计脚本；不用为这项实验重新实现图遍历程序。若课程要求通过自己的私有仓库和 PR 提交，把这些文件放回自己的课程仓库中并保留来源记录。

## 3. 在 Ubuntu 中安装基础工具

打开 Ubuntu 终端：

```bash
sudo apt update
sudo apt install build-essential python3 time strace sysstat stress-ng
```

`perf` 的安装与内核版本有关，可在需要诊断时按所在 Ubuntu 的内核安装匹配工具；它不是以下编译和初步试跑的前置条件。

## 4. 编译与生成顺序图

以下假设文件夹已复制到 `~/course-code`：

```bash
cd ~/course-code/lab/intro-exp
mkdir -p out
gcc -O2 -Wall -Wextra -o out/graph_traverse src/graph_traverse.c
gcc -O2 -Wall -Wextra -o out/graph_traverse_mmap src/graph_traverse_mmap.c
python3 ../util/graphgen.py -s 10M --seed 427 --topology sequential --verify -o graph-seq.bin
stat -c '%n: %s bytes' graph-seq.bin
```

生成命令会创建或覆盖 `graph-seq.bin`，用于准备实验初始数据。保存生成器输出，确认验证通过；Seq 必须用 `sequential`，不能用随机物理顺序的 `chain`。

## 5. 四组功能试跑

```bash
/usr/bin/time -v ./out/graph_traverse 1 graph-seq.bin
/usr/bin/time -v ./out/graph_traverse --write 1 graph-seq.bin
/usr/bin/time -v ./out/graph_traverse_mmap 1 graph-seq.bin
/usr/bin/time -v ./out/graph_traverse_mmap --write 1 graph-seq.bin
```

| 组别 | 程序 | 老师的参数记法 |
|---|---|---|
| A | `graph_traverse`，Read | `(-,-)` |
| B | `graph_traverse`，Write | `(WR,-)` |
| C | `graph_traverse_mmap`，Read | `(-,-)` |
| D | `graph_traverse_mmap`，Write | `(WR,-)` |

四组都不使用 `--no-cache`。`1` 是每次运行的完整遍历次数；正式实验中可固定增大，但四组应保持可比。Write 会把访问到的 `value` 加 1，因此会修改测试文件，但不改变图链接。

这些命令只验证程序能够运行，不是正式统计结果。正式实验还需记录系统信息、固定缓存预热策略、确定 N、交错测量四组、保留每次原始结果、计算置信区间。具体方法见旁边的 `Intro-Exp-学习与答辩.md`。

## 6. 报告要回答的问题

对每种访问 API 分别计算 `平均 Write 时间 / 平均 Read 时间`，以及相对增加量 `(平均 Write 时间 − 平均 Read 时间) / 平均 Read 时间 × 100%`，用置信区间说明结论精度。若 Write 没有更慢，如实报告并检查缓存状态、调频、系统调用和测量噪声。

Cache 模式下程序完成不等于数据已经持久写入硬盘，因此不要把这个结果写成“硬盘纯写入速度”。原生 Ubuntu 可以减少虚拟化因素，但仍需控制后台任务与缓存状态。

报告正文和封面已有俄语 Markdown/Typst 模板。填写个人信息和真实数据后再导出 PDF；不要把功能试跑当成完整实验。
