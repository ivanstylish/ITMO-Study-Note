"""Linear RGB path tracing with explicit point-light connections."""

import numpy as np

from geometry import EPSILON, camera_rays, dot, unit


# 功能：计算空气到介质微表面界面上，非偏振光的能量反射率（报告 §3，教材 3281 式 3.4.5.7–8）。
# 公式：q=cos_i 是入射方向与微表面法向的夹角余弦，n₂=ior。斯涅尔定律给出 c_t=√(1−(1−q²)/n₂²)。
# s=(q−n₂c_t)/(q+n₂c_t)，p=(c_t−n₂q)/(c_t+n₂q)，返回 F_r=(s²+p²)/2。
# 实现范围：c_t 用于求反射率，透射贡献及折射射线路径在本实验范围外。
def fresnel(cos_i, ior):
    """Energy reflectance for unpolarized light from air into a dielectric."""
    cos_t = np.sqrt(1 - (1 - cos_i**2) / ior**2)
    s = (cos_i - ior * cos_t) / (cos_i + ior * cos_t)
    p = (cos_t - ior * cos_i) / (cos_t + ior * cos_i)
    return (s**2 + p**2) / 2


# 功能：给定材质、表面法向和入射／出射方向，计算各 RGB 通道的 BRDF（报告 §3）。
# 公式：c_i=n·wi、c_o=n·wo 都为正时，f_r=Kd/π+Ks·D·G·F_r/(4c_i c_o)，否则为 0。
# h=normalize(wi+wo)，c_h=n·h，q=wo·h。D=exp[−(1−c_h²)/(α²c_h²)]/(πα²c_h⁴) 为 Beckmann 分布。
# G=min(1, 2c_h c_i/q, 2c_h c_o/q) 描述微表面遮蔽，F_r 由 fresnel 计算。
# 实现范围：Lambert 漫反射与 Cook–Torrance 光泽反射。物体之间的遮挡由 local_radiance 检查。
def brdf(scene, material, normal, wi, wo):
    """Lambert and Cook–Torrance (3281, equations 3.4.5.1 and 3.4.5.9)."""
    # 入射与出射均须在法向半球内。朗伯 BRDF 为 Kd/π，接收余弦由辐照度或路径权重处理。
    ni, no = dot(normal, wi), dot(normal, wo)
    same_side = (ni > 0) & (no > 0)
    result = scene.kd[material] / np.pi
    result[~same_side] = 0
    glossy = same_side & np.any(scene.ks[material] > 0, axis=1)
    # 报告 §3：半程向量 h 是能把 wi 镜面反射到 wo 的微表面法向。
    h = unit((wi + wo)[glossy])
    nh = np.clip(dot(normal[glossy], h), 1e-10, 1)
    oh = np.clip(dot(wo[glossy], h), 1e-10, 1)
    alpha2 = scene.roughness[material[glossy]]**2
    tan2 = (1 - nh**2) / nh**2
    # D 为 Beckmann 法向分布，G 描述微表面遮蔽，F_r 是单个微表面的 Fresnel 能量反射率。
    distribution = np.exp(-tan2 / alpha2) / (np.pi * alpha2 * nh**4)
    geometry = np.minimum(1, 2 * nh * np.minimum(ni[glossy], no[glossy]) / oh)
    reflection = fresnel(oh, scene.ior[material[glossy]])
    specular = distribution * geometry * reflection / (4 * ni[glossy] * no[glossy])
    result[glossy] += scene.ks[material[glossy]] * specular[:, None]
    return result


# 功能：对同一盏点光源，逐点计算指向灯的单位方向 wi、距离 R 和各通道辐照度 E（报告 §3）。
# 公式：R=‖灯位置−表面点‖，wi=(灯位置−表面点)/R，E=I₀·[−wi·H]₊·[n·wi]₊/R²。
# H 为单位灯轴，[a]₊=max(a, 0)。R≤ε 时返回零辐照度，避免距离趋零时除以 R²。
# 实现范围：理想点源的发射余弦、接收余弦和平方反比。可见性和反射交给 local_radiance。
def point_irradiance(light, position, normal):
    delta = light.position - position
    distance = np.linalg.norm(delta, axis=1)
    wi = unit(delta)
    # wi 从表面指向灯，计算灯的发射角时方向取反。
    emission = np.maximum(dot(-wi, light.axis), 0)
    reception = np.maximum(dot(wi, normal), 0)
    # 将各通道的辐射强度（W/sr）换算成辐照度（W/m²）。
    falloff = np.divide(emission * reception, distance**2,
                        out=np.zeros_like(distance), where=distance > EPSILON)
    return wi, distance, falloff[:, None] * light.intensity


# 功能：在当前命中点显式连接每盏点光源，计算沿 wo 返回上一顶点的局部直射辐亮度（报告 §4）。
# 教材 3275 §5.4 式 (5.15) 与图 5.9。本场景只有两个点光源，逐灯求和即可。
# 公式：L_d(x,wo)=Σ_j V(x,灯_j)·E_j(x)·f_r(x,wi_j,wo)，单位为 W/(m²·sr)。
# V 由阴影射线确定，灯前有遮挡取 0，否则取 1。接收余弦已包含在 E_j 中。
# 实现范围：下一事件估计中的逐灯直接贡献。路径权重与间接贡献归属由 trace 处理。
def local_radiance(scene, position, normal, wo, material):
    result = np.zeros_like(position)
    origin = position + EPSILON * normal
    for light in scene.lights:
        wi, _, irradiance = point_irradiance(light, position, normal)
        lit = np.flatnonzero(np.any(irradiance > 0, axis=1))
        shadow_delta = light.position - origin[lit]
        shadow_end = np.linalg.norm(shadow_delta, axis=1)
        # 起点沿法向偏移以避开自相交，求交上限取到灯的距离减 ε，灯后物体不投影到该点。
        _, blocker = scene.mesh.intersect(origin[lit], unit(shadow_delta), shadow_end - EPSILON)
        lit = lit[blocker == -1]
        factor = brdf(scene, material[lit], normal[lit], wi[lit], wo[lit])
        result[lit] += factor * irradiance[lit]
    return result


# 功能：把独立均匀随机数 u、v 变成以表面法向 n 为轴的余弦加权续射方向（报告 §4）。
# 公式：r=√u、φ=2πv，局部方向为 (r cosφ, r sinφ, √(1−u))，再用切向、双切向和 n 转入场景坐标。
# 对每单位立体角，方向概率密度为 p(wi)=(n·wi)/π。函数只返回方向，trace 使用化简后的权重。
# 实现范围：漫反射和光泽材质都共用余弦采样。Beckmann 分布在此项目中用于评估 BRDF。
def cosine_direction(normal, u, v):
    """Cosine hemisphere PDF p(wi) = cos(theta)/pi, per unit solid angle."""
    z = np.sqrt(1 - u)
    radius = np.sqrt(u)
    phi = 2 * np.pi * v
    hint = np.zeros_like(normal)
    hint[:, 0] = np.abs(normal[:, 1]) > 0.99
    hint[:, 1] = 1 - hint[:, 0]
    # 将围绕局部 Z 轴采样的方向放进以实际表面法向为轴的世界坐标基。
    tangent = unit(np.cross(hint, normal))
    bitangent = np.cross(normal, tangent)
    return (tangent * (radius * np.cos(phi))[:, None]
            + bitangent * (radius * np.sin(phi))[:, None] + normal * z[:, None])


# 功能：批量执行反向路径追踪，从主射线起步，逐次求最近交点、估计局部照明并生成续射（报告 §4）。
# 教材 3275 §5.1 式 (5.2) 的路径权重与 §5.4 图 5.9 的显式光源连接对应此循环。
# 公式：L_path=Σ_i β_i·L_d(x_i,wo)，β₀=1，β_{i+1}=β_i·f_r·(n·wi)/p(wi)=β_i·π·f_r。
# 首次命中的项存入 primary，后续命中的项累加到 indirect，返回每条路径的线性 RGB 贡献。
# 实现范围：每次命中最多续射一次。路径在离开场景或达到固定深度时停止，深度为 random.shape[1]+1。
# 俄罗斯轮盘终止与透射路径在本算法范围外。
def trace(scene, origins, directions, random):
    count = len(origins)
    active = np.arange(count)
    throughput = np.ones((count, 3))
    primary = np.zeros((count, 3))
    indirect = np.zeros_like(primary)
    depth = random.shape[1] + 1

    for bounce in range(depth):
        distance, triangles = scene.mesh.intersect(origins, directions)
        hits = triangles >= 0
        active, triangles = active[hits], triangles[hits]
        if len(active) == 0:
            break
        rays = directions[hits]
        position = origins[hits] + distance[hits, None] * rays
        normal = scene.mesh.normals[triangles]
        wo = -rays
        # 令法向朝向路径的前一个顶点，使出射方向 ω_o 位于该法向的正半球。
        normal = np.where((dot(normal, wo) < 0)[:, None], -normal, normal)
        material = scene.mesh.materials[triangles]
        # 用累计权重 β_i 把各命中处的局部直射贡献带回相机，首命中为直接项，之后归间接项。
        contribution = throughput[active] * local_radiance(scene, position, normal, wo, material)
        if bounce == 0:
            primary[active] = contribution
        else:
            indirect[active] += contribution
        if bounce + 1 == depth:
            break
        u, v = random[active, bounce].T
        directions = cosine_direction(normal, u, v)
        # β_{i+1}=β_i·f_r·cosθ/p(ω_i)=β_i·π·f_r，纯漫反射时每次反射只乘 Kd。
        throughput[active] *= np.pi * brdf(scene, material, normal, directions, wo)
        origins = position + EPSILON * normal
    return primary, indirect


# 功能：组织整帧渲染，按批次为各像素采样相机射线、调用 trace，并分别汇总直接和间接光（报告 §5）。
# 公式：每项像素值 L_pixel=(1/N)·Σ_s L_path,s，其中 N=samples，两项共享同一批路径。
# 当 N=m² 时，每个子格各取一个随机点，像素内的偏移为 (子格坐标+随机偏移)/m。其余 N 使用均匀随机采样。
# 实现范围：返回两张线性 RGB 辐亮度数组。总量合成、白点归一化与伽马编码由 experiment.py 处理。
def render(scene, camera, size, samples, depth, seed, progress=None):
    rng = np.random.default_rng(seed)
    direct = np.empty((size * size, 3))
    indirect = np.empty_like(direct)
    # 报告 §5：两张图从同一批主射线分出首命中与后续贡献，比较时共享子像素和轮廓采样。
    batch_size = min(1024, max(1, 8192 // samples))
    for start in range(0, size * size, batch_size):
        stop = min(start + batch_size, size * size)
        y, x = np.divmod(np.arange(start, stop), size)
        draws = rng.random((len(x), samples, depth, 2))
        image_jitter = draws[:, :, 0]
        # 完全平方数才走网格分层，报告的 36 条路径对应 6×6 个子格，每格抖动采样一次。
        if (strata := int(np.sqrt(samples)))**2 == samples:
            sy, sx = np.divmod(np.arange(samples), strata)
            image_jitter = (image_jitter + np.stack((sx, sy), axis=1)) / strata
        px = (x[:, None] + image_jitter[:, :, 0]).ravel()
        py = (y[:, None] + image_jitter[:, :, 1]).ravel()
        origins, directions = camera_rays(camera, px, py, size, size)
        path_random = draws[:, :, 1:].reshape(len(px), depth - 1, 2)
        first, rest = trace(scene, origins, directions, path_random)
        # 各像素分别对线性 RGB 的直接和间接贡献求样本均值，之后才做显示编码。
        direct[start:stop] = first.reshape(-1, samples, 3).mean(axis=1)
        indirect[start:stop] = rest.reshape(-1, samples, 3).mean(axis=1)
        if progress is not None:
            progress(stop / (size * size))
    return direct.reshape(size, size, 3), indirect.reshape(size, size, 3)
