from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_OBJ = ROOT / "docs" / "infinity_logo_3d.obj"
OUTPUT_MTL = ROOT / "docs" / "infinity_logo_3d.mtl"


def add_vertex(vertices: list[tuple[float, float, float]], x: float, y: float, z: float) -> int:
    vertices.append((x, y, z))
    return len(vertices)


def add_face(
    faces: list[tuple[str | None, tuple[int, int, int]]],
    a: int,
    b: int,
    c: int,
    material: str | None,
) -> None:
    faces.append((material, (a, b, c)))


def ribbon_color_group(ratio: float) -> str:
    palette = [
        "ribbon_blue",
        "ribbon_cyan",
        "ribbon_violet",
        "ribbon_magenta",
        "ribbon_orange",
        "ribbon_gold",
    ]
    idx = min(int(ratio * len(palette)), len(palette) - 1)
    return palette[idx]


def center_point(t: float) -> tuple[float, float]:
    x = 5.5 * math.sin(t)
    y = 2.85 * math.sin(t) * math.cos(t)
    return x, y


def tangent(t: float) -> tuple[float, float]:
    dt = 1e-3
    x1, y1 = center_point(t - dt)
    x2, y2 = center_point(t + dt)
    tx, ty = x2 - x1, y2 - y1
    length = math.hypot(tx, ty)
    return tx / length, ty / length


def width_at(t: float) -> float:
    base = 0.70
    taper = 0.22 * (1.0 - abs(math.cos(t)))
    return base + taper


def add_ribbon(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[str | None, tuple[int, int, int]]],
) -> None:
    steps = 360
    thickness = 0.36
    rings: list[tuple[int, int, int, int]] = []

    for i in range(steps):
        t = (i / steps) * math.tau
        cx, cy = center_point(t)
        tx, ty = tangent(t)
        nx, ny = -ty, tx
        half_w = width_at(t) / 2.0

        left_top = add_vertex(vertices, cx + nx * half_w, cy + ny * half_w, thickness / 2.0)
        right_top = add_vertex(vertices, cx - nx * half_w, cy - ny * half_w, thickness / 2.0)
        left_bottom = add_vertex(vertices, cx + nx * half_w, cy + ny * half_w, -thickness / 2.0)
        right_bottom = add_vertex(vertices, cx - nx * half_w, cy - ny * half_w, -thickness / 2.0)
        rings.append((left_top, right_top, left_bottom, right_bottom))

    for i in range(steps):
        next_i = (i + 1) % steps
        mat = ribbon_color_group(i / steps)

        lt1, rt1, lb1, rb1 = rings[i]
        lt2, rt2, lb2, rb2 = rings[next_i]

        add_face(faces, lt1, rt1, rt2, mat)
        add_face(faces, lt1, rt2, lt2, mat)

        add_face(faces, lb1, rb2, rb1, mat)
        add_face(faces, lb1, lb2, rb2, mat)

        add_face(faces, lt1, lt2, lb2, mat)
        add_face(faces, lt1, lb2, lb1, mat)

        add_face(faces, rt1, rb2, rt2, mat)
        add_face(faces, rt1, rb1, rb2, mat)


def add_uv_sphere(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[str | None, tuple[int, int, int]]],
    center: tuple[float, float, float],
    radius: float,
    material: str,
    lat_steps: int = 10,
    lon_steps: int = 14,
) -> None:
    cx, cy, cz = center
    rings: list[list[int]] = []

    top = add_vertex(vertices, cx, cy, cz + radius)
    bottom = add_vertex(vertices, cx, cy, cz - radius)

    for lat in range(1, lat_steps):
        phi = math.pi * lat / lat_steps
        ring: list[int] = []
        for lon in range(lon_steps):
            theta = math.tau * lon / lon_steps
            x = cx + radius * math.sin(phi) * math.cos(theta)
            y = cy + radius * math.sin(phi) * math.sin(theta)
            z = cz + radius * math.cos(phi)
            ring.append(add_vertex(vertices, x, y, z))
        rings.append(ring)

    first_ring = rings[0]
    for i in range(lon_steps):
        add_face(faces, top, first_ring[(i + 1) % lon_steps], first_ring[i], material)

    for upper, lower in zip(rings, rings[1:]):
        for i in range(lon_steps):
            a = upper[i]
            b = upper[(i + 1) % lon_steps]
            c = lower[i]
            d = lower[(i + 1) % lon_steps]
            add_face(faces, a, b, d, material)
            add_face(faces, a, d, c, material)

    last_ring = rings[-1]
    for i in range(lon_steps):
        add_face(faces, bottom, last_ring[i], last_ring[(i + 1) % lon_steps], material)


def star_points(cx: float, cy: float, outer_r: float, inner_r: float, z: float) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for i in range(8):
        angle = math.radians(-90 + i * 45)
        radius = outer_r if i % 2 == 0 else inner_r
        points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, z))
    return points


def add_star(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[str | None, tuple[int, int, int]]],
    center: tuple[float, float, float],
    outer_r: float,
    inner_r: float,
    thickness: float,
    material: str,
) -> None:
    cx, cy, cz = center
    top_ring = [add_vertex(vertices, *p) for p in star_points(cx, cy, outer_r, inner_r, cz + thickness / 2.0)]
    bottom_ring = [add_vertex(vertices, *p) for p in star_points(cx, cy, outer_r, inner_r, cz - thickness / 2.0)]
    top_center = add_vertex(vertices, cx, cy, cz + thickness / 2.0)
    bottom_center = add_vertex(vertices, cx, cy, cz - thickness / 2.0)

    count = len(top_ring)
    for i in range(count):
        ni = (i + 1) % count
        add_face(faces, top_center, top_ring[i], top_ring[ni], material)
        add_face(faces, bottom_center, bottom_ring[ni], bottom_ring[i], material)
        add_face(faces, top_ring[i], bottom_ring[i], bottom_ring[ni], material)
        add_face(faces, top_ring[i], bottom_ring[ni], top_ring[ni], material)


def add_bubbles_and_star(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[str | None, tuple[int, int, int]]],
) -> None:
    bubbles = [
        (-4.95, 0.40, 0.30, 0.28),
        (-4.50, -1.85, 0.26, 0.33),
        (-3.45, 1.65, 0.18, 0.19),
        (-2.55, 1.95, 0.16, 0.15),
        (-1.55, 2.10, 0.24, 0.18),
        (-2.05, 1.15, 0.20, 0.20),
        (-4.15, 1.55, 0.14, 0.16),
    ]
    for x, y, z, r in bubbles:
        add_uv_sphere(vertices, faces, (x, y, z), r, "bubble_white")

    add_star(vertices, faces, (5.85, 2.35, 0.30), 0.58, 0.21, 0.18, "star_gold")


def write_materials(path: Path) -> None:
    materials = {
        "ribbon_blue": (0.06, 0.33, 0.95),
        "ribbon_cyan": (0.18, 0.84, 0.96),
        "ribbon_violet": (0.44, 0.12, 0.95),
        "ribbon_magenta": (0.88, 0.18, 0.72),
        "ribbon_orange": (0.98, 0.34, 0.10),
        "ribbon_gold": (0.99, 0.84, 0.16),
        "bubble_white": (0.92, 0.97, 1.00),
        "star_gold": (1.00, 0.90, 0.32),
    }

    lines = ["# Simple materials for the generated infinity logo"]
    for name, (r, g, b) in materials.items():
        lines.extend(
            [
                f"newmtl {name}",
                f"Kd {r:.4f} {g:.4f} {b:.4f}",
                "Ka 0.0500 0.0500 0.0500",
                "Ks 0.2500 0.2500 0.2500",
                "Ns 80.0000",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_obj(
    path: Path,
    mtl_name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[str | None, tuple[int, int, int]]],
) -> None:
    lines = [f"mtllib {mtl_name}", "o InfinityLogo3D"]

    for x, y, z in vertices:
        lines.append(f"v {x:.6f} {y:.6f} {z:.6f}")

    current_material: str | None = None
    for material, (a, b, c) in faces:
        if material != current_material and material is not None:
            lines.append(f"usemtl {material}")
            current_material = material
        lines.append(f"f {a} {b} {c}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_OBJ.parent.mkdir(parents=True, exist_ok=True)

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[str | None, tuple[int, int, int]]] = []

    add_ribbon(vertices, faces)
    add_bubbles_and_star(vertices, faces)

    write_materials(OUTPUT_MTL)
    write_obj(OUTPUT_OBJ, OUTPUT_MTL.name, vertices, faces)

    print(f"Wrote {OUTPUT_OBJ}")
    print(f"Wrote {OUTPUT_MTL}")
    print(f"Vertices: {len(vertices)}")
    print(f"Faces: {len(faces)}")


if __name__ == "__main__":
    main()
