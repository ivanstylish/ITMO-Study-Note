"""White-sphere experiment and controlled comparison with the Lab 3 paths."""
from dataclasses import replace
import numpy as np
from .core.color_conversion import (CIE_RGB_TO_XYZ, XYZ_TO_LINEAR_SRGB,
                                    scene_rgb, spectrum_to_rgb, monitor_encode)
from .core.geometry import validate
from .core.rendering import calculate
from .core.spectral import default_parameters, load_tables, normalize_spd
from .reconstruction import reconstruct


def white_scene():
    return default_parameters()


def run(scene=None, light_rgb=None):
    scene = white_scene() if scene is None else scene
    validate(scene)
    if not np.allclose(scene.reflectance, 1, rtol=0, atol=1e-12):
        raise ValueError("ЛР4: требуется белый ламбертовский отражатель, kd=1")
    # I0 is the original scene intensity. Keep this input scale fixed in both paths.
    scene = replace(scene, lights=tuple(replace(light, spectrum=tuple(normalize_spd(light.spectrum)))
                                       for light in scene.lights))
    t = load_tables()
    _, original_rgb = scene_rgb(scene)
    rgb = original_rgb if light_rgb is None else np.asarray(light_rgb, float)
    if rgb.shape != (len(scene.lights), 3):
        raise ValueError("Требуется RGB для каждого источника")
    recovered = np.array([reconstruct(v) for v in rgb])
    rebuilt = replace(scene, lights=tuple(replace(light, spectrum=tuple(s))
                      for light, s in zip(scene.lights, recovered)))
    reference = calculate(scene)
    result = calculate(rebuilt)
    mask = result["mask"]
    arrays = [result["rgb1"], reference["rgb1"], reference["rgb2"]]
    linear = [v @ CIE_RGB_TO_XYZ.T @ XYZ_TO_LINEAR_SRGB.T for v in arrays]
    maximum = max(float(v[mask].max()) for v in linear)
    gain = 1 / maximum if maximum > 0 else 0
    images = [np.rint(255 * monitor_encode(v * gain)).astype(np.uint8) for v in linear]
    original_spd = np.array([normalize_spd(l.spectrum) for l in scene.lights])
    comparison = {}
    for label, value, image in zip(("image_1", "image_2"), arrays[1:], images[1:]):
        difference = images[0][mask].astype(float) - image[mask].astype(float)
        comparison[label] = dict(rgb_absolute_rmse=float(np.sqrt(np.mean(
            (arrays[0][mask] - value[mask]) ** 2))), monitor_mae=float(np.abs(difference).mean()),
            monitor_max=int(np.abs(difference).max()))
    spectrum_metrics = [dict(rmse=float(np.sqrt(np.mean((s-r)**2))),
                            max_error=float(np.abs(s-r).max()),
                            rgb_max_error=float(np.abs(spectrum_to_rgb(s)-c).max()),
                            integral=float(s @ t.weights))
                        for s, r, c in zip(recovered, original_spd, rgb)]
    return dict(scene=scene, result=result, images=images, original_spd=original_spd,
                recovered=recovered, input_rgb=rgb, spectrum_metrics=spectrum_metrics,
                comparison=comparison, shared_gain=gain)


