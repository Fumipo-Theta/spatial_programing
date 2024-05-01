from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import ArrayLike


class Axis(str, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


class EulerOrder(str, Enum):
    # Intrinsic axis rotation
    XYZ = "XYZ"
    XZY = "XZY"
    YXZ = "YXZ"
    YZX = "YZX"
    ZXY = "ZXY"
    ZYX = "ZYX"
    # Extrinsic axis rotation
    xyz = "xyz"
    xzy = "xzy"
    yxz = "yxz"
    yzx = "yzx"
    zxy = "zxy"
    zyx = "zyx"


class Transform:
    def __init__(self, mat: ArrayLike) -> None:
        """
        4x4 の変換行列を表すクラス.

        Args:
        ----
        mat (ArrayLike): 4x4 の変換行列

        """
        self.mat = np.array(mat)
        assert self.mat.shape == (4, 4), f"Invalid shape: {self.mat.shape}"  # noqa: S101

    def get_matrix(self) -> ArrayLike:
        return self.mat

    def inv(self) -> Transform:
        return Transform(np.linalg.inv(self.mat))

    def T(self) -> Transform:  # noqa: N802 (numpy のメソッド名に合わせるため)
        return Transform(self.mat.T)

    def copy(self) -> Transform:
        return Transform(self.mat.copy())

    def __matmul__(self, other: Transform) -> Transform:
        return Transform(self.mat @ other.mat)

    @staticmethod
    def from_rotate_and_translate(rot: ArrayLike | None, translate: ArrayLike | None) -> Transform:
        rot_ = np.array(rot) if rot is not None else np.identity(3)
        translate_ = np.array(translate) if translate is not None else np.zeros(3)
        assert rot_.shape == (3, 3), f"Invalid shape: {np.array(rot).shape}"  # noqa: S101
        assert translate_.shape in [(3,), (1, 3)], f"Invalid shape: {np.array(translate).shape}"  # noqa: S101

        mat = np.identity(4)
        mat[:3, :3] = rot_
        mat[:3, 3] = translate_
        return Transform(mat)


@dataclass
class ICameraParameters(abc.ABC):
    @abc.abstractmethod
    def get_intrinsic_matrix(self) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_image_size(self) -> tuple[int, int]:
        pass


class ICamera(abc.ABC):
    @abc.abstractmethod
    def get_extrinsic_matrix(self) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_intrinsic_matrix(self) -> np.ndarray:
        pass

    @abc.abstractmethod
    def get_image_size(self) -> tuple[int, int]:
        pass

    @abc.abstractmethod
    def transform(self, transform: Transform) -> None:
        pass

    @abc.abstractmethod
    def copy(self) -> ICamera:
        pass

    @abc.abstractmethod
    def world_to_camera(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray[bool], np.ndarray[bool]]:
        """Return points in image coordinate, mask of points in front of camera, mask of points inside image."""
