# xv6 Intro 与 Shebang 实验记录

本记录属于 ITMO 操作系统课程的 xv6 方向。现有的 `lab1-intro-ex` 是另一项实验，原资料保留。

## 当前进度

- 已核对 Windows、WSL2、Ubuntu 和 Docker。
- 已克隆学校源码并建立本地 `lab-1` 分支。
- Docker 课程镜像已下载，容器工具版本和 QEMU 版本检查通过。
- 未修改的学校源码已编译并通过 QEMU 启动与 echo 检查。
- Pingpong 已实现，通过默认容量、1 字节容量和恢复后的 40 次实际运行。
- 全仓库 `make fmt-check` 通过。
- Dump、Dump2 和 Shebang 已实现，功能检查全部通过。
- Intro 与 Shebang 各自的完整 usertests 和三类崩溃恢复检查通过。
- 已将两个实验分支推送到私有仓库，并分别创建 Intro PR #1 和 Shebang PR #2，均尚未合并。
- Shebang 两套远程 CI 已通过，Intro 专用 CI 已通过，通用 CI 连续两次在孤儿文件输出标记处超时，正在独立分支采集诊断。详见 [CI 复核记录](CI-复核记录.md)。

详细讲解、调用图和中俄双语答辩资料分别见 [Intro 学习与答辩](Intro-学习与答辩.md) 和 [Shebang 学习与答辩](Shebang-学习与答辩.md)。两份源码目录内另有可供审阅的俄语 `REPORT.md`。

## 提交与报告

学生：Чжун Цзяцзюнь，组号 P3310。教师：Максимов Андрей Николаевич，GitHub [Benderr11](https://github.com/Benderr11)。

目前教师尚无私有仓库访问权限。按用户选择暂不发送邀请，先检查报告。

远程仓库保持私有，两个实验分别提交审阅。以下 PR 已创建，实验分支已推送，均尚未合并。远程 CI 进度见 [CI 复核记录](CI-复核记录.md)，本地通过记录见下方验证表。

| 实验 | 分支与 PR | 本地 PDF 报告 | 报告源码 |
| --- | --- | --- | --- |
| Intro | `lab-1`，[PR #1](https://github.com/ivanstylish/os-course-xv6-riscv/pull/1) | [ЛР(1) P3310 Чжун Цзяцзюнь.pdf](<D:/Study-Note/OperatingSystem/Lab/xv6-intro/output/pdf/ЛР(1) P3310 Чжун Цзяцзюнь.pdf>) | [Typst 源码](D:/Study-Note/OperatingSystem/Lab/xv6-intro/report.typ)，[俄语 REPORT.md](D:/Study-Note/OperatingSystem/Lab/xv6-intro/REPORT.md) |
| Shebang | `lab-shebang`，[PR #2](https://github.com/ivanstylish/os-course-xv6-riscv/pull/2) | [ЛР(shebang) P3310 Чжун Цзяцзюнь.pdf](<D:/Study-Note/OperatingSystem/Lab/xv6-shebang/output/pdf/ЛР(shebang) P3310 Чжун Цзяцзюнь.pdf>) | [Typst 源码](D:/Study-Note/OperatingSystem/Lab/xv6-shebang/report.typ)，[俄语 REPORT.md](D:/Study-Note/OperatingSystem/Lab/xv6-shebang/REPORT.md) |

两份 PDF 均为 A4、4 页，已逐页检查。封面采用现有 intro-exp 报告的学校、院系和专业信息，正文包含实现说明、实际测试结果与 PR 链接。

修改报告时先编辑对应的 `REPORT.md`，然后在课程目录重新生成两份 `report.typ` 和 PDF。以下入口使用本机现有 Typst，不会安装软件。

```powershell
node .\Lab\xv6-notes\scripts\build-reports.mjs
```

也可以使用 Typst 独立编译各自的 `report.typ`。直接修改 `report.typ` 后再次运行上述生成入口会被 `REPORT.md` 内容覆盖。

## 源码与环境

| 项目 | 当前记录 |
| --- | --- |
| 日期 | 环境检查 2026-10-16，后续实现与验收 2026-10-17，莫斯科时间 |
| 学校仓库 | https://github.com/secs-dev/xv6-riscv |
| 基线提交 | `57dc72da888497f03084262bcbb40eed04e83eb4` |
| Intro 源码 / 分支 | `D:\Study-Note\OperatingSystem\Lab\xv6-intro` / `lab-1` |
| Shebang 源码 / 分支 | `D:\Study-Note\OperatingSystem\Lab\xv6-shebang` / `lab-shebang` |
| 私有远程仓库 | https://github.com/ivanstylish/os-course-xv6-riscv |
| 学校只读远程名称 | `upstream` |
| Docker 镜像 | 学校提供的 `vityamand/xv6:latest`，启动入口固定使用本次验证的 digest |
| 镜像 digest | `sha256:1bc77fa40a642500bd4dbba1412e1575303976b0dec48f047eaf8237fd93dd69` |
| 容器系统 | Ubuntu 26.04 LTS，x86_64 |
| RISC-V GCC | 14.2.0 |
| QEMU | 10.2.1，满足至少 7.2 的要求 |
| 主机 GCC / Make | 15.2.0 / 4.4.1 |
| GDB / clang-format | 17.1 / 22.1.8 |
| 容器源码目录 | `/xv6`，挂载自本机源码目录 |
| 容器笔记目录 | `/lab-notes`，挂载自本目录 |
| 现有 WSL | Ubuntu 22.04.5 LTS，WSL2，x86_64 |

现有 Ubuntu 具备 Git、Make、主机 GCC、Perl、Python 和 bc。它尚未安装 RISC-V 工具链和 QEMU。本次使用 Docker 提供这些工具，无需先改动原 Ubuntu 的开发环境。

学校 Makefile 要求 `qemu-system-riscv64` 至少为 7.2。现有 Ubuntu 22.04 的本地软件包缓存提供 QEMU 6.2，因此不能直接使用该候选版本完成本次构建要求。

## 在 PowerShell 中操作

先打开 Docker Desktop，等待 Linux 引擎启动。

```powershell
docker version
docker info --format '{{.OSType}}'
```

预期同时看到 Client 和 Server，操作系统类型为 `linux`。

进入操作系统课程目录，以下命令中的相对路径均以它为起点。

```powershell
Set-Location 'D:\Study-Note\OperatingSystem'
```

检查容器工具版本。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Action check
```

编译并启动 xv6。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1
```

预期看到 `xv6 kernel is booting`、`init: starting sh` 和 `$` 提示符。`$` 属于 xv6 shell，此时输入的是 xv6 命令。

退出 QEMU 时，先按 `Ctrl+A`，松开后再按 `X`。容器随即退出，源码和构建结果保存在本机。

进入容器的 Linux shell。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Action shell
```

进入后当前目录是 `/xv6`，可以执行 `make`、查看源码或运行测试。这里的 shell 与 xv6 内部的 shell 属于不同环境。

选择 Shebang 项目启动、执行功能检查或自动演示。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Project shebang
& .\Lab\xv6-notes\Start-Xv6.ps1 -Project shebang -Action test
& .\Lab\xv6-notes\Start-Xv6.ps1 -Project shebang -Action demo
```

手动演示时，在 Shebang 项目的 xv6 shell 中依次执行。

```text
echo #!/echo INTERPRETER_OK > sbdemo
sbdemo hello xv6
```

预期解释器输出 `INTERPRETER_OK sbdemo hello xv6`。这里使用 echo 展示解释器收到的参数，内核本身不解释脚本正文。

`-Action test` 对 Intro 运行格式检查、官方 Dump/Dump2、补充测试和 Pingpong。对 Shebang 运行格式检查与 41 组功能用例。完整回归使用 `-Action regression`，其内容是学校的完整 usertests 与 crash 测试。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Project intro -Action regression
& .\Lab\xv6-notes\Start-Xv6.ps1 -Project shebang -Action regression
```

同一项目的两个 QEMU 会争用同一个 fs.img，启动交互环境或测试时保持每个项目只有一个 QEMU。

## Pingpong 设计

官方明确要求父进程向子进程发送 `ping`，子进程输出后回复 `pong`，父进程输出回复。程序加入 Makefile 的 UPROGS。还必须临时将管道容量改为 1 字节验证，随后恢复原值。

采用两条单向管道，分别表示父到子和子到父的通信方向。官方没有限定必须恰好使用一条管道。

```text
父进程 -- ping --> 子进程
父进程 <-- pong -- 子进程
```

`pipe(fd)` 创建管道，`fd[0]` 用于读取，`fd[1]` 用于写入。`fork()` 创建子进程，并让子进程继承父进程当前打开的文件描述符。

父子进程分别关闭不使用的两个管道端。接收者循环读取，累计收到 4 字节后才把消息作为完整字符串输出。缓冲区额外保留一字节用于字符串结尾的 `\0`。

短读是本实验的关键。管道是字节流，`read(fd, buf, 4)` 不保证返回 4。学校 `piperead()` 在读完当前可用字节后即可返回。当 PIPESIZE 为 1 时，接收端必须多次读取才能得到完整消息。

父进程完成交换后调用 `wait()`，回收子进程并检查其退出状态。异常路径关闭仍在使用的端点，避免另一方一直等待。

预期输出中的 PID 会随运行变化。

```text
5: got ping
4: got pong
```

可执行 Intro 一键功能检查，其中包含默认容量下的 Pingpong 自动检查。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Action test
```

该检查运行真实 QEMU，检查启动、echo、两行消息及其顺序、不同 PID，以及程序是否正常返回 shell。它是为本项目添加的检查，不是学校原有的 Pingpong 验收命令。

## 修改文件与调用关系

Pingpong 阶段的源码改动为两处，Dump 和 Dump2 的后续修改详见独立学习说明。

- `user/pingpong.c`，新增用户程序。
- `Makefile`，在 UPROGS 中加入 `$U/_pingpong`，让程序进入 xv6 文件系统镜像。

`main()` 先创建两条管道，再调用 `fork()` 分为父子两个执行路径。子进程通过 `read_full()` 接收 ping，输出后通过 `write_full()` 回复 pong。父进程发送、接收并输出，最后通过 `wait()` 回收子进程。

`read_full()` 累计每次 read 返回的实际字节数，直到接收完 4 字节。遇到提前 EOF 或错误时返回 -1。`write_full()` 用相同的累计方式处理写入结果。错误退出使用非零状态，父进程还检查子进程的退出状态。

`kernel/pipe.c` 仅在测试期间临时调整，当前内容与学校基线逐字节一致，PIPESIZE 为 512。

## 已实际执行的验证

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 容器工具版本与 QEMU 最低版本检查 | 通过 | `logs/environment.log` |
| 未修改源码 `make -j2 kernel/kernel fs.img` | 退出码 0 | `logs/baseline-build.log` |
| 基线 QEMU 启动及 echo | 通过 | `logs/baseline-boot.log` |
| `make fmt-check` | 退出码 0 | `logs/format-check.log` |
| PIPESIZE=512，3 个虚拟 CPU | 10 次通过 | `logs/pipe-512-initial-result.log` |
| PIPESIZE=1，3 个虚拟 CPU | 20 次通过 | `logs/pipe-1-result.log` |
| 恢复 PIPESIZE=512，3 个虚拟 CPU | 10 次通过 | `logs/pipe-512-restored-result.log` |
| 管道源码恢复 | 字节内容一致，记录 SHA-256 | `logs/pipe-restored.sha256` |
| Dump 官方测试 | 4/4 通过 | `logs/intro-official.log` |
| Dump2 官方测试 | 4/4 通过 | `logs/intro-official.log` |
| Dump2 补充测试 | 4 类通过 | `logs/dump2-extra-qemu.log` |
| 当前 Intro 内核的一键功能检查 | 全部通过，另含 Pingpong 10 次 | `logs/intro-recheck-*.log` |
| Intro 完整 usertests | ALL TESTS PASSED | `logs/intro-usertests.log` |
| Intro crash | 三类恢复检查通过 | `logs/intro-crash.log` |
| Shebang 功能 | 41/41 通过 | `logs/shebang-functional-result.log` |
| Shebang 完整 usertests | ALL TESTS PASSED | `logs/shebang-usertests.log` |
| Shebang crash | 三类恢复检查通过 | `logs/shebang-crash.log` |
| Shebang 启动入口与真实演示 | 通过 | `logs/shebang-recheck-*.log` 与 `logs/shebang-demo-qemu.log` |

每组还保留了对应的 build.log 和 qemu.log。构建命令为 `make -j2 -W kernel/pipe.c kernel/kernel fs.img`，其中 `-W kernel/pipe.c` 保证管道实现重新编译，避免只改源码但运行旧内核。QEMU 运行命令为 `make qemu CPUS=3`。

完整重现三组验证。

```powershell
& .\Lab\xv6-notes\Start-Xv6.ps1 -Action verify
```

此命令会临时把容量改为 1，完成后在 finally 中恢复原文件并重编内核。执行时不要同时编辑 `kernel/pipe.c`，也不要同时启动另一份使用同一 fs.img 的 QEMU。

这些是本机 Docker/QEMU 的实际结果。远程 GitHub Actions 状态需要另行核对，不能用本地通过代替远程 CI 已通过。部分通用用例会主动触发非法访问或磁盘满，因此日志中的 usertrap 或 out of blocks 本身不代表最终失败，应结合测试结果判断。

## 本阶段俄语答辩练习

**Вопрос: Почему вы используете два канала?**

Один канал передаёт ping от родителя к ребёнку, второй передаёт pong обратно. У каждого направления есть свой читатель, поэтому родитель не прочитает собственное сообщение.

中文：两条单向管道分别负责去程与回程，避免父进程读回自己写入的数据。

**Вопрос: Почему одного вызова read недостаточно?**

Канал передаёт поток байтов. Вызов read может вернуть меньше байтов, чем запрошено. Поэтому программа повторяет чтение, пока не получит все четыре байта.

中文：管道是字节流，一次读取可能只返回部分数据，必须累计读取完整消息。

**Вопрос: Что проверяет размер канала в один байт?**

Проверка показывает, что программа корректно обрабатывает частичное чтение и блокировку записи. После проверки исходный размер канала восстановлен.

中文：1 字节测试验证短读和阻塞写入的配合，完成后恢复原容量。

**Вопрос: Зачем закрывать неиспользуемые дескрипторы?**

После fork оба процесса наследуют дескрипторы каналов. Лишние концы нужно закрыть, чтобы не удерживать канал открытым и правильно обрабатывать EOF.

中文：fork 后父子都继承描述符，关闭不用的端点，才能正确释放资源并识别 EOF。

**Вопрос: Для чего родитель вызывает wait?**

Родитель ожидает завершения дочернего процесса, получает его код завершения и освобождает запись завершившегося процесса.

中文：wait 等待并回收子进程，同时获取其退出状态。

术语：进程 — процесс，管道 — канал，文件描述符 — файловый дескриптор，短读 — частичное чтение，系统调用 — системный вызов。

## 后续阶段与提交规则

Dump 已通过 `trapframe` 读取当前进程的 `s2` 到 `s11`，输出低 32 位，并通过学校 `dumptests`。Dump2 已完成完整 64 位返回、祖先权限、四类错误与安全写回。

Intro 文档将 Dump2 标为 `Часть 3*`，但没有解释星号。当前 `.github/workflows/UserTests.yml` 明确在 `lab-1` 上执行 `dumptests` 和 `dump2tests`，因此本项目将 Dump2 纳入 Intro 提交目标。

提交方式存在官方文档差异。Intro 文档写 fork 和精确名称 `lab-1`，通用提交流程要求 Private 仓库和 `lab-<slug>` 分支。按用户选择使用已创建的私有仓库，Intro 保留明确要求的 `lab-1`，Shebang 使用 `lab-shebang`。

两个 worktree 共享 Git 历史，但各自保留实验源码。两分支均从学校原始 main 派生，便于分别审阅。main 保持学校基线，实验修改通过各自 PR 交给教师审阅后再合并。

当前已完成分支推送和 PR 创建：[Intro PR #1](https://github.com/ivanstylish/os-course-xv6-riscv/pull/1)，[Shebang PR #2](https://github.com/ivanstylish/os-course-xv6-riscv/pull/2)。两个 PR 尚未合并，仓库保持私有。远程结果及首次超时复查见 [CI 复核记录](CI-复核记录.md)。

## 官方依据

- [Intro 要求](https://github.com/secs-dev/xv6-riscv/blob/57dc72da888497f03084262bcbb40eed04e83eb4/doc/lab/intro.md)
- [Docker 启动说明](https://github.com/secs-dev/xv6-riscv/blob/57dc72da888497f03084262bcbb40eed04e83eb4/doc/setup/linux.md)
- [构建要求](https://github.com/secs-dev/xv6-riscv/blob/57dc72da888497f03084262bcbb40eed04e83eb4/Makefile)
- [管道实现](https://github.com/secs-dev/xv6-riscv/blob/57dc72da888497f03084262bcbb40eed04e83eb4/kernel/pipe.c)
- [Intro 的 CI 验收配置](https://github.com/secs-dev/xv6-riscv/blob/57dc72da888497f03084262bcbb40eed04e83eb4/.github/workflows/UserTests.yml)
- [通用提交流程](https://github.com/secs-dev/os-course/blob/main/doc/process.md)

参考 PDF 尚未读取。本记录不对其内容作出推断。
