"""读取本地 JSON，建立虚拟目录和 inode 索引；本模块不依赖 FUSE。"""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
import logging
from pathlib import Path, PurePosixPath
import re
import stat
import time


def label(value):
    """分类标签只能占一个目录项，不能借斜杠或 .. 逃出分类目录。"""
    if value is None:
        return "unknown"
    if not isinstance(value, str) or not value.strip():
        raise ValueError("category must be a non-empty string or null")
    if value in (".", "..") or any(c in value for c in "/\\\0"):
        raise ValueError(f"unsafe category: {value!r}")
    if len(value.encode("utf-8")) > 255:
        raise ValueError("category is longer than 255 bytes")
    return value


def bpm_group(value):
    if value is None:
        return "unknown"
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError("bpm must be a positive number or null")
    number = Decimal(str(value))
    if not number.is_finite() or number <= 0:
        raise ValueError("bpm must be finite and positive")
    try:
        # 125 必须归入 130；Decimal 避免 round() 的中点取偶规则。
        return str(int((number / 10).quantize(Decimal(1), rounding=ROUND_HALF_UP)) * 10)
    except InvalidOperation:
        raise ValueError("bpm is too large") from None


@dataclass
class Node:
    # path=None 表示虚拟目录；children 保存“文件名 -> 子节点 inode”。
    inode: int
    parent: int
    name: bytes
    path: Path | None = None
    children: dict[bytes, int] = field(default_factory=dict)
    links: int = 0


class Catalog:
    """目录项引用节点：三个分类入口共享同一个音频节点，不复制音频。"""

    def __init__(self, metadata, source_root):
        self.source_root = Path(source_root).resolve(strict=True)
        if not self.source_root.is_dir():
            raise ValueError("source root must be a directory")
        self.timestamp = time.time_ns()
        self.nodes = {1: Node(1, 1, b"")}  # FUSE 根 inode 为 1，根的父目录仍是自己。
        self.warnings = []
        self.file_count = 0
        with open(metadata, encoding="utf-8") as stream:
            records = json.load(stream, parse_float=Decimal)
        if not isinstance(records, list):
            raise ValueError("metadata must be a JSON array")

        ids, paths, physical_files = set(), set(), set()
        for position, record in enumerate(records, 1):
            try:
                if not isinstance(record, dict):
                    raise ValueError("record must be an object")
                record_id = record.get("id")
                if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", record_id):
                    raise ValueError("id must contain 1-64 ASCII letters, digits, '_' or '-'")
                if record_id in ids:
                    raise ValueError(f"duplicate id: {record_id}")
                ids.add(record_id)
                relative = record.get("path")
                if not isinstance(relative, str) or not relative or "\0" in relative or "\\" in relative:
                    raise ValueError("path must be a relative POSIX path")
                parts = PurePosixPath(relative)
                if parts.is_absolute() or ".." in parts.parts or not parts.name:
                    raise ValueError("absolute paths and '..' are forbidden")
                path = self.source_root / relative
                resolved = self.checked_path(path)
                if resolved in paths:
                    raise ValueError(f"duplicate source path: {relative}")
                paths.add(resolved)
                groups = (bpm_group(record.get("bpm")), label(record.get("key")), label(record.get("type")))
                name = f"{record_id}__{parts.name}".encode("utf-8")
                if len(name) > 255:
                    raise ValueError("virtual filename is longer than 255 bytes")
                try:
                    info = resolved.stat()
                    if not stat.S_ISREG(info.st_mode):
                        raise ValueError("source must be a regular file")
                    with open(resolved, "rb"):
                        pass
                except OSError as exc:
                    message = f"record {position}: skipped {relative}: {exc.strerror}"
                    self.warnings.append(message)
                    logging.warning(message)
                    continue
                # 不同路径可能通过硬链接/符号链接引用同一物理文件，不能只比较路径。
                identity = (info.st_dev, info.st_ino)
                if identity in physical_files:
                    raise ValueError("duplicate physical file (hard link or symlink alias)")
                physical_files.add(identity)
                node = self._new_node(1, name, path)
                # 音频节点只创建一次；每个分类目录仅增加指向它的目录项。
                for category, group in zip(("by_bpm", "by_key", "by_type"), groups):
                    parent = self._directory(1, category)
                    directory = self._directory(parent, group)
                    self.nodes[directory].children[name] = node.inode
                    node.links += 1
                self.file_count += 1
            except ValueError as exc:
                raise ValueError(f"record {position}: {exc}") from exc

        for node in self.nodes.values():
            node.children = dict(sorted(node.children.items()))

    def checked_path(self, path):
        # 先解析符号链接，再检查边界，防止链接目标位于源目录之外。
        resolved = Path(path).resolve()
        if not resolved.is_relative_to(self.source_root):
            raise ValueError("source path escapes source root")
        return resolved

    def _new_node(self, parent, name, path=None):
        inode = len(self.nodes) + 1
        node = Node(inode, parent, name, path)
        self.nodes[inode] = node
        return node

    def _directory(self, parent, name):
        name = name.encode("utf-8")
        children = self.nodes[parent].children
        if name not in children:
            children[name] = self._new_node(parent, name).inode
        return children[name]
