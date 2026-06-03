from build123d import *


def min(shapes: ShapeList) -> Vector:
    mx, my, mz = None, None, None
    for shape in shapes:
        m = shape.bounding_box().min
        if mx is None or m.X < mx:
            mx = m.X
        if my is None or m.Y < my:
            my = m.Y
        if mz is None or m.Z < mz:
            mz = m.Z
    if mx is None or my is None or mz is None:
        raise ValueError("Unable to find minimum of ShapeList")
    return Vector(mx, my, mz)


def center(shapes: ShapeList) -> Vector:
    cx, cy, cz = 0, 0, 0
    for shape in shapes:
        c = shape.bounding_box().center()
        cx += c.X
        cy += c.Y
        cz += c.Z
    cx /= len(shapes)
    cy /= len(shapes)
    cz /= len(shapes)
    return Vector(cx, cy, cz)


def max(shapes: ShapeList) -> Vector:
    mx, my, mz = None, None, None
    for shape in shapes:
        m = shape.bounding_box().max
        if mx is None or m.X > mx:
            mx = m.X
        if my is None or m.Y > my:
            my = m.Y
        if mz is None or m.Z > mz:
            mz = m.Z
    if mx is None or my is None or mz is None:
        raise ValueError("Unable to find maximum of ShapeList")
    return Vector(mx, my, mz)
