from build123d import *

from realkey.Common import key, key_cutters, svgtools


class SystemD(key.Key):
    SD_X_DATUM = 28 * MM
    SD_Y_DATUM = 9.25 * MM
    SD_BOW_WIDTH = 3 * MM

    SD_KEY_WIDTH = 6.45 * MM
    SD_KEY_HEIGHT = 7.125 * MM

    SD_Y_CUT_DATUM = SD_Y_DATUM + SD_KEY_HEIGHT

    SD_CUT_SPACE = 4.0 * MM
    SD_R_CUT_SPACINGS = [7.25 * MM + i * 4 * MM for i in range(5)]
    SD_L_CUT_SPACINGS = [5.0 * MM + i * 4 * MM for i in range(5)]
    SD_CUT_WIDTH = 1 * MM
    SD_CUT_ANGLE = 90

    SD_CUT_DEPTHS = [0.375 * MM, 0.875 * MM, 1.5 * MM, 1.875 * MM, 2.25 * MM]

    @classmethod
    def name(cls) -> str:
        return "dom_system_d"

    @classmethod
    def display_name(cls) -> str:
        return "DOM System D"

    @classmethod
    def profiles(cls) -> dict[str, str]:
        return {"basic": "Basic"}

    @classmethod
    def keyways(cls) -> dict[str, str]:
        return {"1": "1"}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return "Cuts: Up to 10, defined from bow to tip, right side before left side.<br>Depths: Maximum Lift 1 to Minimum Lift 5<br>Example: <i>5233342424</i>"

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")
        if len(bitting) > 10:
            raise ValueError("Only up to 10 cuts are allowed")
        if len(bitting) % 2 != 0:
            raise ValueError("Number of cuts must be even")

        for cut in bitting:
            if int(cut) < 1 or int(cut) > 5:
                raise ValueError("Cut depths must be from 1 to 5")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if profile not in cls.profiles():
            raise ValueError("Invalid profile specified!")
        if keyway not in cls.keyways():
            raise ValueError("Invalid keyway specified!")

        dom_svg = import_svg("resources/DOM/SystemD.svg", label_by="inkscape:label")
        blank_profile = svgtools.get_starting_at_origin(dom_svg, "#profile")
        blade_profile, bow_profile = split(blank_profile, bisect_by=Plane.YZ.offset(cls.SD_X_DATUM), keep=Keep.BOTH)
        bow_inset_profile = svgtools.get_starting_at_origin(dom_svg, "#inset_bow")
        keyway_face = svgtools.get_centered_around_origin(dom_svg, "#keyway")
        dom_logo = svgtools.get_group_centered_around_origin(dom_svg, "#dom_logo")
        for i, shape in enumerate(dom_logo):
            dom_logo[i] = shape.rotate(Axis.Z, 90)

        system_text = Text("System", 2.75, "Libre Baskerville", font_style=FontStyle.BOLD)
        system_text = system_text.rotate(Axis.Z, 90)
        d_text = Text("D", 2.75, "Libre Baskerville", font_style=FontStyle.BOLD)
        d_text = d_text.rotate(Axis.Z, 90)

        if not isinstance(bow_profile, Face):
            raise ValueError("Bow sucks")
        if not isinstance(blade_profile, Face):
            raise ValueError("Blade sucks")

        with BuildPart() as blank:
            with BuildSketch():
                add(bow_profile)
            extrude(amount=cls.SD_BOW_WIDTH)
            with BuildSketch():
                with Locations((0.4 * MM, 0.4 * MM)):
                    add(bow_inset_profile)
            extrude(amount=0.2 * MM, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(cls.SD_BOW_WIDTH)):
                with Locations((0.4 * MM, 0.4 * MM)):
                    add(bow_inset_profile)
            extrude(amount=-0.2 * MM, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(cls.SD_BOW_WIDTH - 0.2 * MM)):
                with Locations((13 * MM, 14.5 * MM)):
                    add(dom_logo)
                with Locations((8.75 * MM, 7.5 * MM)):
                    add(system_text)
                with Locations((15 * MM, 22 * MM)):
                    Circle(1.6 * MM)
                    Circle(1.4 * MM, mode=Mode.SUBTRACT)
                    with Locations((0.25 * MM, 0.125 * MM)):
                        add(d_text)

            extrude(amount=0.2 * MM)
            with BuildSketch() as bp:
                add(blade_profile)
            extrude(amount=cls.SD_KEY_WIDTH / 2 + cls.SD_BOW_WIDTH / 2)
            extrude(bp.sketch, amount=cls.SD_BOW_WIDTH / 2 - cls.SD_KEY_WIDTH / 2)
            with BuildSketch(Plane.ZY.offset(-cls.SD_X_DATUM)) as key_cutter:
                with Locations((cls.SD_BOW_WIDTH / 2, cls.SD_Y_DATUM + cls.SD_KEY_HEIGHT / 2)):
                    Rectangle(cls.SD_KEY_WIDTH, cls.SD_KEY_HEIGHT * 2)
                    add(keyway_face, mode=Mode.SUBTRACT)
            extrude(amount=-50 * MM, mode=Mode.SUBTRACT)

            new_faces = blank.faces().filter_by(Plane.YZ)
            extrude(new_faces.faces()[0], amount=8 * MM, dir=(-0.6, 0, 0.2))
            extrude(new_faces.faces()[0], amount=4 * MM, dir=(-0.6, 0, 0.6))
            extrude(new_faces.faces()[0], amount=2 * MM, dir=(-0.6, 0, 0.9))
            extrude(new_faces.faces()[4], amount=8 * MM, dir=(-0.6, 0, -0.2))
            extrude(new_faces.faces()[4], amount=4 * MM, dir=(-0.6, 0, -0.6))
            extrude(new_faces.faces()[4], amount=2 * MM, dir=(-0.6, 0, -0.9))

        if blank.part is None:
            raise ValueError("Unable to build blank")

        return blank.part

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        blank = cls.blank(profile, keyway)

        right_cuts = bitting[: int(len(bitting) / 2)]
        left_cuts = bitting[int(len(bitting) / 2) :]

        center_line = cls.SD_BOW_WIDTH / 2

        def calculate_cuts(cuts: str, spacings: list[float]) -> list[tuple[float, float]]:
            final_cuts: list[tuple[float, float]] = []
            for i, cut in enumerate(cuts):
                depth_index = int(cut) - 1

                cut_x = cls.SD_X_DATUM + spacings[i]
                cut_y = cls.SD_Y_CUT_DATUM - cls.SD_CUT_DEPTHS[depth_index]
                final_cuts.append((cut_x, cut_y))
            while len(final_cuts) < 6:
                lc = final_cuts[-1]
                nx = lc[0] + cls.SD_CUT_SPACE
                final_cuts.append((nx, lc[1]))

            final_cuts.append(final_cuts[-1])
            return final_cuts

        r_cuts = calculate_cuts(right_cuts, cls.SD_R_CUT_SPACINGS)
        l_cuts = calculate_cuts(left_cuts, cls.SD_L_CUT_SPACINGS)

        r_cutter = key_cutters.smooth_angled_cutter(r_cuts, cls.SD_CUT_WIDTH, cls.SD_Y_CUT_DATUM + 0.001 * MM, cls.SD_CUT_ANGLE)
        l_cutter = key_cutters.smooth_angled_cutter(l_cuts, cls.SD_CUT_WIDTH, cls.SD_Y_CUT_DATUM + 0.001 * MM, cls.SD_CUT_ANGLE)

        with BuildPart() as key:
            add(blank)

            with BuildSketch(Plane.XY.offset(center_line)):
                add(r_cutter)
            extrude(amount=10 * MM, mode=Mode.SUBTRACT)
            with BuildSketch(Plane.XY.offset(center_line)) as cl:
                add(l_cutter)
            extrude(amount=-10 * MM, mode=Mode.SUBTRACT)
        if key.part is None:
            raise ValueError("Unable to generate key")

        return key.part


if __name__ == "__main__":
    from ocp_vscode import *

    # blank = SystemD.blank("basic", "1")
    # export_step(blank, "dom_system_d.step")
    key = SystemD.key("basic", "1", "5233342424")
    # export_step(key, "dom_system_d.step")
    show_all()
