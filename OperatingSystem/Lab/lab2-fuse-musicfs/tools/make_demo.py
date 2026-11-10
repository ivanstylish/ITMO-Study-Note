"""Generate three synthetic WAV fixtures; never overwrite an existing demo."""

import argparse
import json
import math
from pathlib import Path
import struct
import wave


def make_demo(output):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("output must be empty; refusing to overwrite files")
    # 测试样例自包含，清理 examples 目录后仍可重建，不依赖真实音频库。
    records = [
        dict(id="s001", path="drums/drum_loop.wav", bpm=124.5, key="A_minor", type="drum"),
        dict(id="s002", path="bass/bass_line.wav", bpm=125, key=None, type="bass"),
        dict(id="s003", path="songs/夜行 трек.wav", bpm=90, key="C_major", type="song"),
    ]
    for index, record in enumerate(records):
        path = output / "audio" / record["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as stream:
            stream.setparams((1, 2, 22050, 0, "NONE", "not compressed"))
            samples = (int(8000 * math.sin(2 * math.pi * (110 + 110 * index) * n / 22050)) for n in range(22050))
            stream.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))
    (output / "metadata.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        records = make_demo(args.output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Created {len(records)} synthetic WAV files and metadata.json in {args.output}")
