"""Shared render settings and result files for the CLI and desktop viewer."""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from render import render
from scene import build_scene


HERE = Path(__file__).resolve().parent
SCENE_FILE = HERE / "scene.json"
RESULTS_DIR = HERE.parent / "results"
GAMMA = 2.2


@dataclass(frozen=True)
class Settings:
    # 报告 §4–5 的默认参数，depth 计数的是表面命中次数（含首命中）。
    size: int = 500
    samples: int = 36
    depth: int = 4
    seed: int = 5
    white: float = 4

    def __post_init__(self):
        if not 500 <= self.size <= 1000:
            raise ValueError("Размер кадра должен быть в пределах 500–1000 пикселей.")
        if not 1 <= self.samples <= 256 or not 1 <= self.depth <= 16 or self.seed < 0:
            raise ValueError("Требуются 1–256 путей на пиксель, глубина 1–16 и seed ≥ 0.")
        if not np.isfinite(self.white) or self.white <= 0:
            raise ValueError("Уровень белого должен быть конечным и положительным.")


def load_scene(path):
    config = json.loads(path.read_text(encoding="utf-8-sig"))
    return config, build_scene(config)


def run(config, scene, settings, progress):
    direct, indirect = render(scene, config["camera"], settings.size, settings.samples,
                              settings.depth, settings.seed, progress)
    # 报告 §6 表 4：先在线性空间相加，再按整帧统计各通道，包含射线未命中的黑色像素。
    full = direct + indirect
    summary = {
        "size_px": [settings.size, settings.size], "samples": settings.samples,
        "depth": settings.depth, "seed": settings.seed, "triangles": len(scene.mesh.materials),
        "units": "W/(m^2 sr) per RGB band", "gamma": GAMMA,
        "white": settings.white, "max_channel": float(full.max()),
        "mean_direct_rgb": direct.mean(axis=(0, 1)).tolist(),
        "mean_indirect_rgb": indirect.mean(axis=(0, 1)).tolist(),
        "scene": config,
    }
    return {"direct": direct, "indirect": indirect, "full": full}, summary


def encode(image, white, gamma=GAMMA):
    # 报告 §5：用公共白点归一化，裁剪到 [0,1] 后取 1/γ 次幂，再量化为 8 位码值。
    relative = np.clip(image / white, 0, 1)
    return np.rint(255 * relative**(1 / gamma)).astype(np.uint8)


def make_images(data, summary):
    return tuple(Image.fromarray(encode(data[key], summary["white"], summary["gamma"]))
                 for key in ("direct", "full"))


def save(output, data, summary):
    output.mkdir(parents=True, exist_ok=True)
    direct, full = make_images(data, summary)
    direct.save(output / "direct.png")
    full.save(output / "render.png")
    # PNG 用于显示，NPZ 保留裁剪和伽马前的绝对辐亮度，可复核表 4 和前表面选区。
    np.savez_compressed(output / "radiance.npz", **data)
    (output / "results.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
