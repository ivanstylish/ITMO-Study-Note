"""Build the open room and the objects from editable JSON parameters."""

from dataclasses import dataclass

import numpy as np

from geometry import Mesh, unit


@dataclass(frozen=True)
class PointLight:
    # 表 2：位置用米，axis 是单位发射轴 H，intensity 是轴向 RGB 辐射强度 I₀（W/sr）。
    position: np.ndarray
    axis: np.ndarray
    intensity: np.ndarray


@dataclass(frozen=True)
class Scene:
    # 三角形保存材质索引，命中后用索引查找表 3 的 Kd 及 Cook–Torrance 参数。
    mesh: Mesh
    kd: np.ndarray
    ks: np.ndarray
    roughness: np.ndarray
    ior: np.ndarray
    lights: list[PointLight]


def vector(value, name):
    result = np.asarray(value, dtype=float)
    if result.shape != (3,) or not np.isfinite(result).all():
        raise ValueError(f"{name}: требуются три конечных числа")
    return result


def build_scene(config):
    camera = config["camera"]
    eye = vector(camera["eye"], "camera.eye")
    target = vector(camera["target"], "camera.target")
    if np.array_equal(eye, target) or not 1 <= camera["fov_y"] <= 160:
        raise ValueError("Проверьте направление камеры и угол обзора (1–160°)")

    materials = config["materials"]
    material_ids = {name: i for i, name in enumerate(materials)}
    kd = np.array([vector(m["kd"], "kd") for m in materials.values()])
    ks = np.array([vector(m["ks"], "ks") for m in materials.values()])
    roughness = np.array([m["roughness"] for m in materials.values()], dtype=float)
    ior = np.array([m["ior"] for m in materials.values()], dtype=float)
    if (np.any(kd < 0) or np.any(ks < 0) or np.any(kd + ks > 1)
            or not np.all((0.05 <= roughness) & (roughness <= 1))
            or not np.all(np.isfinite(ior) & (ior > 1))):
        raise ValueError("Материалы: kd, ks ≥ 0, kd + ks ≤ 1, 0.05 ≤ roughness ≤ 1, ior > 1")

    triangles, ids = [], []

    def quad(vertices, material):
        # 报告 §2：每个四边形拆成两个共享材质的三角形，默认房间五面、每个箱体六面。
        a, b, c, d = vertices
        triangles.extend(((a, b, c), (a, c, d)))
        ids.extend([material_ids[material]] * 2)

    room = config["room"]
    width, height, depth = vector(room["size"], "room.size")
    if min(width, height, depth) <= 0:
        raise ValueError("Размеры комнаты должны быть положительными")
    l, r, b, f = -width / 2, width / 2, -depth / 2, depth / 2
    quad(((l, 0, b), (l, 0, f), (r, 0, f), (r, 0, b)), room["floor"])
    quad(((l, height, b), (r, height, b), (r, height, f), (l, height, f)), room["ceiling"])
    quad(((l, 0, b), (r, 0, b), (r, height, b), (l, height, b)), room["back"])
    quad(((l, 0, b), (l, height, b), (l, height, f), (l, 0, f)), room["left"])
    quad(((r, 0, b), (r, 0, f), (r, height, f), (r, height, b)), room["right"])

    faces = ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
             (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0))
    for box in config["boxes"]:
        center = vector(box["center"], "box.center")
        sx, sy, sz = vector(box["size"], "box.size") / 2
        angle = np.deg2rad(float(box["yaw"]))
        if min(sx, sy, sz) <= 0 or not np.isfinite(angle):
            raise ValueError("Проверьте размеры и поворот параллелепипеда")
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.array(((c, 0, s), (0, 1, 0), (-s, 0, c)))
        ring = ((-sx, -sz), (sx, -sz), (sx, sz), (-sx, sz))
        vertices = np.array([(x, y, z) for y in (-sy, sy) for x, z in ring])
        # 表 1：顶点先绕穿过箱体中心的局部 Y 轴转 yaw，再平移到世界坐标中的 center。
        vertices = vertices @ rotation.T + center
        for face in faces:
            quad(vertices[list(face)], box["material"])

    lights = []
    for source in config["lights"]:
        position = vector(source["position"], "light.position")
        axis = vector(source["axis"], "light.axis")
        intensity = vector(source["intensity"], "light.intensity")
        if not np.any(axis) or np.any(intensity < 0):
            raise ValueError("Ось источника должна быть ненулевой, сила излучения — неотрицательной")
        lights.append(PointLight(position, unit(axis), intensity))
    return Scene(Mesh(triangles, ids), kd, ks, roughness, ior, lights)
