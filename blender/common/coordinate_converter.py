import math
from typing import Tuple

from mathutils import Euler, Vector


def pos_to_blender(pos) -> Vector:
    return pos_scale_to_blender((pos[0], pos[2], -pos[1]))


def pos_scale_to_blender(pos: Tuple[float, float, float]) -> Vector:
    # From centimeter to meter
    return Vector(pos) * 0.01


def rot_to_blender(rot):
    return Euler(tuple(map(lambda x: -math.radians(x), rot)))


def pos_from_blender(pos: Vector) -> Tuple[float, float, float]:
    pos = pos_scale_to_blender(pos)
    return (pos.x, -pos.z, pos.y)


def pos_scale_from_blender(pos: Vector) -> Tuple[float, float, float]:
    # From meter to centimeter
    return (pos * 100).xyz


def rot_from_blender(rot: Euler) -> Tuple[float, float, float]:
    return (-math.degrees(rot.x), -math.degrees(rot.y), -math.degrees(rot.z))
