from build123d import *
from realkey.Common import geom_tools


def get_filtered(svg: ShapeList[Wire | Face], label: str) -> Wire | Face:
    return svg.filter_by(lambda shape: shape.label == label)[0]


def get_starting_at_origin(svg: ShapeList[Wire | Face], label: str) -> Wire | Face:
    filtered = get_filtered(svg, label)
    filtered.position -= filtered.bounding_box().min
    return filtered


def get_centered_around_origin(svg: ShapeList[Wire | Face], label: str) -> Wire | Face:
    filtered = get_filtered(svg, label)
    filtered.position -= filtered.bounding_box().center()
    return filtered


def get_filtered_group(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    return svg.filter_by(lambda shape: shape.label == label)


def get_group_starting_at_origin(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    filtered = get_filtered_group(svg, label)
    g_min = geom_tools.min(filtered)
    for s in filtered:
        s.position -= g_min
    return filtered


def get_group_centered_around_origin(svg: ShapeList[Wire | Face], label: str) -> ShapeList[Wire | Face]:
    filtered = get_filtered_group(svg, label)
    g_center = geom_tools.center(filtered)
    for s in filtered:
        s.position -= g_center
    return filtered
