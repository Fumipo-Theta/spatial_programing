from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial.transform import Rotation

from .types import EulerOrder, ICamera, ICameraParameters, Transform


def filter_visible_points(points: np.ndarray, image_width: int, image_height: int) -> np.ndarray:
    # Filter points that are inside the image
    mask = np.where(
        (points[0, :] >= 0)
        & (points[0, :] <= image_width)  # 0 <= x <= image_width [pixel]
        & (points[1, :] >= 0)
        & (points[1, :] <= image_height),
    )  # 0 <= y <= image_height [pixel]
    return points[:, *mask], mask


@dataclass
class PinholeCameraParameters(ICameraParameters):
    focal_length: float
    principal_point: tuple[float, float]
    image_size: tuple[int, int]

    def get_intrinsic_matrix(self) -> np.ndarray:
        fx, fy = self.focal_length, self.focal_length
        cx, cy = self.principal_point
        return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    def get_image_size(self) -> tuple[int, int]:
        return self.image_size


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

    def world_to_camera(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray[bool], np.ndarray[bool]]:
        assert points.shape[0] == 3, f"Invalid shape: {points.shape}"  # noqa: S101
        ext_mat = self.get_extrinsic_matrix()
        k_mat = self.get_intrinsic_matrix()
        image_size = self.get_image_size()

        # Transform to camera coordinate
        points = np.vstack([points, np.ones(points.shape[1])])
        points_in_camera = ext_mat @ points

        # Filter points in front of camera
        mask_in_front_of_camera = points_in_camera[2] > 0
        points_in_camera = points_in_camera[:, mask_in_front_of_camera]

        # Normalize
        points_in_camera[:3] = points_in_camera[:3] / points_in_camera[2]

        points_in_image = k_mat @ points_in_camera[:3]
        points_in_image, mask_inside_image = filter_visible_points(points_in_image, image_size[0], image_size[1])

        return points_in_image, mask_in_front_of_camera, mask_inside_image


