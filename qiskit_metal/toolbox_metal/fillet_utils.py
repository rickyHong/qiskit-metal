from typing import Tuple
import numpy as np
from ..draw.utility import Vec3D


def line_width_offset_pts(pt_vec: np.ndarray, path_vec: np.ndarray,
                          width: float) -> list:
    """Create offset points for straight line

    Args:
        pt_vec (np.ndarray): vectors of points within the line
        path_vec (np.ndarray): vectors along linestring path
        width (float): width for offset
        chip_z (float): z-coordinate of chip
        ret_pts (bool, optional): Return Gmsh points if True
                        else return np.ndarray. Defaults to True.

    Returns:
        list: list of Gmsh points or vec3D objs
    """
    path_angle = Vec3D.angle_azimuth(path_vec)
    perp_angle = path_angle + np.pi / 2
    cos_t = np.round(np.cos(perp_angle), decimals=9)
    sin_t = np.round(np.sin(perp_angle), decimals=9)
    r = width / 2

    offset_vec = np.array([r * cos_t, r * sin_t, 0])
    v1 = Vec3D.add(pt_vec, offset_vec)
    v2 = Vec3D.sub(pt_vec, offset_vec)

    return [v1, v2]


def arc_width_offset_pts(vec1: np.ndarray, vec3: np.ndarray, angle: float,
                         width: float) -> list:
    """Create offset points for Circle Arcs

    Args:
        vec1 (np.ndarray): incoming vector to arc
        vec3 (np.ndarray): outgoing vector from arc
        angle (float): angle of arc
        width (float): width for offset
        chip_z (float): z-coordinate of chip

    Returns:
        list: list of Gmsh points
    """
    perp_angle = np.pi / 2 - angle  # π - (angle + π/2)
    cos_t = np.round(np.cos(perp_angle), decimals=9)
    sin_t = np.round(np.sin(perp_angle), decimals=9)
    r = width / 2

    offset1 = np.array([0, r, 0])
    v1 = Vec3D.add(vec1, offset1)
    v2 = Vec3D.sub(vec1, offset1)

    sign = 1 if angle == np.pi / 2 else -1
    offset2 = np.array([r * cos_t * sign, r * sin_t * sign, 0])

    v3 = Vec3D.add(vec3, offset2)
    v4 = Vec3D.sub(vec3, offset2)

    return [v1, v2, v3, v4]


def make_arc_vecs(angle: float,
                  fillet: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create vectors for the circle arc.
    Disclaimer: The arc is drawn at the origin, and then has to be
    translated, rotated or mirrored using `transform_arc_points()`

    Args:
        angle (float): angle of arc
        fillet (float): fillet radius

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: vectors defining the arc control points
    """
    sector_angle = np.pi - angle
    intercept = np.abs(fillet * np.tan(sector_angle / 2))
    cos_t = np.round(np.cos(sector_angle), decimals=9)
    sin_t = np.round(np.sin(sector_angle), decimals=9)

    p1x = np.round(-intercept, decimals=9)
    p1y = 0
    p2x = np.round(p1x, decimals=9)
    p2y = np.round(p1y + fillet, decimals=9)
    p3x = np.round(intercept * cos_t, decimals=9)
    p3y = np.round(intercept * sin_t, decimals=9)

    v1 = np.array([p1x, p1y, 0])
    v2 = np.array([p2x, p2y, 0])
    v3 = np.array([p3x, p3y, 0])

    return v1, v2, v3


def transform_arc_points(vecs: np.ndarray, translate: np.ndarray,
                         path_vecs: list, chip_z: float) -> list:
    """Apply transformation to arc points

    Args:
        pts (list): list of Gmsh points
        translate (np.ndarray): translation vector (only a 2D vector)
        path_vecs (list): vectors along the linestring path
        chip_z (float): z-coordinate of chip

    Returns:
        list: list of transformed vectors
    """

    angle1 = Vec3D.angle_azimuth(path_vecs[0])
    cross_vec = Vec3D.cross(path_vecs[0], path_vecs[1])
    mirror = True if np.sign(Vec3D.normed(cross_vec)[2]) < 0 else False

    if mirror:
        # Flip right turn start/end points
        p1 = vecs.pop(0)
        p4 = vecs.pop(2)
        vecs.insert(1, p1)
        vecs.append(p4)
        vecs = Vec3D.mirror(vecs, [0, 1, 0, 0])

    new_vecs = []
    for vec in vecs:
        vec = Vec3D.rotate(vec, [0, 0, 0], az=True, radians=angle1)
        vec = Vec3D.translate(vec, translate)
        new_vecs.append(vec)

    return new_vecs