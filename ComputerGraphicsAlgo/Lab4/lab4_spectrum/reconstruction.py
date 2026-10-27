"""Three-basis reconstruction: Lecture 4, pages 37–42, textbook Fig. 4.6."""
import numpy as np
from .core.color_conversion import CIE_RGB_TO_XYZ
from .core.spectral import load_tables


def reconstruct(rgb):
    """Solve C a = M RGB with F1=x_bar, F2=y_bar, F3=z_bar."""
    rgb = np.asarray(rgb, float)
    if rgb.shape != (3,) or not np.all(np.isfinite(rgb)) or np.linalg.norm(rgb) == 0:
        raise ValueError("RGB: требуются три конечных ненулевых координаты CIE RGB")
    tables = load_tables()
    basis = tables.cmf
    matrix = tables.weighted_cmf.T @ basis
    coefficients = np.linalg.solve(matrix, CIE_RGB_TO_XYZ @ rgb)
    spectrum = basis @ coefficients
    # Lecture p. 42: the chosen basis can produce a negative spectrum. Never clip it.
    if not np.all(np.isfinite(spectrum)) or np.any(spectrum < 0) or not np.any(spectrum > 0):
        raise ValueError("Выбранный базис XYZ даёт отрицательный или нулевой спектр для этого RGB")
    return spectrum
