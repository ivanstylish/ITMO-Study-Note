"""41 通道光谱、输入表和场景参数，不负责显示颜色。"""
import csv
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
import numpy as np
from .geometry import Parameters, require

BASE = Path(__file__).resolve().parent
WAVELENGTHS = np.arange(380.0, 781.0, 10.0)


@dataclass(frozen=True)
class ColorTables:
    wavelengths: np.ndarray
    cmf: np.ndarray
    d65: np.ndarray
    weights: np.ndarray

    @property
    def weighted_cmf(self):
        return self.cmf * self.weights[:, None]


@lru_cache(maxsize=1)
def load_tables():
    def read(name, columns):
        with (BASE / "data" / name).open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        require(np.array_equal([float(r["wavelength_nm"]) for r in rows], WAVELENGTHS),
                name + ": требуется 380..780 нм с шагом 10 нм")
        values = np.array([[float(r[c]) for c in columns] for r in rows])
        require(np.all(np.isfinite(values)) and np.all(values >= 0), name + ": неверные значения")
        return values
    cmf = read("cie_xyz_1931.csv", ("x_bar", "y_bar", "z_bar"))
    sources = read("light_spectra.csv", ("d65",))
    require(np.any(sources > 0), "Нулевой спектр источника")
    weights = np.full(41, 10.0)
    weights[[0, -1]] = 5.0  # 梯形积分的端点权重，单位 nm。
    return ColorTables(WAVELENGTHS.copy(), cmf, sources[:, 0], weights)


def normalize_spd(spectrum, tables=None):
    tables = tables or load_tables()
    values = np.asarray(spectrum, float)
    values = values / np.max(values)
    return values / np.dot(values, tables.weights)


def default_parameters():
    spectrum = tuple(normalize_spd(load_tables().d65))
    lights = tuple(replace(light, spectrum=spectrum) for light in Parameters().lights)
    return Parameters(lights=lights)
