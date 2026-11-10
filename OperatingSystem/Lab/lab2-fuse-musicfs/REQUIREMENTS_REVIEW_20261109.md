# MusicFS 实验核对记录

核对日期：2026-11-09。依据：当前课程 FUSE 原文、libfuse 官方说明、pyfuse3 稳定版文档及工作区实际代码。本轮只审查和补充文档，没有修改产品逻辑。

## 结论

Python 方案符合公开说明：原文主动提到 Python bindings，没有 C-only 规定。对照已经确认的“本地 JSON、三类目录、只读、启动快照”选题，正常场景没有发现阻断演示的功能问题；有一个极端输入处理缺口，另有报告与提交说明需要完善。

原文短句：«Обратите внимание, что для данной библиотеки есть bindings для Python.» [课程来源](https://github.com/secs-dev/os-course/blob/main/lab/fuse/README.md)

## 要求和当前证据

| 核对项 | 当前状态 |
|---|---|
| 了解 libfuse，完成用户态文件系统 | 使用真实 libfuse3/pyfuse3 挂载，非普通目录复制脚本 |
| 自选主题并与老师确认 | 用户已明确表示 MusicFS 选题获同意；本轮没有联系老师或独立核验批准记录 |
| 通过文件系统接口提供功能 | `lookup/getattr/readdir/open/read/release`，支持普通 ls/stat/cp |
| 语言 | Python 绑定受到原文提示，无需因官方示例为 C 而重写 |
| 网络/外部服务 | 原文举例不等于必须联网；当前使用本地数据没有与公开条文冲突 |
| LLM 使用方法 | 报告源文件已说明用途、错误反馈和测试过程 |
| 生成的外部服务交互模块隔离 | 本项目没有外部服务交互模块，该具体条件没有实际对象 |

只读、BPM 识别、写文件、热更新、硬件性能测试、固定测试数量均没有在这份 FUSE README 中被列为统一必做项。当前只读和 JSON 规则来自选题范围，不应把自行选择的功能冒充课程统一要求。

## 已发现的缺口

### 1. 低优先级：极端 BPM 会泄漏 Decimal 异常

位置：[catalog.py](musicfs/catalog.py)，`bpm_group` 中的除法和异常处理。

复现：

```python
from decimal import Decimal
from musicfs.catalog import bpm_group
bpm_group(Decimal("1e1000001"))
```

本轮探针结果为 `decimal.Overflow`。代码只捕获 `InvalidOperation`，没有覆盖 Decimal 除法的 Overflow。JSON 可以表示这个有限正数，因而输入校验在极端值上不完整。正常音乐 BPM 不受影响；失败发生在挂载准备阶段，不会改写源音频。

建议最小修复：将 Overflow 一并转换为现有的 `ValueError`，补一个极端数回归场景。无需为此重构分类逻辑。本轮是检查任务，保留产品代码现状。

### 2. 报告仍是早期批次，不能直接代表最新完整状态

位置：[报告源文件](report_musicfs.typ)，限制部分仍说真实 MP3/FLAC 没有检查；现有 PDF 是 11 月 1 日生成的版本。

后来已加入 8 个真实 WAV/MP3 的文件读取检查。本轮再次通过，覆盖源内容哈希、三入口 inode、范围读取、只读拒绝和卸载。正式提交最新报告前，应将“真实 MP3 文件访问已验证”与“MP3 解码/播放、FLAC 未验证”分别写清，并重新生成 PDF。README 已有历史批次说明，所以旧报告不是伪造结果，但作为最新提交材料不够完整。

### 3. LLM 条款的范围需要准确表述

课程明确提到可生成“外部服务交互”代码。它没有在本页明确授权或禁止生成全部 FUSE 核心代码。因此不能把这句扩大为“所有核心代码由 LLM 生成都已得到课程批准”，也不能据此直接断言本项目违规。

实际开发中 LLM 参与了核心代码、测试和材料，报告已经如实说明。选题批准与 AI 使用范围批准是两件事；答辩前应按老师的实际规则确认该范围，并能独立解释代码。这项事项无法通过运行测试证明。

### 4. 本机样例不会自动随代码提交

`local-data/` 被 Git 忽略，音频通过 E 盘原路径读取。这保护了原始素材，但干净检出后不会自带 8 条本机清单或音乐文件。可复现提交应保留现有合成 WAV 生成器，并附去除私人路径的说明；不要把本机真实样例可用与任何人都可直接运行混为一谈。

## 实现限制与测试空白

- `forget` 不回收 inode：对固定、有限、挂载期间不删除的索引是明确的简化；若增加热更新，需要真正的 lookup/open 引用管理和缓存失效。
- 源库假定受信任且不在挂载期间修改内容；`resolve` 的路径检查不是针对恶意并发换链接的完整安全隔离。
- 首次启动和属性查询中仍有同步 stat/open；小规模本地样例可用，未进行慢盘或大库吞吐测试。
- 字节读取通过不代表听音、解码、BPM/调性正确。文件名标签仅为输入，未测量。
- 没有确认该班 FUSE 的具体 PR/私有仓库/邮件提交流程，不把 xv6 流程自动套用成 FUSE 的额外硬性要求。

## 本轮执行结果

1. `MUSICFS_INTEGRATION=1 python -m unittest discover -s tests -v`：30/30 通过，含 11 项真实挂载测试。完整日志：[audit-20261109-tests.log](evidence/audit-20261109-tests.log)。
2. `python tools/check_local_audio.py`：8 个真实文件，70,316,922 bytes（67.06 MiB）通过；三个入口一致，源文件内容/大小/修改时间未变，已卸载。结果：[validation.json](local-data/validation.json)。
3. 额外 BPM 探针发现上述 Overflow；它不属于现有 30 个已通过测试，不应被“30/30”掩盖。

## 查阅入口

- [libfuse 官方仓库](https://github.com/libfuse/libfuse/tree/master)
- [libfuse 官方 API 介绍](https://libfuse.github.io/doxygen/)
- [pyfuse3 关于 Python 绑定的说明](https://pyfuse3.readthedocs.io/en/stable/about.html)
- [pyfuse3 回调约定](https://pyfuse3.readthedocs.io/en/stable/operations.html)
- [完整学习笔记](FUSE_libfuse_学习笔记.md)

## 整理后的状态

报告源文件与 report_musicfs_final.pdf 已补充真实 WAV/MP3 读取证据。旧 PDF 的占用已释放并已清理，目录只保留新版正式 PDF。学习与答辩合并到 FUSE_libfuse_学习笔记.md，全文采用定义、对比和实现对应的中俄结构。极端 BPM 和 LLM 使用范围事项仍按上文说明。

## Формальная выборка / 正式组重评

正式清单已扩为 12 个（11 WAV＋1 MP3，101.72 MiB），新增四个带 BPM 文件名的伴奏循环，没有可信调性标签，key 留空。重新验证全部 36 个入口、144 次范围读取和 12 次复制；源内容、大小和修改时间未变。实测发现 EOF 前短读未补齐，已在 read 中修复并加入回归。现有完整回归 31/31 通过；12 个正式音频全部通过。第四节现采用正式组实测值，不再采用 s001 合成样例作为正式结果。证据：evidence/local-audio-summary.json、formal-validation.log、formal-short-read.log 和 tests.log。极端 BPM 的独立已知边界仍未修改。
