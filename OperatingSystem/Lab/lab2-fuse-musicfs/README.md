# MusicFS · FUSE 实验

MusicFS 把 JSON 中的音乐元数据组织成只读目录。三个分类入口读取同一份原始音频，不复制文件、不修改标签、不分析音频。

已在 WSL2 Ubuntu 中通过 **30 项测试，其中 11 项是真实挂载集成测试**，记录见 [evidence/tests.log](evidence/tests.log)。另已对本机选取的 **8 个真实音频（7 WAV＋1 MP3，约 67 MiB）**完成只读挂载与字节一致性验证；音频解码、播放器播放和 FLAC 尚未验证。

本项目不调用在线音乐平台或其他网络服务。JSON 保存分类元数据，音频文件保存实际内容；FUSE/pyfuse3 和 `os.pread` 是本地编程接口，不是网络服务 API。

## 1. 从这里开始

在 Windows 终端进入现有 Linux：

```powershell
wsl -d Ubuntu-Recovery
```

以下命令均在 Ubuntu 中执行：

```bash
cd /mnt/d/Study-Note/OperatingSystem/Lab/lab2-fuse-musicfs

# 首次安装；已安装的系统包无需重复安装。
sudo apt install fuse3 libfuse3-dev libattr1-dev pkg-config build-essential python3-dev python3-venv
python3 -m venv ~/.venvs/musicfs-lab
source ~/.venvs/musicfs-lab/bin/activate
python -m pip install -e .

# 生成三个有效的合成 WAV 和示例 JSON；为保护文件，不覆盖非空目录。
python tools/make_demo.py demo
mkdir -p ~/musicfs-mnt

# 前台运行；此终端用于观察日志。
python -m musicfs --metadata demo/metadata.json --source-root demo/audio ~/musicfs-mnt --debug
```

本次交付已生成 `demo/`，可直接使用；再次执行生成命令时换一个空输出目录。挂载点必须为空，不得与音频根目录互相包含，也不能是已有挂载。

第二个 Ubuntu 终端中查看：

```bash
ls -R ~/musicfs-mnt
stat ~/musicfs-mnt/by_bpm/120/s001__drum_loop.wav
stat ~/musicfs-mnt/by_key/A_minor/s001__drum_loop.wav
stat ~/musicfs-mnt/by_type/drum/s001__drum_loop.wav
sha256sum ~/musicfs-mnt/by_type/drum/s001__drum_loop.wav
sha256sum /mnt/d/Study-Note/OperatingSystem/Lab/lab2-fuse-musicfs/demo/audio/drums/drum_loop.wav

# 复制到挂载点外，读取是允许的。
cp ~/musicfs-mnt/by_type/drum/s001__drum_loop.wav /tmp/musicfs-copy.wav

# 应失败：Read-only file system。
touch ~/musicfs-mnt/new.wav

# 关闭使用该目录的程序，终端退出挂载目录，然后卸载。
cd ~
fusermount3 -u ~/musicfs-mnt
```

也可在运行 MusicFS 的终端按 Ctrl+C。不要删除仍在挂载的目录。

## 2. JSON 与分类规则

参考 [examples/metadata.json](examples/metadata.json)：

```json
[
  {"id": "s001", "path": "drums/drum_loop.wav", "bpm": 124.5, "key": "A_minor", "type": "drum"},
  {"id": "s002", "path": "songs/example.mp3", "bpm": null, "key": null, "type": "song"}
]
```

| 字段 | 约定 |
|---|---|
| `id` | 必填、唯一，1–64 个 ASCII 字母、数字、下划线或连字符 |
| `path` | 必填，相对于 `--source-root` 的 POSIX 文件路径，使用 `/` |
| `bpm` | 可缺失或为 null；否则为有限正数，以最近的 10 的倍数分类，中点向上 |
| `key` | 可缺失或为 null；否则为单个安全目录名，推荐统一用 `A_minor`、`C_major` 等标签 |
| `type` | 可缺失或为 null；否则为用途标签，例如 `drum`、`bass`、`vocal`、`song` |

`124.5 → 120`，`125 → 130`，`128 → 130`；缺失字段分别进入 `unknown`。小于 5 的正 BPM 会归入取值点 0，目录名是分组中心，不是原始 BPM。

音频格式保留在扩展名中，不与用途混合。系统直接读取字节，不依赖解码器，因此无需为 WAV、MP3、FLAC 编写不同读取函数；有效音频和元数据正确性由输入提供。

每个源音频仅有一条记录，硬链接或符号链接指向同一物理文件的重复记录也会拒绝。虚拟文件名为 `id__原文件名`，避免同名音频互相覆盖。标签不得为空、`.`、`..`，或含 `/`、`\`、NUL；虚拟名称最多 255 个 UTF-8 字节。

```text
by_bpm/120/s001__drum_loop.wav ─┐
by_key/A_minor/s001__drum_loop.wav ─┼─ 同一个虚拟 inode ─ 原始 drum_loop.wav
by_type/drum/s001__drum_loop.wav ─┘
```

三个路径共享一个**虚拟** inode；不要求它等于源文件所在文件系统的 inode。源音频不会新增物理硬链接。根目录下只生成有有效音频记录的分类；空目录库可正常挂载。

JSON 的格式、字段、重复记录和越界路径错误会阻止挂载。缺失或无权读取的源文件跳过并警告，其他记录仍可使用。启动后若源文件删除，新的打开失败；已经打开的文件描述符仍然可以读取。

## 3. 代码之间怎样联系

建议按此顺序读，详细讲解及俄语回答见 [学习与答辩](LEARNING_zh_ru.md)。

1. [catalog.py](musicfs/catalog.py)：校验 JSON，建立 `inode → Node` 表和目录的 `name → inode` 表。它不导入 FUSE，便于单独理解和测试。
2. [fs.py](musicfs/fs.py)：回调查询上述表，把 `open/read/release` 转成操作系统的只读打开、`pread`、关闭操作。
3. [__main__.py](musicfs/__main__.py)：校验挂载目录，设置 `ro`，调用挂载和 Trio 请求循环，最后清理。

这里没有通用存储层、插件或额外服务。测试使用 Python 自带的 `unittest`，无需 pytest。

## 4. 测试与证据

在已激活虚拟环境、项目根目录下运行：

```bash
# 19 项目录/回调测试；11 项真实挂载测试明确跳过。
python -m unittest discover -s tests -v

# 全部 30 项，包含真实挂载。仅操作 /tmp 中的临时合成音频。
MUSICFS_INTEGRATION=1 python -m unittest discover -s tests -v
```

测试包括：BPM 中点、错误输入、源路径越界、同名和重复源文件、多入口 inode、读取/EOF、50 次并发范围读取、8 类禁止修改操作、1,200 项目录遍历、Unicode、元数据快照与重新挂载、缺失源文件、SIGINT/SIGTERM 和可捕获异常清理。

- [完整测试结果](evidence/tests.log)
- [演示与 inode/哈希证据](evidence/demo.txt)
- [结构化演示结果](evidence/summary.json)
- [环境版本](evidence/environment.txt)及 [Python 包版本](evidence/python-packages.txt)
- [挂载读取日志](evidence/mount.log)
- [俄语报告源文件](report_musicfs.typ) / [PDF](report_musicfs.pdf)

## 5. 排错和边界

| 现象 | 处理 |
|---|---|
| `No module named pyfuse3` | 激活 Ubuntu 中的虚拟环境；不要用 Windows Python 启动 FUSE |
| 构建找不到头文件 | 检查 libfuse3-dev、libattr1-dev、python3-dev、pkg-config 和编译器 |
| `/dev/fuse` 不存在或无法访问 | 检查 Linux/FUSE 支持和当前用户权限，先解决环境问题 |
| 修改 JSON 后目录未改变 | 当前挂载使用启动快照，卸载后重新挂载 |
| 挂载点非空 | 选择独立空目录，不覆盖现有文件 |
| 卸载提示 busy | 关闭访问它的程序，让终端离开挂载目录，再卸载 |
| 进程被强制杀死，访问报连接错误 | 用 `fusermount3 -u 挂载点` 清理后重启；SIGKILL 无法执行 Python 清理逻辑 |

第一版假定挂载期间源音频内容保持不变，分类/文件索引一直保留到卸载。删除源文件的错误处理不等同于完整热更新。更新源库、移动文件或修改内容后请重新挂载。路径检查适用于本地受信任的音乐库；没有实现抵御恶意进程同时替换目录的沙箱。

常规测试使用合成 WAV，另已验证本地 WAV/MP3 的文件读取与哈希一致性；没有验证音频解码、播放器播放、FLAC 或大规模音乐库性能。没有建立远程提交、推送、联系老师或代替教师验收。

## 6. 本机真实音频演示

从 `E:\preset` 选择 6 个采样，从 `E:\project\AUTUMN` 选择 `I Know.wav` 与 `I Know.mp3`，总计 8 个、67.06 MiB。没有复制音频或改写标签；本地清单位于 [local-data/metadata.json](local-data/metadata.json)，验证结果见 [local-data/validation.json](local-data/validation.json)。`local-data/` 已忽略 Git 提交，源音频也不随代码提交。

三个旋律的 BPM/调性来自文件名，未进行音频测量；鼓、bass 和歌曲的 BPM/调性保持未知。`type` 是依据文件名和目录语境人工填写的用途标签。JSON 的 `metadata_source` 只用于说明来源，文件系统不依赖它。

Ubuntu 中运行：

```bash
cd /mnt/d/Study-Note/OperatingSystem/Lab/lab2-fuse-musicfs
source ~/.venvs/musicfs-lab/bin/activate
mkdir -p ~/musicfs-mnt
python -m musicfs --metadata local-data/metadata.json --source-root /mnt/e ~/musicfs-mnt --debug
```

`/mnt/e` 作为两个来源的公共根目录，只加载 JSON 中的 8 条记录，不扫描或展示整个 E 盘。修改清单后重新挂载即可。

可重复执行独立的真实音频检查：

```bash
python tools/check_local_audio.py
```

该脚本限制为指定两处目录、最多 8 个文件及 100 MiB；逐一比较三个虚拟入口的 inode、完整 SHA-256、首部/中间/尾部/EOF 读取，验证写入被拒绝和卸载完成。验证前后源文件内容哈希、大小和修改时间一致。它只测试文件字节访问，不启动播放器或解码器。

现有 PDF 保留 11 月 1 日合成样例测试批次的记录；本轮真实音频补充以本节和 `local-data/validation.json` 为准。

## 7. 官方资料

- [课程 FUSE 要求](https://github.com/secs-dev/os-course/blob/main/lab/fuse/README.md)
- [libfuse](https://github.com/libfuse/libfuse) / [官方 API 文档](https://libfuse.github.io/doxygen/)
- [pyfuse3 概念与生命周期](https://pyfuse3.readthedocs.io/en/stable/general.html)
- [pyfuse3 回调接口](https://pyfuse3.readthedocs.io/en/stable/operations.html)
- [官方只读示例](https://pyfuse3.readthedocs.io/en/stable/example.html)
- [课程报告规范](https://github.com/secs-dev/os-course/blob/main/doc/report.md)
