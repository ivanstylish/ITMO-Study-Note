# 远程 CI 复核记录

首次检查：2026-10-17。继续诊断：2026-10-19。时间均按莫斯科时间记录。

## 当前提交

| 项目 | PR | 提交 |
| --- | --- | --- |
| Intro | [PR #1](https://github.com/ivanstylish/os-course-xv6-riscv/pull/1) | `f9fde02e243e9e0192609c65449e13410d6ea9ea` |
| Shebang | [PR #2](https://github.com/ivanstylish/os-course-xv6-riscv/pull/2) | `2de5e7855d6317b50f88015b80bc4a8ad2908a56` |

## 10 月 17 日初始验证

- Shebang 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013780793) 与 [Linux/macOS 工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013780786) 均成功，包括完整 usertests 和三项 crash。
- Intro 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013779812) 成功，包括官方 Dump、Dump2、快速与完整通用测试。
- Intro 的 [Linux/macOS 工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013779816) 首次运行中，macOS 成功，Linux 的格式、构建及完整 usertests 成功。crash 的日志恢复成功，随后孤儿文件测试等待 `wait` 输出标记 30 秒超时。

失败片段保存在 [intro-ci-attempt1-crash.log](logs/intro-ci-attempt1-crash.log)。这是测试输出中的字符串 `wait`，不是 `wait()` 系统调用。测试尚未进入该组的强制终止与孤儿回收阶段，不能据此断言回收逻辑失败。

## 对照与复查

早期 Intro 提交 `6827c0674e915be863641db0aeb299e42bf86621` 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013720226) 和 [通用工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013720127) 均成功。该提交与首次超时提交 `3613919` 之间只修改了 `REPORT.md`、`report.typ` 和 PDF，当时实验执行源码相同。

针对首次失败，本地再次使用固定课程镜像执行 `python3 test-xv6.py crash`，退出码为 0，三组检查均为 OK。记录见 [intro-ci-followup-crash.log](logs/intro-ci-followup-crash.log)。此前的首次本地验证日志仍然保留。

对失败工作流原样重跑后，同一提交的 Linux 任务再次在孤儿文件就绪标记处超时，完整 usertests 和日志恢复仍通过。第二次失败片段见 [intro-ci-attempt2-crash.log](logs/intro-ci-attempt2-crash.log)。因此当时的 Intro 通用 CI 尚未通过，后续使用独立诊断采集缺失输出。

隔离的 `codex/intro-crash-diagnostics` 分支从原 Intro 提交派生，首轮保持实现及原版驱动不变，采集原始 QEMU 输出。独立诊断运行不等同于实验 PR 的 CI 通过。

2026-10-19 已完成诊断工作流的 Python 静态编译检查，并将提交 `571c2ecd745eadb437fbe04acc3cfc63e85ddb2b` 推送到诊断分支。[原始输出诊断任务](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39311029246)依次运行学校原版 `forphan`、`crash`、`crash`，逐场打印并保存 `test-xv6.out`，无论成功或失败均上传诊断记录。

## 10 月 19 日复现与修复

首轮诊断的三场均真实输出了 `$ wait for kill and reclaim 31`，随后仍报告匹配 `wait` 失败。原始输入回显在 `init: starting sh` 之前出现，后续 shell 提示符与程序消息落在同一行。`re.match('wait', line)` 只从行首匹配，因此误报失败。记录见 [原版驱动诊断日志](logs/intro-ci-20261019-diagnostics.log)。这三次复现明确证实了启动同步缺陷。10 月 17 日两轮没有保存原始输出，不能逐次证明当时的字符串布局。

修复仅把 `QEMU.__init__()` 的固定 `time.sleep(1)` 改为 `self.monitor(r'^\$ ', timeout=30)`。输出缓冲区先初始化，再等待没有换行的 shell 提示符。先前读取到的恢复标记仍保留，后续恢复检查可继续匹配。原用例断言、功能检查的超时及 C/汇编测试均保留，新增启动就绪等待单独以 30 秒为限。

| 相同的三场诊断 | 提交 | 结果 |
| --- | --- | --- |
| 原版驱动，`forphan/crash/crash` | `571c2ec` | 三场返回码均为 1，原始输出均有 `$ wait...` |
| 等待 shell 后，`forphan/crash/crash` | `363b3ee` | 三场返回码均为 0，原有断言全部通过 |

修复后的 [同场对照](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39311769440)和 [完整 Linux/macOS CI](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39311769431)均成功。两次完整 crash 各有三项 OK，覆盖日志、孤儿文件和孤儿目录恢复。日志见 [修复后远程诊断](logs/intro-ci-20261019-shell-ready.log)。

本地也重新执行了两个项目的 crash，均退出 0、三项 OK，记录为 [Intro](logs/intro-shell-ready-local-crash.log) 和 [Shebang](logs/shebang-shell-ready-local-crash.log)。相同修复已进入两个实验分支。两份报告清楚列出 Python 驱动改动，报告中的原始本地测试表与后续远程结果分别记录。

## 首次同步修复后的远程检查

| 项目 | 工作流 | 当前状态 |
| --- | --- | --- |
| Intro，`3aa7cad` | [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312963461) | 失败，第二处命令回显提示符竞态，见下文 |
| Intro，`3aa7cad` | [Linux/macOS](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312963930) | 成功，完整 usertests 与 crash 通过 |
| Shebang，`2de5e78` | [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312967552) | 成功 |
| Shebang，`2de5e78` | [Linux/macOS](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312967955) | 成功，完整 usertests 与 crash 通过 |

## Intro 独立测试驱动的提示符处理

Intro 的 UserTests 在官方 Dump 4/4 通过后，启动 Dump2 时出现 `Assertion failed: '$ dump2tests' != 'dump2tests'`。这是进入 Dump2 功能检查之前的命令回显比较失败，记录见 [失败片段](logs/intro-suite-prompt-ci-failure.log)。`ci/test/` 是另一套主机驱动，与前述 `test-xv6.py` 独立。它一次写入两个换行，并假定提示符一定出现在第一条程序结果之前。shell 提示符若先于命令回显到达，正确回显就会带有 `$ `。

修复让 `Xv6.run()` 只允许命令前出现完整的 `$ ` 前缀，并使用 `re.escape()` 与完整匹配保持命令本体精确。`SimpleSuite` 的首条输出允许带提示符或不带提示符。空行断言、后续功能消息、寄存器预期值、C/汇编测试和时限均未修改。

新增 [主机驱动回归源码](D:/Study-Note/OperatingSystem/Lab/xv6-intro/ci/test/test_prompt_handling.py) 包含四组检查，覆盖合法提示符位置、命令字面量、错误命令及分隔行拒绝、错误寄存器值拒绝。原驱动运行该回归有三组失败，修复后四组均通过，`run.sh` 现先执行回归再执行学校原有套件。真实 QEMU 下，官方 Dump/Dump2 按正序三次、倒序一次执行，32 项全部通过。接入入口后又完整执行一次，8 项全部通过。

证据保留为 [修复前](logs/intro-suite-prompt-before.log)、[主机回归](logs/intro-suite-prompt-after-unit.log)、[正序第 1 次](logs/intro-suite-prompt-after-1.log)、[第 2 次](logs/intro-suite-prompt-after-2.log)、[第 3 次](logs/intro-suite-prompt-after-3.log)、[倒序](logs/intro-suite-prompt-after-4.log) 和 [入口整体验证](logs/intro-suite-prompt-integrated.log)。对应修改及报告已提交为 `f9fde02`。

## 最终提交的远程检查

| 项目 | 工作流 | 当前状态 |
| --- | --- | --- |
| Intro，`f9fde02` | [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39315287210) | 成功，主机回归、Lab1、快速与完整通用套件通过 |
| Intro，`f9fde02` | [Linux/macOS](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39315287212) | 成功，Linux 完整 usertests 与 crash 通过 |
| Shebang，`2de5e78` | [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312967552) | 成功 |
| Shebang，`2de5e78` | [Linux/macOS](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39312967955) | 成功 |

最终核对时间为 2026-10-19 23:05:10 莫斯科时间。四条工作流均为 `completed / success`，逐 job 和步骤状态保存在 [JSON 快照](logs/remote-ci-final.json)。Intro 的 [Lab1 远程日志](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39315287210/job/118275047486) 确认新增主机回归 4 项、Dump 4/4、Dump2 4/4 全通过。该工作流的 Lab2 与 Lab3 按原分支规则跳过，没有将其记为功能通过。

两份源码工作目录在最终提交后均无未提交修改，`main` 仍是学校基线。仓库保持私有，两项 PR 均未合并，按用户要求没有发送教师邀请。这里的远程检查通过不代表教师已经验收。
