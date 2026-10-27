"""Textbook color transforms, with the lecture display gamma approximation."""
import numpy as np
from .spectral import load_tables

# Textbook 3281, printed p. 70: numerical CIE RGB -> XYZ matrix.
CIE_RGB_TO_XYZ = np.array([[.49, .31, .20],
                          [.17697, .81240, .01063], [0, .01, .99]])
XYZ_TO_CIE_RGB = np.linalg.inv(CIE_RGB_TO_XYZ)
XYZ_TO_LINEAR_SRGB = np.array([[3.2406, -1.5372, -.4986],
                              [-.9689, 1.8758, .0415], [.0557, -.2040, 1.0570]])


def spectrum_to_xyz(spectrum, tables=None):
    return np.asarray(spectrum) @ (tables or load_tables()).weighted_cmf


def spectrum_to_rgb(spectrum, tables=None):
    return spectrum_to_xyz(spectrum, tables) @ XYZ_TO_CIE_RGB.T


def scene_rgb(p, tables=None):
    tables = tables or load_tables()
    white = spectrum_to_rgb(tables.d65, tables)
    if np.any(np.abs(white) < 1e-12):
        raise ValueError("Нулевой канал эталонного D65")
    kd = spectrum_to_rgb(tables.d65 * np.asarray(p.reflectance), tables) / white
    lights = [spectrum_to_rgb(light.spectrum, tables) for light in p.lights]
    return kd, np.array(lights)


def monitor_encode(linear):
    """Lecture 5 pp. 43–46: display gamma 2.2, after linear-light computation."""
    return np.clip(np.asarray(linear, float), 0, 1) ** (1 / 2.2)
