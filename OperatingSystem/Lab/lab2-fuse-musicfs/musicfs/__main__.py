"""检查输入 -> 加载目录索引 -> 挂载并处理请求 -> 卸载和关闭资源。"""

import argparse
import logging
import os
from pathlib import Path
import signal

import pyfuse3
import trio

from .catalog import Catalog
from .fs import MusicFS


def validate_mountpoint(mountpoint, source_root):
    mountpoint = Path(mountpoint).resolve(strict=True)
    if not mountpoint.is_dir() or os.path.ismount(mountpoint):
        raise ValueError("mountpoint must be an unmounted directory")
    if mountpoint.is_relative_to(source_root) or source_root.is_relative_to(mountpoint):
        # 避免挂载遮住源库，或从源库递归访问回自己的挂载点。
        raise ValueError("mountpoint and source root must not contain each other")
    if any(mountpoint.iterdir()):
        raise ValueError("mountpoint must be empty")
    return mountpoint


async def serve():
    async def stop_on_signal():
        with trio.open_signal_receiver(signal.SIGINT, signal.SIGTERM) as signals:
            async for received in signals:
                logging.info("received signal %s; stopping", received)
                pyfuse3.terminate()
                return

    async with trio.open_nursery() as nursery:
        # 一个任务等待退出信号，主任务持续处理内核的文件请求。
        nursery.start_soon(stop_on_signal)
        await pyfuse3.main()
        nursery.cancel_scope.cancel()


def main():
    parser = argparse.ArgumentParser(description="MusicFS: read-only audio categories from JSON")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("mountpoint", type=Path)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(levelname)s %(message)s")
    try:
        catalog = Catalog(args.metadata, args.source_root)
        mountpoint = validate_mountpoint(args.mountpoint, catalog.source_root)
        if args.metadata.resolve().is_relative_to(mountpoint):
            raise ValueError("metadata must be outside mountpoint")
    except (ValueError, OSError, RuntimeError) as exc:
        parser.error(str(exc))

    filesystem = MusicFS(catalog)
    options = set(pyfuse3.default_options) | {"ro", "fsname=MusicFS"}
    # default_options 保留内核权限检查，ro 在挂载层禁止修改。
    try:
        pyfuse3.init(filesystem, str(mountpoint), options)
    except (OSError, RuntimeError) as exc:
        parser.error(f"could not mount: {exc}")
    logging.info("mounted %s files at %s", catalog.file_count, mountpoint)
    try:
        trio.run(serve)
    finally:
        # 即使请求循环抛异常，也尝试卸载，并关闭全部源文件句柄。
        try:
            pyfuse3.close(unmount=True)
        finally:
            filesystem.close()
    logging.info("unmounted; all source handles closed")


if __name__ == "__main__":
    main()
