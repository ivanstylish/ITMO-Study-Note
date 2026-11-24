"""把 FUSE 请求转换为目录索引查询，以及对源音频的只读系统调用"""

import errno
from itertools import count
import logging
import os
import stat

import pyfuse3
import trio


class MusicFS(pyfuse3.Operations):
    enable_writeback_cache = False

    def __init__(self, catalog):
        super().__init__()
        self.catalog = catalog
        self.handles = {}  # fd -> inode：inode 标识文件，fd 标识本次打开的资源
        # 内存句柄使用独立编号区间，避免与操作系统分配的音频 fd 重叠
        self.info_handles = {}
        self.next_info_handle = count(1 << 32)

    # 查找虚拟节点
    def node(self, inode):
        try:
            return self.catalog.nodes[inode]
        except KeyError:
            raise pyfuse3.FUSEError(errno.ENOENT) from None

    # 获取安全源路径
    def source_path(self, node):
        try:
            return self.catalog.checked_path(node.path)
        except (ValueError, RuntimeError):
            raise pyfuse3.FUSEError(errno.EACCES) from None
        except OSError as exc:
            raise pyfuse3.FUSEError(exc.errno) from exc

    # 获取文件属性
    async def getattr(self, inode, ctx=None):
        """向内核提供属性；目录属性由索引合成，音频属性取自源文件。"""
        node = self.node(inode)
        entry = pyfuse3.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = entry.attr_timeout = 0  # 演示时每次重新查询属性，及时发现源文件消失
        entry.st_uid, entry.st_gid = os.getuid(), os.getgid()
        entry.st_blksize = 4096
        if node.path is None:
            # 第一种情况：虚拟目录
            if node.is_directory:
                entry.st_mode = stat.S_IFDIR | 0o555
                entry.st_nlink = 2 + sum(self.node(child).is_directory for child in node.children.values())
                entry.st_size = entry.st_blocks = 0
            # 第二种情况：内存info文件
            else:
                entry.st_mode = stat.S_IFREG | 0o444
                entry.st_nlink = node.links
                entry.st_size = len(node.content)
                entry.st_blocks = (entry.st_size + 511) // 512
            entry.st_atime_ns = entry.st_mtime_ns = entry.st_ctime_ns = self.catalog.timestamp
            # 第三种情况：真实音频文件
        else:
            try:
                try:
                    info = os.stat(self.source_path(node))
                except FileNotFoundError:
                    # 源文件名删除后，旧 fd 仍有效，用 fstat 保证已有打开仍能读取
                    fh = next((fd for fd, ino in self.handles.items() if ino == inode), None)
                    if fh is None:
                        raise
                    info = os.fstat(fh)
            except OSError as exc:
                raise pyfuse3.FUSEError(exc.errno) from exc
            if not stat.S_ISREG(info.st_mode):
                raise pyfuse3.FUSEError(errno.EINVAL)
            entry.st_mode = stat.S_IFREG | 0o444
            entry.st_nlink = node.links
            entry.st_size, entry.st_blocks = info.st_size, info.st_blocks
            entry.st_atime_ns = info.st_atime_ns
            entry.st_mtime_ns = info.st_mtime_ns
            entry.st_ctime_ns = info.st_ctime_ns
        return entry

    # 根据名字查找 inode
    async def lookup(self, parent_inode, name, ctx=None):
        """把一个目录项解析为文件对象，再返回该对象的属性"""
        parent = self.node(parent_inode)
        if not parent.is_directory:
            raise pyfuse3.FUSEError(errno.ENOTDIR)
        if name == b".":
            inode = parent_inode
        elif name == b"..":
            inode = parent.parent
        else:
            try:
                # 内核逐级传入“父 inode + 名字”，无需在这里重新解析完整路径
                inode = parent.children[name]
            except KeyError:
                raise pyfuse3.FUSEError(errno.ENOENT) from None
        return await self.getattr(inode, ctx)

    # 打开目录
    async def opendir(self, inode, ctx=None):
        """虚拟目录没有底层目录 fd，直接用 inode 作为目录句柄"""
        if not self.node(inode).is_directory:
            raise pyfuse3.FUSEError(errno.ENOTDIR)
        return inode

    # 列出目录内容
    async def readdir(self, fh, start_id, token):
        # position 是续读位置，不是音频字节偏移；固定索引使分页稳定
        directory = self.node(fh)
        for position, (name, inode) in enumerate(directory.children.items(), 1):
            if position <= start_id:
                continue
            try:
                entry = await self.getattr(inode)
            except pyfuse3.FUSEError as exc:
                if exc.errno == errno.ENOENT:
                    continue
                raise
            if not pyfuse3.readdir_reply(token, name, entry, position):
                # 内核目录缓冲区已满，下次从上一次成功返回的位置继续。
                break

    async def open(self, inode, flags, ctx=None):
        # 除 ro 挂载外，回调也拒绝写入，源文件始终以 O_RDONLY 打开。
        if flags & os.O_ACCMODE != os.O_RDONLY or flags & (os.O_TRUNC | os.O_APPEND):
            raise pyfuse3.FUSEError(errno.EROFS)
        node = self.node(inode)
        if node.is_directory:
            raise pyfuse3.FUSEError(errno.EISDIR)
        if node.content is not None:
            fh = next(self.next_info_handle)
            self.info_handles[fh] = node.content
            return pyfuse3.FileInfo(fh=fh)
        try:
            fd = os.open(self.source_path(node), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise pyfuse3.FUSEError(errno.EINVAL)
            except BaseException:
                os.close(fd)
                raise
        except OSError as exc:
            raise pyfuse3.FUSEError(exc.errno) from exc
        self.handles[fd] = inode
        logging.debug("open inode=%s fh=%s", inode, fd)
        return pyfuse3.FileInfo(fh=fd)

    # 读取文件字节
    async def read(self, fh, off, size):
        info_content = self.info_handles.get(fh)
        if info_content is None and fh not in self.handles:
            raise pyfuse3.FUSEError(errno.EBADF)
        if off < 0 or size < 0:
            raise pyfuse3.FUSEError(errno.EINVAL)
        if info_content is not None:
            # st_size 与 read 都使用同一份 UTF-8 字节快照，切片自然处理偏移和 EOF
            return info_content[off:off + size]
        data = bytearray()
        try:
            # 底层可在 EOF 前短读；FUSE 要求补齐请求，只有真正 EOF 才返回短结果
            while len(data) < size:
                chunk = await trio.to_thread.run_sync(os.pread, fh, size - len(data), off + len(data))
                if not chunk:
                    break
                data.extend(chunk)
        except OSError as exc:
            raise pyfuse3.FUSEError(exc.errno) from exc
        logging.debug("read fh=%s offset=%s size=%s returned=%s", fh, off, size, len(data))
        return bytes(data)

    # 关闭文件句柄
    async def release(self, fh):
        if self.info_handles.pop(fh, None) is not None:
            return
        # 最后一个引用关闭时才释放 fd；退出清理还会兜底关闭未释放的 fd
        if fh in self.handles:
            del self.handles[fh]
            try:
                os.close(fh)
            except OSError as exc:
                raise pyfuse3.FUSEError(exc.errno) from exc

    async def releasedir(self, fh):
        # 目录句柄就是 inode，没有额外打开的 OS 资源需要关闭
        pass

    # 处理 inode 引用释放通知
    async def forget(self, inode_list):
        # shortcut: 固定索引保留至卸载；加入热更新/节点回收时再维护 lookup 引用计数
        pass

    def close(self):
        for fh in list(self.handles):
            try:
                os.close(fh)
            except OSError:
                logging.exception("could not close fh=%s", fh)
        self.handles.clear()
        self.info_handles.clear()
