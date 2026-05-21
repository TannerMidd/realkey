from build123d import *
from copy import copy

def get_filtered(svg: ShapeList[Wire | Face], label: str) -> Wire | Face:
    return svg.filter_by(lambda shape: shape.label == label)[0]

def get_starting_at_origin(svg: ShapeList[Wire | Face], label: str) -> Wire | Face:
    filtered = get_filtered(svg, label)
    filtered.position -= filtered.bounding_box().min
    return filtered

def get_centered_around_origin(svg: ShapeList[Wire | Face], label: str) -> Wire |Face:
    filtered = get_filtered(svg, label)
    filtered.position -= filtered.bounding_box().center()
    return filtered

def get_filtered_group(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    return svg.filter_by(lambda shape: shape.label == label)

def _group_min(shapes: ShapeList[Wire | Face]):
    min_x = None
    min_y = None
    min_z = None

    for s in shapes:
        v = s.bounding_box().min
        if min_x is None or v.X < min_x:
            min_x = v.X
        if min_y is None or v.Y < min_y:
            min_y = v.Y
        if min_z is None or v.Z < min_z:
            min_z = v.Z

    if min_x is None or min_y is None or min_z is None:
        raise ValueError("Unable to find minimum of group")
    return Vector(min_x, min_y, min_z)

def _group_center(shapes: ShapeList[Wire | Face]):
    sum_x = 0
    sum_y = 0
    sum_z = 0

    for s in shapes:
        v = s.bounding_box().center()
        sum_x += v.X
        sum_y += v.Y
        sum_z += v.Z
    
    sum_x /= len(shapes)
    sum_y /= len(shapes)
    sum_z /= len(shapes)
    return Vector(sum_x, sum_y, sum_z)


def get_group_starting_at_origin(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    filtered = get_filtered_group(svg, label)
    g_min = _group_min(filtered)
    for s in filtered:
        s.position -= g_min
    return filtered

def get_group_centered_around_origin(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    filtered = get_filtered_group(svg, label)
    g_center = _group_center(filtered)
    for s in filtered:
        s.position -= g_center
    return filtered