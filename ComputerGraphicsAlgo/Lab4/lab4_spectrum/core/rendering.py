"""Absolute spectral/RGB arrays, surface control points and sampled extrema."""
import math
import numpy as np
from .geometry import camera_basis, geometry_factors, trace, unit, validate
from .spectral import load_tables
from .color_conversion import (CIE_RGB_TO_XYZ, XYZ_TO_CIE_RGB,
                               scene_rgb, spectrum_to_xyz)


def radiance_at(points_mm, p, tables=None):
    tables = tables or load_tables()
    factors = geometry_factors(points_mm, p)
    # The linear basis preserves XYZ, not the radiant integral. Do not renormalize.
    spectra = np.array([light.spectrum for light in p.lights])
    spectral = (factors @ spectra) * np.asarray(p.reflectance)
    xyz = spectrum_to_xyz(spectral, tables)
    kd, lights = scene_rgb(p, tables)
    return dict(spectral=spectral, xyz=xyz, rgb1=xyz @ XYZ_TO_CIE_RGB.T,
                rgb2=(factors @ lights) * kd, radiance_w_m2_sr=spectral @ tables.weights,
                luminance_cd_m2=683 * xyz[..., 1])


def control_points(p, tables=None):
    front = unit(p.observer() - p.center())
    right = camera_basis(p)[0]
    tangent = unit(right - np.dot(right, front) * front)
    angle = min(math.acos(.8), .7 * math.acos(p.radius_mm / np.linalg.norm(p.observer() - p.center())))
    normals = (front, math.cos(angle) * front - math.sin(angle) * tangent,
               math.cos(angle) * front + math.sin(angle) * tangent)
    points = p.center() + p.radius_mm * np.array(normals)
    values, records = radiance_at(points, p, tables), []
    for i, (point, normal) in enumerate(zip(points, normals)):
        row = dict(name=f"P{i+1}", x_mm=float(point[0]), y_mm=float(point[1]), z_mm=float(point[2]),
                   visible=bool(np.dot(normal, p.observer() - point) > 0),
                   radiance_w_m2_sr=float(values["radiance_w_m2_sr"][i]),
                   luminance_cd_m2=float(values["luminance_cd_m2"][i]))
        for name in ("xyz", "rgb1", "rgb2"):
            row.update({f"{name}_{c}": float(v) for c, v in
                        zip("XYZ" if name == "xyz" else "RGB", values[name][i])})
        records.append(row)
    return records


def _extrema(values):
    return dict(minimum=float(values.min()), maximum=float(values.max()))


def calculate(p):
    validate(p)
    tables = load_tables()
    x = -p.width_mm / 2 + (np.arange(p.width_px) + .5) * p.width_mm / p.width_px
    y = p.height_mm / 2 - (np.arange(p.height_px) + .5) * p.height_mm / p.height_px
    mask, points = trace(p, *np.meshgrid(x, y))
    if not np.any(mask):
        raise ValueError("Ни один пиксель не пересекает сферу")
    shape = mask.shape
    spectral = np.zeros(shape + (41,), float)
    xyz, rgb1, rgb2 = (np.zeros(shape + (3,), float) for _ in range(3))
    radiance = np.zeros(shape, float)
    ids = np.flatnonzero(mask)
    # 保留完整光谱立方体，但按块计算中间结果，避免额外大数组。
    for start in range(0, len(ids), 8192):
        chunk = ids[start:start + 8192]
        values = radiance_at(points.reshape(-1, 3)[chunk], p, tables)
        spectral.reshape(-1, 41)[chunk] = values["spectral"]
        for target, key in ((xyz, "xyz"), (rgb1, "rgb1"), (rgb2, "rgb2")):
            target.reshape(-1, 3)[chunk] = values[key]
        radiance.reshape(-1)[chunk] = values["radiance_w_m2_sr"]
    xyz2 = rgb2 @ CIE_RGB_TO_XYZ.T
    luminance1, luminance2 = 683 * xyz[..., 1], 683 * xyz2[..., 1]
    statistics = {name: _extrema(v[mask]) | {"mean": float(v[mask].mean())} for name, v in
                  (("radiance_w_m2_sr", radiance), ("luminance_1_cd_m2", luminance1),
                   ("luminance_2_cd_m2", luminance2))}
    statistics["visible_pixel_count"] = int(mask.sum())
    theta, phi = np.meshgrid(np.linspace(0, np.pi, 181),
                            np.linspace(0, 2 * np.pi, 360, endpoint=False), indexing="ij")
    normals = np.stack((np.sin(theta) * np.cos(phi), np.sin(theta) * np.sin(phi), np.cos(theta)), axis=-1)
    sampled = {key: [] for key in ("radiance_w_m2_sr", "luminance_cd_m2")}
    normals = normals.reshape(-1, 3)
    for start in range(0, len(normals), 8192):
        values = radiance_at(p.center() + p.radius_mm * normals[start:start + 8192], p, tables)
        for key in sampled:
            sampled[key].append(values[key])
    statistics.update({"sphere_sampled_" + key: _extrema(np.concatenate(v)) for key, v in sampled.items()})
    statistics["sphere_sampling"] = "181 polar angles x 360 azimuths, poles included"
    return dict(parameters=p, wavelengths=tables.wavelengths, x=x, y=y, mask=mask, points=points,
                spectral=spectral, xyz=xyz, rgb1=rgb1, rgb2=rgb2, radiance=radiance,
                luminance1=luminance1, luminance2=luminance2,
                statistics=statistics, control_points=control_points(p, tables))

