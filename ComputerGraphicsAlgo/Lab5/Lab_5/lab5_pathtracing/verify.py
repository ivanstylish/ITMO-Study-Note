"""Analytical checks for the illumination and path weights used in the report."""

import numpy as np

from geometry import Mesh
from render import brdf, cosine_direction, fresnel, local_radiance, point_irradiance, trace
from scene import PointLight, Scene


def main():
    # 报告 §7 表 5：法向照射、R=2 m、I₀=20 W/sr、Kd=0.6，手算亮度应为 3/π。
    triangle = np.array([[-2., -2., 0.], [2., -2., 0.], [0., 2., 0.]])
    position = np.array([[0., 0., 0.]])
    normal = np.array([[0., 0., 1.]])
    material = np.array([0])
    intensity = np.full(3, 20.)
    light = PointLight(np.array([0., 0., 2.]), -normal[0], intensity)
    far_light = PointLight(np.array([0., 0., 4.]), light.axis, intensity)
    turned_light = PointLight(light.position, np.array([0.6, 0., -0.8]), intensity)
    turned_normal = np.array([[0.6, 0., 0.8]])

    def surface(triangles, ks=0., source=light):
        return Scene(Mesh(triangles, [0] * len(triangles)), np.full((1, 3), 0.6),
                     np.full((1, 3), ks), np.array([0.32]), np.array([1.55]), [source])

    def local(triangles):
        return local_radiance(surface(triangles), position, normal, normal, material)[0, 0]

    def irradiance(source, receiver=normal):
        return point_irradiance(source, position, receiver)[2][0, 0]

    normal_fresnel = ((1.55 - 1) / (1.55 + 1))**2
    glossy = surface([triangle], ks=0.4)
    # 让灯只照第二个平面并固定续射方向，隔离互反射项，验证第一跳乘 Kd 后得到 7.2/π。
    upward_light = PointLight(np.array([0., 0., 1.]), normal[0], intensity)
    first, later = trace(surface([triangle, triangle + [0, 0, 2]], source=upward_light),
                         np.array([[0., 0., 0.5]]), -normal, np.zeros((1, 1, 2)))
    checks = [
        ("Lambert radiance", local([triangle]), 3 / np.pi),
        ("Occluder before light", local([triangle, triangle + [0, 0, 1]]), 0.),
        ("Occluder behind light", local([triangle, triangle + [0, 0, 3]]), 3 / np.pi),
        ("Inverse-square ratio", irradiance(light) / irradiance(far_light), 4.),
        ("Tilted receiver", irradiance(light, turned_normal), 4.),
        ("Tilted light axis", irradiance(turned_light), 4.),
        ("Fresnel at normal incidence", fresnel(1., 1.55), normal_fresnel),
        ("Cook–Torrance plus Lambert at normal incidence",
         brdf(glossy, material, normal, normal, normal)[0, 0],
         0.6 / np.pi + 0.4 * normal_fresnel / (4 * np.pi * 0.32**2)),
        ("Two-hit path, first surface", first[0, 0], 0.),
        ("Two-hit path, indirect contribution", later[0, 0], 7.2 / np.pi),
    ]
    for name, actual, expected in checks:
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12, err_msg=name)
        print(f"{name}: {actual:.10g} (expected {expected:.10g})")

    np.testing.assert_allclose(brdf(glossy, material, normal, normal, turned_normal),
                               brdf(glossy, material, normal, turned_normal, normal), rtol=1e-12)
    # 对余弦加权半球，μ=n·ω 的边际密度为 2μ，单位方向的 μ 样本均值应接近 2/3。
    rng = np.random.default_rng(5)
    u, v = rng.random((2, 100_000))
    directions = cosine_direction(np.broadcast_to(normal, (len(u), 3)), u, v)
    np.testing.assert_allclose(np.linalg.norm(directions, axis=1), 1.)
    mean_cosine = directions[:, 2].mean()
    np.testing.assert_allclose(mean_cosine, 2 / 3, atol=0.004)
    print(f"Cosine sample mean: {mean_cosine:.10g} (expected {2 / 3:.10g})")


if __name__ == "__main__":
    main()
