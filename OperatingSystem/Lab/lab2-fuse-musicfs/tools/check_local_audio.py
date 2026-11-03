"""只读验证本机选择的 8 个音频；清单与结果留在忽略提交的 local-data 中。"""

import errno
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

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
    if not 1 <= len(records) <= 8:
        raise ValueError("local validation is limited to 1-8 files")
    sources = [source_root / record["path"] for record in records]
    allowed = [source_root / "preset", source_root / "project/AUTUMN"]
    if any(not any(p.resolve().is_relative_to(root) for root in allowed) for p in sources):
        raise ValueError("source outside the two authorized directories")
    total = sum(p.stat().st_size for p in sources)
    if total > 100 * 1024 * 1024:
        raise ValueError("local validation is limited to 100 MiB")
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
             "--source-root", str(source_root), str(mount)],
            cwd=project, stdout=log, stderr=log,
        )
        try:
            deadline = time.monotonic() + 15
            while not os.path.ismount(mount):
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("local audio mount failed; see local-data/mount.log")
                time.sleep(0.05)
            for record, source, original in zip(records, sources, before):
                name = f"{record['id']}__{source.name}"
                paths = [mount / category / group / name for category, group in (
                    ("by_bpm", bpm_group(record.get("bpm"))),
                    ("by_key", label(record.get("key"))),
                    ("by_type", label(record.get("type"))),
                )]
                assert len({p.stat().st_ino for p in paths}) == 1
                assert all(p.stat().st_nlink == 3 and sha256(p) == original[2] for p in paths)
                with open(paths[0], "rb") as virtual, open(source, "rb") as physical:
                    for offset in (0, original[0] // 2, max(0, original[0] - 16), original[0]):
                        assert os.pread(virtual.fileno(), 4096, offset) == os.pread(physical.fileno(), 4096, offset)
                results.append(dict(id=record["id"], source=record["path"], bytes=original[0],
                                    format=source.suffix, sha256=original[2],
                                    aliases=[str(p.relative_to(mount)) for p in paths],
                                    inode=paths[0].stat().st_ino, aliases_and_ranges="passed"))
            try:
                (mount / "must-not-create.wav").touch()
            except OSError as exc:
                assert exc.errno == errno.EROFS
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
    report = dict(files=len(records), total_bytes=total, source_unchanged=True,
                  read_only="passed", unmounted=True, network_services_used=False,
                  scope="Byte reading and hashes only; no decoding or playback verification.", results=results)
    (project / "local-data/validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(records)} files, {total / 1024**2:.2f} MiB, 3 aliases each; source unchanged; unmounted")


if __name__ == "__main__":
    main()
