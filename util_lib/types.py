from enum import Enum


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
