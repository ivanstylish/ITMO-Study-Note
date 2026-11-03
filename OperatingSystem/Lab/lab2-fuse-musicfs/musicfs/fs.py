"""把 FUSE 请求转换为目录索引查询，以及对源音频的只读系统调用。"""

import errno
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
        self.handles = {}  # fd -> inode：inode 标识文件，fd 标识本次打开的资源。

    def node(self, inode):
        try:
            return self.catalog.nodes[inode]
        except KeyError:
            raise pyfuse3.FUSEError(errno.ENOENT) from None

    def source_path(self, node):
        try:
            return self.catalog.checked_path(node.path)
        except (ValueError, RuntimeError):
            raise pyfuse3.FUSEError(errno.EACCES) from None
        except OSError as exc:
            raise pyfuse3.FUSEError(exc.errno) from exc

    async def getattr(self, inode, ctx=None):
        node = self.node(inode)
        entry = pyfuse3.EntryAttributes()
        entry.st_ino = inode
        entry.generation = 0
        entry.entry_timeout = entry.attr_timeout = 0  # 演示时每次重新查询属性，及时发现源文件消失。
        entry.st_uid, entry.st_gid = os.getuid(), os.getgid()
        entry.st_blksize = 4096
        if node.path is None:
            entry.st_mode = stat.S_IFDIR | 0o555
            entry.st_nlink = 2 + sum(self.node(child).path is None for child in node.children.values())
            entry.st_size = entry.st_blocks = 0
            entry.st_atime_ns = entry.st_mtime_ns = entry.st_ctime_ns = self.catalog.timestamp
        else:
            try:
                try:
                    info = os.stat(self.source_path(node))
                except FileNotFoundError:
                    # 源文件名删除后，旧 fd 仍有效；用 fstat 保证已有打开仍能读取。
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

    async def lookup(self, parent_inode, name, ctx=None):
        parent = self.node(parent_inode)
        if parent.path is not None:
            raise pyfuse3.FUSEError(errno.ENOTDIR)
        if name == b".":
            inode = parent_inode
        elif name == b"..":
            inode = parent.parent
        else:
            try:
                # 内核逐级传入“父 inode + 名字”，无需在这里重新解析完整路径。
                inode = parent.children[name]
            except KeyError:
                raise pyfuse3.FUSEError(errno.ENOENT) from None
        return await self.getattr(inode, ctx)

    async def opendir(self, inode, ctx=None):
        if self.node(inode).path is not None:
            raise pyfuse3.FUSEError(errno.ENOTDIR)
        return inode

    async def readdir(self, fh, start_id, token):
        # position 是续读位置，不是音频字节偏移；固定索引使分页稳定。
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
        if node.path is None:
            raise pyfuse3.FUSEError(errno.EISDIR)
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

    async def read(self, fh, off, size):
        if fh not in self.handles:
            raise pyfuse3.FUSEError(errno.EBADF)
        if off < 0 or size < 0:
            raise pyfuse3.FUSEError(errno.EINVAL)
        try:
            # pread 不改变共享文件位置；阻塞读取交给工作线程，不阻塞 Trio 请求循环。
            data = await trio.to_thread.run_sync(os.pread, fh, size, off)
        except OSError as exc:
            raise pyfuse3.FUSEError(exc.errno) from exc
        logging.debug("read fh=%s offset=%s size=%s returned=%s", fh, off, size, len(data))
        return data

    async def release(self, fh):
        # 最后一个引用关闭时才释放 fd；退出清理还会兜底关闭未释放的 fd。
        if fh in self.handles:
            del self.handles[fh]
            try:
                os.close(fh)
            except OSError as exc:
                raise pyfuse3.FUSEError(exc.errno) from exc

    async def releasedir(self, fh):
        # 目录句柄就是 inode，没有额外打开的 OS 资源需要关闭。
        pass

    async def forget(self, inode_list):
        # shortcut: 固定索引保留至卸载；加入热更新/节点回收时再维护 lookup 引用计数。
        pass

    def close(self):
        for fh in list(self.handles):
            try:
                os.close(fh)
            except OSError:
                logging.exception("could not close fh=%s", fh)
        self.handles.clear()
