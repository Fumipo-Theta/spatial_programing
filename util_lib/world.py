from __future__ import annotations

import numpy as np
import open3d as o3d


def create_coordinate_objects() -> o3d.geometry.TriangleMesh:
    """この関数は、座標軸を表すオブジェクトを生成します."""

    def __create_spheres(xs, ys, zs, color):  # noqa: ANN202, ANN001
        spheres = []
        for x, y, z in zip(xs, ys, zs):
            sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
            sphere.compute_vertex_normals()
            sphere.paint_uniform_color(color)
            sphere.translate([x, y, z])
            spheres.append(sphere)
        return spheres

    points_1d = np.arange(-2.5, 2.51, 0.5)
    points_x = __create_spheres(points_1d, np.zeros_like(points_1d), np.zeros_like(points_1d), [1, 0.3, 0.3])
    points_y = __create_spheres(np.zeros_like(points_1d), points_1d, np.zeros_like(points_1d), [0.3, 1, 0.3])
    points_z = __create_spheres(np.zeros_like(points_1d), np.zeros_like(points_1d), points_1d, [0.3, 0.3, 1])
    coordinate = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1, origin=[0, 0, 0])
    coordinate.translate([0.3, 0, 0.3])

    floor = o3d.geometry.TriangleMesh.create_box(width=5, height=0.01, depth=5)
    floor.compute_vertex_normals()
    floor.paint_uniform_color([0.5, 0.5, 0.5])
    floor.translate([-2.5, -1, -2.5])

    world = o3d.geometry.TriangleMesh()
    for points in points_x + points_y + points_z:
        world += points
    world += coordinate
    world += floor

    return world
