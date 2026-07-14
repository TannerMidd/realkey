from build123d import *
import math


def angled_cutter(cuts: list[tuple[float, float]], cut_root_width: float, neutral_y: float, max_cutter_width: float, angle: float) -> Sketch:
    """Generates a generic angled cutter with a fixed angle and set root width. Undercut is allowed by this cutter.

    Args:
        cuts (list[tuple[float, float]]): A list of cut centers, specified as (x, y)
        cut_root_width (float): The width of the flat spot or root of the cut
        neutral_y (float): The default neutral position for ramp in and ramp out, typically the Y value of the top of the key with a little cushion to close the shape.
        max_cutter_width (float): A maximum width for the cutter, to make sure it doesnt extend too far outside the cutting region
        angle (float): The desired angle of all cuts, defined as the total angle of the cut, between two ramps
    """
    ha = angle / 2
    hw = cut_root_width / 2
    cs = math.tan(math.radians(ha))

    with BuildSketch() as cutter:
        for ci, (cx, cy) in enumerate(cuts):
            dy = cy - neutral_y
            dx = abs(dy / cs)
            if dx * 2 + cut_root_width > max_cutter_width:
                # cap dx, requiring extra points
                dx = (max_cutter_width - cut_root_width) / 2
                dy = abs(dx * cs)

                with BuildLine():
                    Polyline(
                        (cx - hw - dx, neutral_y),
                        (cx + hw + dx, neutral_y),
                        (cx + hw + dx, cy + dy),
                        (cx + hw, cy),
                        (cx - hw, cy),
                        (cx - hw - dx, cy + dy),
                        (cx - hw - dx, neutral_y),
                    )
                make_face()

            else:
                with BuildLine():
                    Polyline(
                        (cx - hw - dx, neutral_y),
                        (cx + hw + dx, neutral_y),
                        (cx + hw, cy),
                        (cx - hw, cy),
                        (cx - hw - dx, neutral_y),
                    )
                make_face()

    return cutter.sketch


def smooth_angled_cutter(cuts: list[tuple[float, float]], cut_root_width: float, neutral_y: float, angle: float) -> Sketch:
    """Generates a specialized cutter with a fixed angle. The angled cut is placed halfway between two adjacent cuts, and cut root width is enforced.

    Args:
        cuts (list[tuple[float, float]]): A list of cut centers, specified as (x, y)
        cut_root_width (float): The minimum width a cut should be, used to validate if the cuts are possible
        neutral_y (float): The default neutral position for ramp in and ramp out, typically the Y value of the top of the key with a little cushion to close the shape.
        angle (float): The desired angle of all cuts, defined as the total angle of the cut, between two ramps
    """
    if len(cuts) < 2:
        return angled_cutter(cuts, cut_root_width, neutral_y, cut_root_width*10, angle)

    ha = angle / 2
    hw = cut_root_width / 2
    cs = math.tan(math.radians(ha))

    def add_cut(cuts: list[tuple[float, float]], x: float, y: float, w: float, signum: float = 1.0):
        cuts.append((x - math.copysign(w, signum), y))
        cuts.append((x + math.copysign(w, signum), y))

    def add_neutral_cut(cuts: list[tuple[float, float]], x: float, y: float, w: float, signum: float = 1.0):
        hw = w / 2
        dy = y - neutral_y
        dx = abs(dy / cs)
        cuts.append((x + math.copysign(hw + dx, signum), neutral_y))

    cut_points: list[tuple[float, float]] = []
    signum = cuts[1][0] - cuts[0][0]  # Used to define the direction we are building in

    add_neutral_cut(cut_points, cuts[0][0], cuts[0][1], cut_root_width, -signum)

    # iterates (c0,c1),(c1,c2),(c2,c3), etc..
    for ci, ((c0x, c0y), (c1x, c1y)) in enumerate(zip(cuts[0:-1], cuts[1:])):
        # first make a segment for the c0 cut
        add_cut(cut_points, c0x, c0y, hw, signum)

        dy = c1y - c0y
        # we only make angled cuts if theres a change in height
        if dy != 0:
            sx = abs(c1x - c0x) - cut_root_width  # space available to cut the angle
            hs = abs(c1x - c0x) / 2  # length to midpoint between the cuts
            dx = abs(dy / cs)  # change in x needed to make the angled cut

            # if the available space is equal to the needed space, this is a MACS cut
            # and our normal cut adds will add the point
            if not math.isclose(dx, sx):
                if dx > sx:
                    raise ValueError(f"Angled cut impossible with available space. Cut #{ci}, Required={dx}, Available={sx}, c0=({c0x},{c0y}), c1=({c1x},{c1y})")

                c_0ax = c0x + math.copysign(hs - dx / 2, signum)
                c_1ax = c0x + math.copysign(hs + dx / 2, signum)

                cut_points.append((c_0ax, c0y))
                cut_points.append((c_1ax, c1y))

        # add segment for c1 cut
        add_cut(cut_points, c1x, c1y, hw, signum)

    # calculate trailing angled cut
    add_neutral_cut(cut_points, cuts[-1][0], cuts[-1][1], cut_root_width, signum)
    cut_points.append(cut_points[0])

    with BuildSketch() as cutter:
        with BuildLine():
            Polyline(cut_points)
        make_face()
    return cutter.sketch


def lever_cutter(cuts: list[tuple[float, float, float]], neutral_y: float) -> Sketch:
    """Generates a rectangular shaped cutter for use with lever lock keys.

    Args:
        cuts (list[tuple[float, float, float]]): A list of cut centers with cut width, specified as (x,y,width)
        neutral_y (float): The default neutral position for the top of the cutter, typically the Y value of the top of the key with a little cushion to close the shape.
    """

    with BuildSketch() as cutter:
        for cx, cy, cw in cuts:
            yh = abs(neutral_y - cy)
            yc = neutral_y - (neutral_y - cy) / 2

            with Locations((cx, yc)):
                Rectangle(cw, yh)

    return cutter.sketch
