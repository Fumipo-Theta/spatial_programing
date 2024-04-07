import sys
from pathlib import Path

import open3d as o3d
from scipy.spatial.transform import Rotation


def create_camera() -> o3d.geometry.TriangleMesh:
    """
    Create Triangle Mesh of Camera object.

    Coordinate:
      - In the world coordinate system
        - lense faces to +y direction
        - lense is placed on the origin

                  ----------------
                  |          [ ] |
                  |     (+y) ----|---> +x
                  |       |      |
                  ----------------
                          |
                         +z

      - Camera coordinate system
        - +x: right, +y: down, +z: forward like below

                  ----------------
                  |          [ ] |
          +x <----|---- (+z)     |
                  |       |      |
                  ----------------
                          |
                         +y
    """
    body = o3d.geometry.TriangleMesh.create_box(width=0.5, height=0.1, depth=0.3)
    body.paint_uniform_color([0.9, 0.9, 0.9])
    body.translate([-0.25, -0.05, -0.15])
    finder = o3d.geometry.TriangleMesh.create_box(width=0.07, height=0.01, depth=0.05)
    finder.paint_uniform_color([0.1, 0.1, 0.1])
    finder.translate([0.14, 0.05, -0.12])
    lense = o3d.geometry.TriangleMesh.create_cylinder(radius=0.1, height=0.07)
    lense.rotate(Rotation.from_euler("x", 90, degrees=True).as_matrix(), center=[0, 0, 0])
    lense.paint_uniform_color([0.6, 0.6, 1])
    lense.translate([0, 0.05, 0])

    camera_coord = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.3, origin=[0, 0, 0])
    camera_coord.rotate(Rotation.from_euler("x", -90, degrees=True).as_matrix(), center=[0, 0, 0])
    camera_coord.rotate(Rotation.from_euler("y", 180, degrees=True).as_matrix(), center=[0, 0, 0])
    camera_coord.translate([0, 0.1, 0])

    camera = o3d.geometry.TriangleMesh()
    camera += body
    camera += finder
    camera += lense
    camera += camera_coord

    center = camera.get_center()
    camera.translate([-center[0], -center[1], -center[2]])
    camera.compute_vertex_normals()
    return camera


def switch_format(raw_ext: str) -> str:
    match raw_ext.lower():
        case "obj":
            return "obj"
        case "ply":
            return "ply"
        case "stl":
            return "stl"
        case "gltf":
            return "gltf"
        case "glb":
            return "glb"
        case _:
            error_msg = f"Invalid extension: {raw_ext}"
            raise ValueError(error_msg)


if __name__ == "__main__":
    format = switch_format(sys.argv[1])
    file_path = Path(__file__).parent / f"../data/camera.{format}"
    camera = create_camera()
    assert o3d.io.write_triangle_mesh(str(file_path.resolve()), camera), f"Failed to write {file_path}"
