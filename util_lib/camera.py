from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation

from .types import EulerOrder, ICamera, PinholeCameraParameters, Transform


class SimplePinholeCamera(ICamera):
    def __init__(
        self,
        camera_param: PinholeCameraParameters,
        initial_pose_in_world: Transform = Transform(np.identity(4)),
    ) -> None:
        self.__intrinsic_parameters = camera_param
        self.__current_transform = initial_pose_in_world

    def transform(self, transform: Transform) -> None:
        self.__current_transform = transform @ self.__current_transform

    def get_extrinsic_matrix(self) -> np.ndarray:
        transform = self.__current_transform.get_matrix()
        extrinsic = np.identity(4)
        extrinsic[:3, :3] = transform[:3, :3].T
        extrinsic[:3, 3] = -transform[:3, :3].T @ transform[:3, 3]
        return extrinsic

    def get_extrinsic_parameters(self, rotate_order: EulerOrder) -> tuple[np.typing.ArrayLike, np.typing.ArrayLike]:
        transform = self.__current_transform.get_matrix()
        extrinsic = np.identity(4)
        extrinsic[:3, :3] = transform[:3, :3].T
        extrinsic[:3, 3] = -transform[:3, :3].T @ transform[:3, 3]
        return Rotation.from_matrix(extrinsic[:3, :3]).as_euler(rotate_order, degrees=True), extrinsic[:3, 3]

    def get_intrinsic_matrix(self) -> np.ndarray:
        return self.__intrinsic_parameters.get_intrinsic_matrix()

    def get_image_size(self) -> tuple[int, int]:
        return self.__intrinsic_parameters.get_image_size()

    def copy(self) -> ICamera:
        return SimplePinholeCamera(self.__intrinsic_parameters, self.__current_transform.copy())
