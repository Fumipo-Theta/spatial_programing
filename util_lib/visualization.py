from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import open3d as o3d

from .transformable_object import TransformableObject

if TYPE_CHECKING:
    from .types import ICamera


def draw_geometries(
    *geometries: o3d.geometry.Geometry | TransformableObject,
    camera: ICamera | None = None,
    title: str | None = None,
) -> None:
    """
    Open3D の visualization API のラッパー関数.

    Note:
    ----
    - オブジェクトを見やすいよう背景色を変更している

    """
    vis = o3d.visualization.Visualizer()

    if camera is not None:
        vis.create_window(
            window_name=title or "Open3D",
            width=camera.get_image_size()[0],
            height=camera.get_image_size()[1],
        )
    else:
        vis.create_window(window_name=title or "Open3D", width=1920, height=1080)
    render_option = vis.get_render_option()

    render_option.background_color = np.asarray([0, 0, 0.2])

    for geometry in geometries:
        if isinstance(geometry, TransformableObject):
            vis.add_geometry(geometry.get_geometry())
        elif isinstance(geometry, o3d.geometry.Geometry):
            vis.add_geometry(geometry)
        else:
            error_msg = f"Invalid type: {type(geometry)}"
            raise TypeError(error_msg)

    if camera is not None:
        view_control = vis.get_view_control()
        pinhole_parameters = view_control.convert_to_pinhole_camera_parameters()
        pinhole_parameters.intrinsic.intrinsic_matrix = camera.get_intrinsic_matrix()
        pinhole_parameters.extrinsic = camera.get_extrinsic_matrix()
        view_control.convert_from_pinhole_camera_parameters(pinhole_parameters, allow_arbitrary=True)

    while vis.poll_events():
        vis.update_renderer()

    vis.destroy_window()
