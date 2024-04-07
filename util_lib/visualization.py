from __future__ import annotations

import numpy as np
import open3d as o3d

from .transformable_object import TransformableObject


def draw_geometries(*geometries: o3d.geometry.Geometry | TransformableObject) -> None:
    vis = o3d.visualization.Visualizer()

    vis.create_window()
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

    while vis.poll_events():
        vis.update_renderer()

    vis.destroy_window()
