"""Perspective camera and intersections with a triangle mesh (metres)."""

import numpy as np


EPSILON = 1e-6


def dot(a, b):
    return np.einsum("...i,...i->...", a, b)


def unit(v):
    length = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.divide(v, length, out=np.zeros_like(v), where=length > 0)


def camera_rays(camera, x, y, width, height):
    eye = np.asarray(camera["eye"], dtype=float)
    # 报告 §3：用视线和参考上方向构造相机正交基，避免参考方向与视线近乎平行。
    forward = unit(np.asarray(camera["target"], dtype=float) - eye)
    hint = (1, 0, 0) if abs(forward[1]) > 0.99 else (0, 1, 0)
    right = unit(np.cross(forward, hint))
    up = np.cross(right, forward)
    # 把含子像素偏移的坐标映射到距相机 1 的虚拟成像平面，图像行向下而相机 up 向上。
    half_height = np.tan(np.deg2rad(camera["fov_y"]) / 2)
    horizontal = ((2 * x / width - 1) * width / height * half_height)[:, None]
    vertical = ((1 - 2 * y / height) * half_height)[:, None]
    directions = unit(forward + horizontal * right + vertical * up)
    return np.broadcast_to(eye, directions.shape), directions


class Mesh:
    def __init__(self, triangles, materials):
        a, b, c = np.asarray(triangles, dtype=float).transpose(1, 0, 2)
        e1, e2 = b - a, c - a
        cross = np.cross(e1, e2)
        if np.any(np.linalg.norm(cross, axis=1) == 0):
            raise ValueError("Сетка содержит вырожденный треугольник")
        self.normals = unit(cross)
        # 预计算面法向、平面常量和重心坐标系数，供所有主射线、反射射线和阴影射线复用。
        area2 = dot(cross, self.normals)
        self.u = np.cross(e2, self.normals) / area2[:, None]
        self.v = np.cross(self.normals, e1) / area2[:, None]
        self.offset = dot(a, self.normals)
        self.u_offset = dot(a, self.u)
        self.v_offset = dot(a, self.v)
        self.materials = np.asarray(materials, dtype=int)

    def intersect(self, origin, direction, limit=np.inf):
        """Return closest (distance, triangle index). Misses are (inf, -1)."""
        # 报告 §3：将 P(t)=o+tω 代入平面方程，得 t=((a−o)·n)/(ω·n)，跳过近乎平行的射线。
        denominator = np.einsum("ij,kj->ik", direction, self.normals)
        numerator = self.offset - np.einsum("ij,kj->ik", origin, self.normals)
        t = np.divide(numerator, denominator, out=np.zeros_like(numerator),
                      where=np.abs(denominator) > 1e-10)
        limit = np.broadcast_to(limit, (len(origin),))
        ray, tri = np.nonzero((t > EPSILON) & (t < limit[:, None]))
        # P=a+u(b−a)+v(c−a)，仅保留 u≥0、v≥0、u+v≤1 的交点（含边界容差）。
        points = origin[ray] + t[ray, tri, None] * direction[ray]
        u = dot(points, self.u[tri]) - self.u_offset[tri]
        v = dot(points, self.v[tri]) - self.v_offset[tri]
        inside = (u >= -1e-10) & (v >= -1e-10) & (u + v <= 1 + 1e-10)
        distances = np.full_like(t, np.inf)
        distances[ray[inside], tri[inside]] = t[ray[inside], tri[inside]]
        # 材质和法向取自最近的有效三角形，无交点时返回 (inf, -1)。
        nearest = distances.argmin(axis=1)
        depth = distances[np.arange(len(origin)), nearest]
        return depth, np.where(np.isfinite(depth), nearest, -1)
