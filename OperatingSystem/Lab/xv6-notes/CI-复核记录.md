# 远程 CI 复核记录

核对日期：2026-10-17，莫斯科时间。

## 当前提交

| 项目 | PR | 提交 |
| --- | --- | --- |
| Intro | [PR #1](https://github.com/ivanstylish/os-course-xv6-riscv/pull/1) | `3613919a001fdbf0608e5eba9a15868ad6966e15` |
| Shebang | [PR #2](https://github.com/ivanstylish/os-course-xv6-riscv/pull/2) | `7003674026cbea5eb38316aa017935c4d28efaaf` |

## 已观察到的结果

- Shebang 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013780793) 与 [Linux/macOS 工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013780786) 均成功，包括完整 usertests 和三项 crash。
- Intro 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013779812) 成功，包括官方 Dump、Dump2、快速与完整通用测试。
- Intro 的 [Linux/macOS 工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013779816) 首次运行中，macOS 成功，Linux 的格式、构建及完整 usertests 成功。crash 的日志恢复成功，随后孤儿文件测试等待 `wait` 输出标记 30 秒超时。

失败片段保存在 [intro-ci-attempt1-crash.log](logs/intro-ci-attempt1-crash.log)。这是测试输出中的字符串 `wait`，不是 `wait()` 系统调用。测试尚未进入该组的强制终止与孤儿回收阶段，不能据此断言回收逻辑失败。

## 对照与复查

早期 Intro 提交 `6827c0674e915be863641db0aeb299e42bf86621` 的 [UserTests](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013720226) 和 [通用工作流](https://github.com/ivanstylish/os-course-xv6-riscv/actions/runs/39013720127) 均成功。该提交与当前提交之间只修改了 `REPORT.md`、`report.typ` 和 PDF，实验执行源码相同。

针对首次失败，本地再次使用固定课程镜像执行 `python3 test-xv6.py crash`，退出码为 0，三组检查均为 OK。记录见 [intro-ci-followup-crash.log](logs/intro-ci-followup-crash.log)。此前的首次本地验证日志仍然保留。

对失败工作流原样重跑后，同一提交的 Linux 任务再次在孤儿文件就绪标记处超时，完整 usertests 和日志恢复仍通过。第二次失败片段见 [intro-ci-attempt2-crash.log](logs/intro-ci-attempt2-crash.log)。因此当前 Intro 通用 CI 尚未通过，不能用早期提交或本地成功代替当前结果。

已建立隔离的 `codex/intro-crash-diagnostics` 分支，采集原始 QEMU 输出。诊断从当前 Intro 提交派生，不修改实验实现、官方测试、两个实验 PR 或测试超时。独立诊断运行不等同于实验 PR 的 CI 通过。

## 证据边界

远程首次失败没有上传 `test-xv6.out`，因此无法从现有记录区分启动、命令接收、程序执行或文件操作在哪一步没有完成。学校测试器采用固定 1 秒启动等待，匹配标记时使用行首匹配，停止 QEMU 时没有显式等待退出确认。这些是源码中可观察到的时序风险，尚未证实是本次超时原因。

即使原样复跑通过，也应记录“复跑通过，首次超时原因未确认”，不能据此声称已证实 GitHub 负载或学校脚本是根因。报告中的测试表明确记载本地验证结果，与远程 CI 结果分别记录。
