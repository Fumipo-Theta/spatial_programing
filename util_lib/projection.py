from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import open3d as o3d

if TYPE_CHECKING:
    from util_lib.types import ICamera


def projection_by_camera(
    pcd: o3d.geometry.PointCloud,
    camera: ICamera,
    *,
    return_with_color: bool = True,
    remove_hidden: bool = False,
) -> o3d.geometry.PointCloud:
    """
    ICamera の world_to_camera メソッドを使用して点群を投影するバージョン.

    Note:
    ----
    カメラモデルによってはカメラ座標から画像座標への変換が単純な行列の積で表せない場合がある。
    ICamera ではワールド座標から画像座標への一般化された変換を world_to_camera で定義する。

    """
    points = np.asarray(pcd.points).T
    projected_points, filter_points_func = camera.world_to_camera(points, remove_hidden=remove_hidden)

    projected_pcd = o3d.geometry.PointCloud()
    projected_pcd.points = o3d.utility.Vector3dVector(projected_points.T)
    if return_with_color:
        projected_pcd.colors = o3d.utility.Vector3dVector(
            filter_points_func(np.asarray(pcd.colors)),
        )
    return projected_pcd
