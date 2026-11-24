"""只读验证本机选择的最多 12 个音频，记录正式组实测数据。"""

import errno
from datetime import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import stat
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

from musicfs.catalog import Catalog, bpm_group, label


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    project = Path(__file__).resolve().parents[1]
    metadata = project / "local-data/metadata.json"
    source_root = Path("/mnt/e")
    records = json.loads(metadata.read_text(encoding="utf-8"))
    if not 1 <= len(records) <= 12:
        raise ValueError("local validation is limited to 1-12 files")
    sources = [source_root / record["path"] for record in records]
    allowed = [source_root / "preset", source_root / "project/AUTUMN"]
    if any(not any(p.resolve().is_relative_to(root) for root in allowed) for p in sources):
        raise ValueError("source outside the two authorized directories")
    total = sum(p.stat().st_size for p in sources)
    if total > 128 * 1024 * 1024:
        raise ValueError("local validation is limited to 128 MiB")
    catalog = Catalog(metadata, source_root)
    assert catalog.file_count == len(records) and not catalog.warnings
    before = [(p.stat().st_size, p.stat().st_mtime_ns, sha256(p)) for p in sources]
    temporary = tempfile.TemporaryDirectory(prefix="musicfs-local-")
    mount = Path(temporary.name) / "mnt"
    mount.mkdir()
    results = []
    with (project / "local-data/mount.log").open("w") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "musicfs", "--metadata", str(metadata),
             "--source-root", str(source_root), str(mount), "--debug"],
            cwd=project, stdout=log, stderr=log,
        )
        try:
            deadline = time.monotonic() + 15
            while not os.path.ismount(mount):
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("local audio mount failed; see local-data/mount.log")
                time.sleep(0.05)
            mount_info = subprocess.check_output(
                ["findmnt", "-n", "-o", "FSTYPE,OPTIONS", "--mountpoint", str(mount)], text=True).strip()
            assert "ro" in mount_info.split(maxsplit=1)[1].split(",")
            assert stat.S_IMODE(mount.stat().st_mode) == 0o555
            tree = subprocess.check_output(["ls", "-R", str(mount)], text=True)
            (project / "evidence/formal-tree.txt").write_text(
                tree.replace(str(mount), "<mountpoint>"), encoding="utf-8")
            info_dir = mount / "info"
            assert {p.name for p in info_dir.iterdir()} == {f"{r['id']}.info" for r in records}
            for record, source, original in zip(records, sources, before):
                name = f"{record['id']}__{source.name}"
                paths = [mount / category / group / name for category, group in (
                    ("by_bpm", bpm_group(record.get("bpm"))),
                    ("by_key", label(record.get("key"))),
                    ("by_type", label(record.get("type"))),
                )]
                aliases = []
                offsets = (0, original[0] // 2, max(0, original[0] - 16), original[0])
                for path in paths:
                    attributes = path.stat()
                    digest = sha256(path)
                    assert attributes.st_size == original[0] and attributes.st_nlink == 3
                    assert stat.S_IMODE(attributes.st_mode) == 0o444, (
                        record["id"], str(path.relative_to(mount)), oct(stat.S_IMODE(attributes.st_mode)))
                    assert digest == original[2], (record["id"], digest, original[2])
                    returned = []
                    with open(path, "rb") as virtual, open(source, "rb") as physical:
                        for offset in offsets:
                            data = os.pread(virtual.fileno(), 4096, offset)
                            assert data == os.pread(physical.fileno(), 4096, offset)
                            returned.append(len(data))
                    aliases.append(dict(path=str(path.relative_to(mount)), inode=attributes.st_ino,
                                        device=attributes.st_dev, links=attributes.st_nlink,
                                        bytes=attributes.st_size, mode="0444", sha256=digest,
                                        range_checks=len(offsets), returned_bytes=returned))
                assert len({(alias["device"], alias["inode"]) for alias in aliases}) == 1
                info_path = info_dir / f"{record['id']}.info"
                info_text = subprocess.check_output(["cat", str(info_path)], timeout=5)
                info_attrs = info_path.stat()
                assert info_attrs.st_mode == stat.S_IFREG | 0o444
                assert info_attrs.st_size == len(info_text) and info_attrs.st_nlink == 1
                assert info_attrs.st_ino != aliases[0]["inode"]
                bpm_line, rest = info_text.decode("utf-8").split("\n", 1)
                assert bpm_line.startswith("BPM: ")
                bpm = record.get("bpm")
                assert (bpm_line == "BPM: unknown" if bpm is None else float(bpm_line[5:]) == bpm)
                assert rest == (f"Key: {label(record.get('key'))}\n"
                                f"Type: {label(record.get('type'))}\nSize: {original[0]} bytes\n")
                # 只尝试以写方式打开，不写入、不截断或删除正式源文件。
                try:
                    fd = os.open(paths[0], os.O_WRONLY)
                except OSError as exc:
                    assert exc.errno == errno.EROFS
                    write_errno = exc.errno
                else:
                    os.close(fd)
                    raise AssertionError("write open unexpectedly succeeded")
                copied = Path(temporary.name) / (record["id"] + source.suffix)
                subprocess.run(["cp", str(paths[0]), str(copied)], check=True, timeout=30)
                copied_digest = sha256(copied)
                assert copied_digest == original[2]
                results.append(dict(id=record["id"], source=record["path"], bytes=original[0],
                                    format=source.suffix, sha256=original[2],
                                    aliases=[str(p.relative_to(mount)) for p in paths],
                                    name=name, bpm=record.get("bpm"), key=record.get("key"),
                                    type=record.get("type"), alias_stats=aliases,
                                    range_offsets=list(offsets), range_checks=3 * len(offsets),
                                    requested_bytes=4096, write_open_errno=write_errno,
                                    copied_sha256=copied_digest,
                                    info_path=str(info_path.relative_to(mount)),
                                    info_content=info_text.decode("utf-8"),
                                    info_inode=info_attrs.st_ino, info_bytes=info_attrs.st_size,
                                    inode=aliases[0]["inode"], aliases_and_ranges="passed"))
            try:
                (mount / "must-not-create.wav").touch()
            except OSError as exc:
                assert exc.errno == errno.EROFS
                create_errno = exc.errno
            else:
                raise AssertionError("read-only protection failed")
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
            if os.path.ismount(mount):
                subprocess.run(["fusermount3", "-u", str(mount)], check=True, timeout=10)
            if os.path.ismount(mount):
                raise RuntimeError("refusing to clean a mounted directory")
            temporary.cleanup()
    assert process.returncode == 0
    after = [(p.stat().st_size, p.stat().st_mtime_ns, sha256(p)) for p in sources]
    assert before == after, "source content, size or mtime changed"
    assert len({result["inode"] for result in results}) == len(records)
    report = dict(files=len(records), total_bytes=total, source_unchanged=True,
                  read_only="passed", unmounted=True, network_services_used=False,
                  checked_at=datetime.now(ZoneInfo("Europe/Moscow")).isoformat(),
                  metadata_sha256=sha256(metadata), mount_info=mount_info,
                  environment=dict(python=platform.python_version(),
                                   pyfuse3=importlib.metadata.version("pyfuse3"),
                                   trio=importlib.metadata.version("trio"),
                                   libfuse3=subprocess.check_output(
                                       ["pkg-config", "--modversion", "fuse3"], text=True).strip()),
                  alias_checks=sum(len(result["aliases"]) for result in results),
                  range_checks=sum(result["range_checks"] for result in results),
                  copy_checks=len(results), create_errno=create_errno,
                  info_checks=len(results),
                  scope="Byte reading and hashes only; no decoding or playback verification.", results=results)
    (project / "local-data/validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # 报告采用本次正式组实测数据；便携证据省去源库的完整相对路径。
    portable = dict(report, results=[{k: v for k, v in result.items() if k != "source"} for result in results])
    portable["formats"] = {ext: sum(r["format"] == ext for r in results)
                           for ext in sorted({r["format"] for r in results})}
    (project / "evidence/local-audio-summary.json").write_text(
        json.dumps(portable, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(records)} files, {total / 1024**2:.2f} MiB; "
          f"{report['alias_checks']} aliases, {report['range_checks']} ranges, "
          f"{report['copy_checks']} copies, {report['info_checks']} info files; source unchanged; unmounted")


if __name__ == "__main__":
    main()
