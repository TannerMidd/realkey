from math import atan2, sqrt, pi

from build123d import *

from realkey.Common import key, resource_fetcher, svgtools


class Memolis(key.Key):
    MEMOLIS_KEY_WIDTH = 3.25 * MM
    MEMOLIS_KEY_HEIGHT = 8.5 * MM
    MEMOLIS_KEY_X_DATUM = 31 * MM
    MEMOLIS_KEY_Y_DATUM = 6.25 * MM

    MEMOLIS_R_CUT_SPACINGS = [i * 3.75 * MM + 7 * MM for i in range(7)]  # Right of keyway, with the arrow being at the top
    MEMOLIS_L_CUT_SPACINGS = [i * 3.75 * MM + 8.875 * MM for i in range(7)]
    MEMOLIS_CUT_DEPTHS = [i * 0.35 * MM for i in range(6)]

    MEMOLIS_MAX_DEPTH = MEMOLIS_CUT_DEPTHS[-1]
    MEMOLIS_CUT_SURFACE_WIDTH = 1 * MM

    @classmethod
    def name(cls) -> str:
        return "opnus_memolis"

    @classmethod
    def display_name(cls) -> str:
        return "Opnus Memolis"

    @classmethod
    def profiles(cls) -> dict[str, str]:
        return {"memolis": "Operator Key", "memolis_change": "Change Key"}

    @classmethod
    def keyways(cls) -> dict[str, str]:
        return {"memolis": "Memolis"}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "There are 14 cuts from bow to tip, with maximum lift as 0 and minimum lift as 5.<br>"
            "The right side is defined as the right side of the key when the bow is held with the tip facing away. "
            "All right cuts come before all left cuts.<br>"
            "Cuts 1 and 14 are always fixed for a given lock, but the rest can be changed with the appropriate change key and new key.<br>"
            "On Memolis 2, a key cut of 0 will disable that lever.<br><br>"
            "<i>E.g. 40503325050251 will generate a key with 4050332 as right cuts, 5050251 as left cuts.</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

        if len(bitting) > 14:
            raise ValueError("Maximum supported cuts for Memolis is 14")

        for cut in bitting:
            if int(cut) < 0 or int(cut) > 5:
                raise ValueError("Cut depths must be from 0 to 5")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if profile not in cls.profiles():
            raise ValueError("Invalid profile specified!")
        if keyway not in cls.keyways():
            raise ValueError("Invalid keyway specified!")
        
        if not resource_fetcher.pre_fetch_resource("resources/Opnus/Memolis.svg"):
            raise ValueError("Unable to load Opnus Memolis SVG")

        opnus_svg = import_svg("resources/Opnus/Memolis.svg", flip_y=False, label_by="inkscape:label")
        profile_face = svgtools.get_starting_at_origin(opnus_svg, "#profile_" + profile)
        keyway_face = svgtools.get_centered_around_origin(opnus_svg, "#keyway_" + keyway)
        keyway_face = keyway_face.mirror(Plane.XZ)

        with BuildPart() as memolis_blank:
            with BuildSketch():
                add(profile_face)
            extrude(amount=cls.MEMOLIS_KEY_WIDTH)

            with BuildSketch(Plane.YZ.offset(cls.MEMOLIS_KEY_X_DATUM)) as keyway_cutter:
                with Locations((cls.MEMOLIS_KEY_Y_DATUM + cls.MEMOLIS_KEY_HEIGHT / 2, cls.MEMOLIS_KEY_WIDTH / 2)):
                    Rectangle(cls.MEMOLIS_KEY_HEIGHT, cls.MEMOLIS_KEY_WIDTH)
                    add(keyway_face, mode=Mode.SUBTRACT)
            extrude(amount=100 * MM, mode=Mode.SUBTRACT)

            chamfer(memolis_blank.edges().filter_by_position(Axis.X, 63.5, 65), 0.5 * MM)

            # secondary chamfer
            tip_edges = memolis_blank.edges().filter_by_position(Axis.X, 62, 65).filter_by(Plane.XY).group_by(Axis.Z)
            secondary_edges = tip_edges[1] + tip_edges[2]
            chamfer(secondary_edges, 0.25 * MM)

            # key bitting surface chamfer
            right_edges = memolis_blank.edges().filter_by_position(Axis.Y, cls.MEMOLIS_KEY_Y_DATUM - 0.1, cls.MEMOLIS_KEY_Y_DATUM + 0.1).filter_by(Plane.XZ).group_by(Axis.Z)
            left_edges = (
                memolis_blank.edges()
                .filter_by_position(Axis.Y, cls.MEMOLIS_KEY_Y_DATUM + cls.MEMOLIS_KEY_HEIGHT - 0.1, cls.MEMOLIS_KEY_Y_DATUM + cls.MEMOLIS_KEY_HEIGHT + 0.1)
                .filter_by(Plane.XZ)
                .group_by(Axis.Z)
            )
            bitting_edges = right_edges[0] + right_edges[-1] + left_edges[0] + left_edges[-1]

            chamfer(bitting_edges, cls.MEMOLIS_CUT_SURFACE_WIDTH / sqrt(2))
        return Part(memolis_blank.part)

    @classmethod
    def key_cutter(cls):
        base = RectangleRounded(1.5 * MM, 1.25 * MM, 0.624 * MM)
        base = extrude(base, cls.MEMOLIS_MAX_DEPTH)

        trapezoid_angle = 180 / pi * atan2(2 * cls.MEMOLIS_MAX_DEPTH, 5.5 * MM)
        side = Trapezoid(6.5 * MM, cls.MEMOLIS_MAX_DEPTH, trapezoid_angle, align=Align.MIN)
        side = Pos(3.25 * MM, 0.5 * MM, cls.MEMOLIS_MAX_DEPTH) * Rotation(90, 0, 180) * side
        side = extrude(Sketch(side), cls.MEMOLIS_CUT_SURFACE_WIDTH)
        side_bottom = side.faces().filter_by_position(Axis.Z, -1, 0.1)[0]
        top = Pos(0, 0, cls.MEMOLIS_MAX_DEPTH) * make_hull(Rectangle(6.5 * MM, cls.MEMOLIS_CUT_SURFACE_WIDTH).edges() + Rectangle(cls.MEMOLIS_CUT_SURFACE_WIDTH, 2.5 * MM).edges())
        top_extra = extrude(Sketch(top), 10 * MM)

        cutter = loft(side_bottom + top)
        cutter += base
        cutter += top_extra
        return cutter

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        def cutter_for_side(cuts: str, is_right_side: bool):
            cutter = Part()
            mirror_plane_1 = Plane.XZ.offset(-cls.MEMOLIS_KEY_Y_DATUM - cls.MEMOLIS_KEY_HEIGHT / 2)
            mirror_plane_2 = Plane.XY.offset(cls.MEMOLIS_KEY_WIDTH / 2)
            for i, cut in enumerate(cuts):
                depth_index = int(cut)

                cut_x = cls.MEMOLIS_R_CUT_SPACINGS[i] if is_right_side else cls.MEMOLIS_L_CUT_SPACINGS[i]
                cut_x += cls.MEMOLIS_KEY_X_DATUM
                cut_depth = cls.MEMOLIS_CUT_DEPTHS[depth_index]
                rotation = 45 if is_right_side else -45

                cut_y = cls.MEMOLIS_KEY_Y_DATUM
                if not is_right_side:
                    cut_y += cls.MEMOLIS_KEY_HEIGHT

                cutter_tool = cls.key_cutter()
                if cutter_tool == None:
                    return Part()
                cutter_tool = Pos(0, 0, -cut_depth - cls.MEMOLIS_CUT_SURFACE_WIDTH / 2) * cutter_tool
                cutter_tool = Location((cut_x, cut_y, cls.MEMOLIS_KEY_WIDTH), (rotation, 0, 0)) * cutter_tool
                cutter += cutter_tool

                cutter_tool2 = mirror(Part() + cutter_tool, mirror_plane_1)
                cutter_tool2 = mirror(cutter_tool2, mirror_plane_2)
                cutter += cutter_tool2
            return cutter

        right_cuts = bitting[: int(len(bitting) / 2)]
        left_cuts = bitting[int(len(bitting) / 2) :]

        key = cls.blank(profile, keyway)
        cutter_right = cutter_for_side(right_cuts, True)
        cutter_left = cutter_for_side(left_cuts, False)

        return Part(key - (cutter_right + cutter_left))


if __name__ == "__main__":
    from ocp_vscode import *

    # blank = Memolis.blank("memolis_change", "memolis")
    key = Memolis.key("memolis", "memolis", "40503325050251")
    # export_step(key, "memolis_change_key.step")
    show_all()
