from __future__ import annotations

import copy

import numpy as np
import numpy.typing as npt
import open3d as o3d
from scipy.spatial.transform import Rotation

from .types import Axis, EulerOrder, Transform


class TransformableObject:
    def __init__(
        self,
        base_model: o3d.geometry.TriangleMesh,
        initial_transform: npt.ArrayLike[float] = np.identity(4),
    ) -> None:
        self.base_model = base_model
        self.__current_transform: Transform = Transform(initial_transform)

    def get_geometry(self) -> o3d.geometry.TriangleMesh:
        """Return raw Open3D's TriangleMesh object."""
        return self.base_model

    def get_transform(self) -> Transform:
        """Return current transformation."""
        return self.__current_transform

    def copy(self) -> TransformableObject:
        return TransformableObject(copy.deepcopy(self.base_model), copy.deepcopy(self.get_transform().get_matrix()))

    def translate(self, vector_xyz: npt.ArrayLike[float]) -> None:
        """
        Translate object by a vector.

        Description:
        -----------
        - 並進ベクトルによりオブジェクトを並進変換する
        - 並進ベクトルは長さが3で、要素がそれぞれx, y, z方向の並進を表すこと

        Arguments:
        ---------
        vector_xyz: a vector of translation. The length should be 3

        """
        x, y, z = vector_xyz
        self.base_model.translate((x, y, z))
        transform = np.identity(4)
        transform[:, 3] = np.array([x, y, z, 1])
        self.__current_transform = Transform(transform) @ self.__current_transform

    def rotate(self, rotate_matrix: npt.ArrayLike[float]) -> None:
        """
        Rotate object by a matrix.

        Description:
        -----------
        - 回転行列によりオブジェクトを回転変換する
        - 回転行列はサイズが3x3であること

        Arguments:
        ---------
        rotate_matrix: 3x3のnp.ndarrayに変換可能なオブジェクト

        """
        assert np.array(rotate_matrix).shape == (3, 3), f"Invalid shape: {np.array(rotate_matrix).shape}"  # noqa: S101
        self.base_model.rotate(rotate_matrix)
        transform = np.identity(4)
        transform[:3, :3] = rotate_matrix @ self.__current_transform.get_matrix()[:3, :3]
        transform[:3, 3] = self.__current_transform.get_matrix()[:3, 3]
        self.__current_transform = Transform(transform)

    def rotate_by_euler(self, order: EulerOrder, rotation_123: npt.ArrayLike[float], degrees: bool = True) -> None:
        """
        Rotete object by a set of Euler angles.

        Description:
        -----------
        - オイラー角によりオブジェクトを回転変換する
        - オイラー角は順序と角度を指定する必要がある
        - 回転の角度は回転の順序と一致するように指定すること
            - ex. order='xyz'ならrotation_123=[rx, ry, rz]とする
        - 角度の単位は度数法か弧度法かを指定すること

        Arguments:
        ---------
        order: オイラー角の順序
        rotation_123: オイラー角の角度
        degrees: 角度の単位が度数法か弧度法かを指定する。Trueなら度数法

        """
        r1, r2, r3 = rotation_123
        rot = Rotation.from_euler(order, [r1, r2, r3], degrees=degrees).as_matrix()
        self.rotate(rot)

    def rotate_by_quaternion(self, quaternion_xyzw: npt.ArrayLike[float]) -> None:
        """
        Rotate object by a quaternion.

        Description:
        -----------
        - クォータニオンによりオブジェクトを回転変換する
        - クォータニオンはx, y, z, wの順で指定すること

        Arguments:
        ---------
        quaternion_xyzw: クォータニオンのx, y, z, wの順で指定する (wはスカラー成分)

        """
        assert np.array(quaternion_xyzw).shape == (4,), f"Invalid shape: {np.array(quaternion_xyzw).shape}"  # noqa: S101
        self.rotate(Rotation.from_quat(quaternion_xyzw).as_matrix())

    def transform(self, transform: Transform) -> None:
        """
        Transform object by a transformation matrix.

        Description:
        -----------
        - 変換行列によりオブジェクトを変換する
        - 変換行列は4x4の行列であること

        Arguments:
        ---------
        transform: 4x4のnp.ndarrayに変換可能なオブジェクト

        """
        self.base_model.transform(transform.get_matrix())
        self.__current_transform = transform @ self.__current_transform

    def mirror(self, axis: Axis) -> None:
        pass

    @staticmethod
    def load_model(file_path: str, **kwargs) -> TransformableObject:  # noqa: ANN003
        return TransformableObject(o3d.io.read_triangle_mesh(file_path, **kwargs))
