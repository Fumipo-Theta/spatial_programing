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


@dataclass
class OCamCalibOmniDirectionalCameraParameters(ICameraParameters):
    world_to_cam_params: np.typing.ArrayLike[float]
    affine_params_cde: tuple[float, float, float]
    principal_point: tuple[float, float]
    image_size: tuple[int, int]
    fov: float

    def get_intrinsic_matrix(self) -> np.ndarray:
        cx, cy = self.principal_point
        return np.array([1, 0, cx], [0, 1, cy], [0, 0, 1])

    def get_image_size(self) -> tuple[int, int]:
        return self.image_size


class OCamCalibOmniDirectionalCamera(ICamera):

    """
    Implementation of Fish Eye Camera by OCamCalib.

    Note:
    ----
    - For model details, see the following URL:
        https://sites.google.com/site/scarabotix/ocamcalib-omnidirectional-camera-calibration-toolbox-for-matlab

    """

    def __init__(
        self,
        camera_param: OCamCalibOmniDirectionalCameraParameters,
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

    def get_intrinsic_matrix(self) -> np.ndarray:
        raise Exception("Intrinsic parameter for OCamCalibFishEyeCamera has no meaning.")

    def get_image_size(self) -> tuple[int, int]:
        return self.__intrinsic_parameters.get_image_size()

    def copy(self) -> ICamera:
        return OCamCalibOmniDirectionalCamera(self.__intrinsic_parameters, self.__current_transform.copy())

    def world_to_camera(self, points: np.ndarray) -> tuple[np.ndarray, np.ndarray[bool], np.ndarray[bool]]:
        assert points.shape[0] == 3, f"Invalid shape: {points.shape}"  # noqa: S101

        ext_mat = self.get_extrinsic_matrix()
        image_size = self.get_image_size()
        cx, cy = self.__intrinsic_parameters.principal_point
        affine_c, affine_d, affine_e = self.__intrinsic_parameters.affine_params_cde
        fov = self.__intrinsic_parameters.fov

        # Transform to camera coordinate
        points = np.vstack([points, np.ones(points.shape[1])])
        points_in_camera = ext_mat @ points

        # points_2d repesensts the points in image coordinate
        points_2d = np.zeros((2, points_in_camera.shape[1]))
        points_2d = np.vstack([points_2d, np.ones(points_2d.shape[1])])

        norm = np.sqrt(np.sum(points_in_camera[:2] ** 2, axis=0))
        valid_flag = norm != 0

        # Optical center
        points_2d[0][~valid_flag] = cx
        points_2d[1][~valid_flag] = cy

        # Points on (0, 0, 0)
        zero_flag = (points_in_camera == 0).all(axis=0)
        points_2d[0][zero_flag] = 0
        points_2d[1][zero_flag] = 0

        # Else
        # Mappings of the points in camera coordinate to the points in image coordinate
        #   can be represented by distance of a point from the optical center.
        # The mapping is represented by a polynomial function.
        theta = -np.arctan(points_in_camera[2][valid_flag] / norm[valid_flag])
        inv_norm = 1 / norm[valid_flag]
        for i, elem in enumerate(self.__intrinsic_parameters.world_to_cam_params):
            if i == 0:
                rho = np.full_like(theta, elem)
                tmp_theta = theta.copy()
            else:
                rho += elem * tmp_theta
                tmp_theta *= theta

        u = points_in_camera[0][valid_flag] * inv_norm * rho
        v = points_in_camera[1][valid_flag] * inv_norm * rho

        # Consider misalignments errors and digitizing artefacts
        points_2d_valid_0 = v * affine_e + u + cx
        points_2d_valid_1 = v * affine_c + u * affine_d + cy

        # Filter visible points by a field of view (fov)
        if fov < 360:
            thres_theta = np.deg2rad(fov / 2) - np.pi / 2
            outside_lag = theta > thres_theta
            points_2d_valid_0[outside_lag] = 0
            points_2d_valid_1[outside_lag] = 0

        points_2d[0][valid_flag] = points_2d_valid_0
        points_2d[1][valid_flag] = points_2d_valid_1

        points_in_image, mask_inside_image = filter_visible_points(points_2d, image_size[0], image_size[1])
        mask_in_front_of_camera = points_2d[2] > 0
        return points_in_image, mask_in_front_of_camera, mask_inside_image
