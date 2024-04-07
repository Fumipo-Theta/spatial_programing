from __future__ import annotations

import copy

import open3d as o3d
from scipy.spatial.transform import Rotation

from .types import Axis, EulerOrder  # noqa: TCH001


class TransformableObject:
    def __init__(self, base_model: o3d.geometry.TriangleMesh) -> None:
        self.base_model = base_model

    def get_geometry(self) -> o3d.geometry.TriangleMesh:
        return self.base_model

    def copy(self) -> TransformableObject:
        return TransformableObject(copy.deepcopy(self.base_model))

    def translate(self, *, x: float = 0, y: float = 0, z: float = 0) -> None:
        self.base_model.translate((x, y, z))

    def rotate_euler(self,
                     order: EulerOrder,
                     *,
                     x: float = 0, y: float = 0, z: float = 0,
                     degrees: bool = True) -> None:
        self.base_model.rotate(Rotation.from_euler(order, [x, y, z], degrees=degrees).as_matrix())

    def mirror(self, axis: Axis) -> None:
        pass

    @staticmethod
    def load_model(file_path: str, **kwargs) -> TransformableObject:
        return TransformableObject(o3d.io.read_triangle_mesh(file_path, **kwargs))
