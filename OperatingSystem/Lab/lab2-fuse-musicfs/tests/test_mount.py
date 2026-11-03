"""Opt-in tests using a real Linux FUSE mount, never the user's audio library."""

from concurrent.futures import ThreadPoolExecutor
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from tools.make_demo import make_demo


@unittest.skipUnless(os.environ.get("MUSICFS_INTEGRATION") == "1", "set MUSICFS_INTEGRATION=1 for real mounts")
class MountedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="musicfs-")
        self.base = Path(self.temp.name)
        self.records = make_demo(self.base / "demo")
        self.root = self.base / "demo/audio"
        self.metadata = self.base / "demo/metadata.json"
        self.mount = self.base / "mnt"
        self.mount.mkdir()
        self.process = None
        self.log = open(self.base / "fuse.log", "w+")
        self.addCleanup(self.cleanup_mount)
        self.start_mount()

    def start_mount(self):
        command = [sys.executable, "-m", "musicfs", "--metadata", str(self.metadata),
                   "--source-root", str(self.root), str(self.mount), "--debug"]
        self.process = subprocess.Popen(command, stdout=self.log, stderr=self.log,
                                        cwd=Path(__file__).resolve().parents[1])
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if os.path.ismount(self.mount):
                return
            if self.process.poll() is not None:
                self.log.seek(0)
                self.fail("mount process exited: " + self.log.read())
            time.sleep(0.05)
        self.fail("mount timed out")

    def stop_mount(self):
        if os.path.ismount(self.mount):
            subprocess.run(["fusermount3", "-u", str(self.mount)], check=True, timeout=10)
        if self.process is not None:
            self.process.wait(timeout=10)
        self.assertFalse(os.path.ismount(self.mount))

    def cleanup_mount(self):
        try:
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
            if os.path.ismount(self.mount):
                subprocess.run(["fusermount3", "-u", str(self.mount)], check=True, timeout=10)
            if os.path.ismount(self.mount):
                raise RuntimeError("refusing to clean a still-mounted directory")
        finally:
            self.log.close()
        self.temp.cleanup()

    def audio(self):
        return self.mount / "by_type/drum/s001__drum_loop.wav"

    def test_aliases_hashes_stat_and_external_commands(self):
        aliases = [self.audio(), self.mount / "by_bpm/120/s001__drum_loop.wav",
                   self.mount / "by_key/A_minor/s001__drum_loop.wav"]
        self.assertEqual(len({(p.stat().st_dev, p.stat().st_ino) for p in aliases}), 1)
        source = self.root / "drums/drum_loop.wav"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        for path in aliases:
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            self.assertEqual(path.stat().st_nlink, 3)
        subprocess.run(["ls", "-l", str(aliases[0].parent)], check=True, capture_output=True)
        subprocess.run(["stat", str(aliases[0])], check=True, capture_output=True)
        copy = self.base / "copy.wav"
        subprocess.run(["cp", str(aliases[0]), str(copy)], check=True, capture_output=True)
        self.assertEqual(copy.read_bytes(), source.read_bytes())

    def test_random_reads_eof_and_concurrency(self):
        data = (self.root / "drums/drum_loop.wav").read_bytes()
        fd = os.open(self.audio(), os.O_RDONLY)
        try:
            ranges = [(0, 44), (111, 8192), (len(data)-10, 100), (len(data), 20), (len(data)+50, 20)] * 10
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda pair: os.pread(fd, pair[1], pair[0]), ranges))
            self.assertEqual(results, [data[off:off+size] for off, size in ranges])
        finally:
            os.close(fd)

    def test_all_mutations_fail_without_source_changes(self):
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in self.root.rglob("*.wav")}
        path = self.audio()
        def write_open():
            fd = os.open(path, os.O_WRONLY)
            os.close(fd)
        operations = [write_open, lambda: path.write_bytes(b"overwrite"),
                      lambda: (path.parent / "new.wav").touch(), path.unlink,
                      lambda: path.rename(path.with_name("renamed.wav")),
                      lambda: os.truncate(path, 0), lambda: path.chmod(0o777),
                      lambda: (path.parent / "newdir").mkdir()]
        for operation in operations:
            with self.assertRaises(OSError) as error:
                operation()
            self.assertEqual(error.exception.errno, errno.EROFS)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in before})

    def test_unicode_and_unknown_category(self):
        unicode_path = self.mount / "by_type/song/s003__夜行 трек.wav"
        self.assertEqual(unicode_path.read_bytes(), (self.root / "songs/夜行 трек.wav").read_bytes())
        self.assertTrue((self.mount / "by_key/unknown/s002__bass_line.wav").is_file())
        self.assertTrue((self.mount / "by_bpm/130/s002__bass_line.wav").is_file())
        self.assertEqual((self.audio().parent / "..").stat().st_ino,
                         (self.mount / "by_type").stat().st_ino)

    def test_source_deleted_after_open(self):
        fd = os.open(self.audio(), os.O_RDONLY)
        data = (self.root / "drums/drum_loop.wav").read_bytes()
        try:
            (self.root / "drums/drum_loop.wav").unlink()
            self.assertEqual(os.pread(fd, 100, 0), data[:100])
            with self.assertRaises(FileNotFoundError):
                os.open(self.audio(), os.O_RDONLY)
        finally:
            os.close(fd)

    def test_metadata_snapshot_and_remount(self):
        self.records[0]["type"] = "percussion"
        self.metadata.write_text(json.dumps(self.records, ensure_ascii=False), encoding="utf-8")
        self.assertTrue(self.audio().is_file())
        self.assertFalse((self.mount / "by_type/percussion").exists())
        self.stop_mount()
        self.start_mount()
        self.assertFalse((self.mount / "by_type/drum").exists())
        self.assertTrue((self.mount / "by_type/percussion/s001__drum_loop.wav").is_file())

    def test_large_directory_pagination(self):
        self.stop_mount()
        records = []
        for index in range(1200):
            name = f"item{index:04d}.wav"
            (self.root / name).write_bytes(bytes([index % 256]))
            records.append({"id": f"i{index:04d}", "path": name, "type": "many"})
        self.metadata.write_text(json.dumps(records), encoding="utf-8")
        self.start_mount()
        actual = os.listdir(self.mount / "by_type/many")
        expected = {f"i{i:04d}__item{i:04d}.wav" for i in range(1200)}
        self.assertEqual(len(actual), len(expected))
        self.assertEqual(set(actual), expected)

    def test_sigint_unmount_and_restart(self):
        self.process.send_signal(signal.SIGINT)
        self.assertEqual(self.process.wait(timeout=10), 0)
        self.assertFalse(os.path.ismount(self.mount))
        self.start_mount()
        self.assertTrue(self.audio().is_file())

    def test_sigterm_unmount(self):
        self.process.terminate()
        self.assertEqual(self.process.wait(timeout=10), 0)
        self.assertFalse(os.path.ismount(self.mount))

    def test_exception_cleanup_and_restart(self):
        self.stop_mount()
        code = (
            "import trio\nimport musicfs.__main__ as app\n"
            "async def fail():\n"
            "    await trio.sleep(0.2)\n"
            "    raise RuntimeError('intentional integration test failure')\n"
            "app.serve = fail\napp.main()\n"
        )
        command = [sys.executable, "-c", code, "--metadata", str(self.metadata),
                   "--source-root", str(self.root), str(self.mount)]
        self.process = subprocess.Popen(command, stdout=self.log, stderr=self.log,
                                        cwd=Path(__file__).resolve().parents[1])
        self.assertNotEqual(self.process.wait(timeout=10), 0)
        self.assertFalse(os.path.ismount(self.mount))
        self.start_mount()
        self.assertTrue(self.audio().is_file())

    def test_missing_before_mount_and_empty_catalog(self):
        self.stop_mount()
        for source in self.root.rglob("*.wav"):
            source.unlink()
        self.start_mount()
        self.assertEqual(os.listdir(self.mount), [])
        self.stop_mount()
        self.log.flush()
        self.log.seek(0)
        self.assertIn("skipped", self.log.read())


if __name__ == "__main__":
    unittest.main()
