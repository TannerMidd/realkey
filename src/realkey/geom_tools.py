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
            my = m.Y1
        if mz is None or m.Z > mz:
            mz = m.Z
    if mx is None or my is None or mz is None:
        raise ValueError("Unable to find maximum of ShapeList")
    return Vector(mx, my, mz)


def Tube(inner_radius: float, outer_radius: float, length: float) -> Part:
    with BuildPart() as tube:
        with BuildSketch():
            Circle(radius=outer_radius)
            Circle(radius=inner_radius, mode=Mode.SUBTRACT)
        extrude(amount=length/2, both=True)
    if tube.part is None:
        raise ValueError("Unable to generate Tube")
    return tube.part
