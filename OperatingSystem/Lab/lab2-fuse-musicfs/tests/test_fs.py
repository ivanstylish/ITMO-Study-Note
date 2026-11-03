import errno
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pyfuse3
import trio

from musicfs.catalog import Catalog
from musicfs.fs import MusicFS
from musicfs.__main__ import validate_mountpoint


class CallbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "audio"
        self.root.mkdir()
        self.data = bytes(range(256)) * 100
        self.source = self.root / "loop.wav"
        self.source.write_bytes(self.data)
        metadata = self.base / "metadata.json"
        metadata.write_text(json.dumps([{"id": "a", "path": "loop.wav", "bpm": 125}]))
        self.fs = MusicFS(Catalog(metadata, self.root))
        self.addCleanup(self.fs.close)
        self.inode = next(n.inode for n in self.fs.catalog.nodes.values() if n.path is not None)

    def test_read_offsets_eof_and_release(self):
        async def scenario():
            file_info = await self.fs.open(self.inode, os.O_RDONLY)
            fh = file_info.fh
            for off, size in [(0, 100), (121, 500), (len(self.data)-8, 100),
                              (len(self.data), 50), (len(self.data)+10, 50), (0, 0)]:
                self.assertEqual(await self.fs.read(fh, off, size), self.data[off:off+size])
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.read(fh, -1, 1)
            self.assertEqual(error.exception.errno, errno.EINVAL)
            await self.fs.release(fh)
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.read(fh, 0, 1)
            self.assertEqual(error.exception.errno, errno.EBADF)
        trio.run(scenario)

    def test_read_only_flags(self):
        async def scenario():
            for flags in [os.O_WRONLY, os.O_RDWR, os.O_RDONLY | os.O_TRUNC, os.O_RDONLY | os.O_APPEND]:
                with self.assertRaises(pyfuse3.FUSEError) as error:
                    await self.fs.open(self.inode, flags)
                self.assertEqual(error.exception.errno, errno.EROFS)
            self.assertEqual(self.source.read_bytes(), self.data)
        trio.run(scenario)

    def test_attributes_and_dot_lookup(self):
        async def scenario():
            attrs = await self.fs.getattr(self.inode)
            self.assertEqual(attrs.st_nlink, 3)
            self.assertEqual(attrs.st_size, len(self.data))
            self.assertEqual(attrs.st_mode & 0o777, 0o444)
            category = self.fs.catalog.nodes[1].children[b"by_bpm"]
            self.assertEqual((await self.fs.lookup(category, b".")).st_ino, category)
            self.assertEqual((await self.fs.lookup(category, b"..")).st_ino, 1)
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.opendir(self.inode)
            self.assertEqual(error.exception.errno, errno.ENOTDIR)
        trio.run(scenario)

    def test_readdir_resumes_after_full_buffer(self):
        async def scenario():
            accepted = []
            def reply(token, name, entry, position):
                if len(accepted) == 1:
                    return False
                accepted.append((name, position))
                return True
            with patch("musicfs.fs.pyfuse3.readdir_reply", side_effect=reply):
                await self.fs.readdir(1, 0, None)
            first = accepted[0]
            rest = []
            with patch("musicfs.fs.pyfuse3.readdir_reply",
                       side_effect=lambda token, name, entry, position: rest.append((name, position)) or True):
                await self.fs.readdir(1, first[1], None)
            self.assertEqual([name for name, _ in accepted + rest], list(self.fs.catalog.nodes[1].children))
        trio.run(scenario)

    def test_missing_source_and_existing_handle(self):
        async def scenario():
            info = await self.fs.open(self.inode, os.O_RDONLY)
            self.source.unlink()
            self.assertEqual((await self.fs.getattr(self.inode)).st_size, len(self.data))
            self.assertEqual(await self.fs.read(info.fh, 0, 50), self.data[:50])
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.open(self.inode, os.O_RDONLY)
            self.assertEqual(error.exception.errno, errno.ENOENT)
            await self.fs.release(info.fh)
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.getattr(self.inode)
            self.assertEqual(error.exception.errno, errno.ENOENT)
        trio.run(scenario)

    def test_symlink_replacement_cannot_escape(self):
        outside = self.base / "outside.wav"
        outside.write_bytes(b"private")
        self.source.unlink()
        self.source.symlink_to(outside)
        async def scenario():
            with self.assertRaises(pyfuse3.FUSEError) as error:
                await self.fs.open(self.inode, os.O_RDONLY)
            self.assertEqual(error.exception.errno, errno.EACCES)
        trio.run(scenario)

    def test_close_cleans_unreleased_handles(self):
        info = trio.run(self.fs.open, self.inode, os.O_RDONLY)
        self.fs.close()
        self.assertFalse(self.fs.handles)
        with self.assertRaises(OSError):
            os.fstat(info.fh)

    def test_mountpoint_validation(self):
        mount = self.base / "mnt"
        mount.mkdir()
        self.assertEqual(validate_mountpoint(mount, self.root), mount)
        (mount / "keep.txt").write_text("do not hide")
        with self.assertRaises(ValueError):
            validate_mountpoint(mount, self.root)
        with self.assertRaises(ValueError):
            validate_mountpoint(self.root, self.root)
        with self.assertRaises(ValueError):
            validate_mountpoint(self.base, self.root)


if __name__ == "__main__":
    unittest.main()
