# 组织白球实验：重建各光源光谱，计算原始与重建场景，生成统一显示的三图和误差。
from dataclasses import replace
import numpy as np
from .core.color_conversion import (CIE_RGB_TO_XYZ, cie_rgb_to_linear_srgb,
                                    scene_rgb, spectrum_to_rgb, monitor_encode)
from .core.geometry import validate, geometry_factors, light_geometry
from .core.rendering import calculate
from .core.spectral import default_parameters, load_tables, normalize_spd
from .reconstruction import reconstruct


# 创建使用归一化 D65 光谱、白色漫反射球和默认相机及光源的场景。
def white_scene():
    return default_parameters()


# 接收可选场景和各光源的 CIE RGB，返回渲染数据、三张对照图和光谱误差。
def run(scene=None, light_rgb=None):
    scene = white_scene() if scene is None else scene
    validate(scene)
    # 实验限定白色朗伯球，所有波长的漫反射系数均为 1。
    if not np.allclose(scene.reflectance, 1, rtol=0, atol=1e-12):
        raise ValueError("ЛР4: требуется белый ламбертовский отражатель, kd=1")

    # 原始光谱积分归一到 1，I₀ 保留为原场景的强度尺度；重建谱不再归一化。
    scene = replace(scene, lights=tuple(replace(light, spectrum=tuple(normalize_spd(light.spectrum)))
                                       for light in scene.lights))
    t = load_tables()
    # 未传入光源 RGB 时，从原始光谱计算输入颜色；每个光源对应三个坐标。
    _, original_rgb = scene_rgb(scene)
    rgb = original_rgb if light_rgb is None else np.asarray(light_rgb, float)
    if rgb.shape != (len(scene.lights), 3):
        raise ValueError("Требуется RGB для каждого источника")
    # 重建函数只接收 RGB；再以重建谱建立几何参数相同的场景。
    recovered = np.array([reconstruct(v) for v in rgb])
    rebuilt = replace(scene, lights=tuple(replace(light, spectrum=tuple(s))
                      for light, s in zip(scene.lights, recovered)))
    # 分别渲染原场景与重建场景，用相同白球和照明公式进行比较。
    reference = calculate(scene)
    result = calculate(rebuilt)
    mask = result["mask"]
    # 三条路径依次为：重建谱渲染、原谱渲染、原场景直接 RGB 计算。
    # Direct RGB must use the edited RGB input, not the original D65 reference.
    rgb_direct = np.zeros_like(reference["rgb2"])
    ids = np.flatnonzero(mask)
    for start in range(0, len(ids), 8192):
        chunk = ids[start:start + 8192]
        points = reference["points"].reshape(-1, 3)[chunk]
        rgb_direct.reshape(-1, 3)[chunk] = geometry_factors(points, scene) @ rgb
    luminance_direct = 683 * (rgb_direct @ CIE_RGB_TO_XYZ.T)[..., 1]
    arrays = [result["rgb1"], reference["rgb1"], rgb_direct]
    # 绝对 CIE RGB 先转 XYZ，再转线性 sRGB，之后才进行显示编码。
    linear = [cie_rgb_to_linear_srgb(v) for v in arrays]
    # 三图共用球面有效像素的最大通道设置增益，避免独立缩放掩盖差异。
    maximum = max(float(v[mask].max()) for v in linear)
    gain = 1 / maximum if maximum > 0 else 0
    # 最后才进行 gamma 编码和 8 位量化；绝对计算数组仍为浮点数。
    images = [np.rint(255 * monitor_encode(v * gain)).astype(np.uint8) for v in linear]
    original_spd = np.array([normalize_spd(l.spectrum) for l in scene.lights])
    comparison = {}
    # 仅比较球体 mask 内的绝对 RGB 和显示像素，排除背景。
    for label, value, image in zip(("image_1", "image_2"), arrays[1:], images[1:]):
        difference = images[0][mask].astype(float) - image[mask].astype(float)
        comparison[label] = dict(rgb_absolute_rmse=float(np.sqrt(np.mean(
            (arrays[0][mask] - value[mask]) ** 2))), monitor_mae=float(np.abs(difference).mean()),
            monitor_max=int(np.abs(difference).max()))
    # 记录光谱误差、RGB 回算误差和积分；同色光谱的积分可以不同。
    spectrum_metrics = [dict(rmse=float(np.sqrt(np.mean((s-r)**2))),
                            max_error=float(np.abs(s-r).max()),
                            rgb_max_error=float(np.abs(spectrum_to_rgb(s)-c).max()),
                            integral=float(s @ t.weights))
                        for s, r, c in zip(recovered, original_spd, rgb)]
    for label, lv in (("image_1", reference["luminance1"]), ("image_2", luminance_direct)):
        comparison[label]["luminance_rmse_cd_m2"] = float(np.sqrt(np.mean(
            (result["luminance1"][mask] - lv[mask])**2)))
    comparison["image_1"]["radiance_rmse_w_m2_sr"] = float(np.sqrt(np.mean(
        (result["radiance"][mask] - reference["radiance"][mask])**2)))
    control_comparison = []
    for a, b in zip(result["control_points"], reference["control_points"]):
        point = np.array([a["x_mm"], a["y_mm"], a["z_mm"]])
        direct = geometry_factors(point, scene) @ rgb
        control_comparison.append(dict(name=a["name"], x_mm=a["x_mm"], y_mm=a["y_mm"], z_mm=a["z_mm"],
            radiance_A=a["radiance_w_m2_sr"], radiance_1=b["radiance_w_m2_sr"],
            luminance_A=a["luminance_cd_m2"], luminance_1=b["luminance_cd_m2"],
            luminance_2=float(683*(CIE_RGB_TO_XYZ @ direct)[1])))
    point = np.array([control_comparison[0][axis+"_mm"] for axis in "xyz"])
    geometry_rows = []
    for i, light in enumerate(scene.lights):
        terms = light_geometry(point, light, scene.center())
        geometry_rows.append(dict(source=f"L{i+1}", distance_m=float(terms["distance_m"]),
            theta_deg=float(np.degrees(np.arccos(np.clip(terms["emission_raw"], -1, 1)))),
            sigma_deg=float(np.degrees(np.arccos(np.clip(terms["incidence_raw"], -1, 1)))),
            **{k:float(terms[k]) for k in ("emitted_intensity_w_sr", "irradiance_w_m2", "lambert_factor_w_m2_sr")}))
    # Keep only the reference arrays needed for comparison, not another spectral cube.
    reference = {k: reference[k] for k in ("rgb1", "xyz", "radiance", "luminance1", "control_points")}
    return dict(scene=scene, result=result, reference=reference, rgb_direct=rgb_direct,
                luminance_direct=luminance_direct, images=images, original_spd=original_spd,
                recovered=recovered, input_rgb=rgb, original_rgb=original_rgb,
                input_matches_original=bool(np.allclose(rgb, original_rgb, rtol=1e-10, atol=1e-12)),
                spectrum_metrics=spectrum_metrics, comparison=comparison, shared_gain=gain,
                control_comparison=control_comparison, geometry_rows=geometry_rows)
