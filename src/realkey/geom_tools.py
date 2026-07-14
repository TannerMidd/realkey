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


def Tube(inner_radius: float, outer_radius: float, length: float) -> Part:
    with BuildPart() as tube:
        with BuildSketch():
            Circle(radius=outer_radius)
            Circle(radius=inner_radius, mode=Mode.SUBTRACT)
        extrude(amount=length/2, both=True)
    if tube.part is None:
        raise ValueError("Unable to generate Tube")
    return tube.part

def generate_lifting_cut(face: Face, direction: VectorLike, lift_direction:VectorLike, length: float, lift_amount: float) -> Part:


    total_displacement = Vector(direction).normalized() * length
    total_lift = Vector(lift_direction).normalized() * lift_amount

    #face.position = source
    #face.orientation = Vector(direction).normalized()

    with BuildPart() as lifting_cut:
        with BuildLine() as cut_line:
            Line((0,0,0), total_displacement + total_lift)
        sweep(face, cut_line.line)

    if lifting_cut.part is None:
        raise ValueError("Unable to generate lifting cut")
    return lifting_cut.part
