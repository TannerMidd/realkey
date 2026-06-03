from build123d import *

from realkey import key, key_cutters, resource_fetcher, svgtools


class PR1(key.Key):
    PR1_KEY_WIDTH = 2 * MM
    PR1_KEY_HEIGHT = 1 * IN
    PR1_KEY_X_DATUM = 36 * MM
    PR1_KEY_Y_DATUM = 9 * MM
    PR1_KEY_CUT_SPACINGS = [i * 0.1375 * IN + 0.145 * IN for i in range(7)]
    PR1_KEY_CUT_DEPTHS = [i * IN for i in [0.2840, 0.2684, 0.2450, 0.2215, 0.1981, 0.1747]]
    PR1_KEY_CUT_WIDTH = 0.065 * IN

    @classmethod
    def name(cls) -> str:
        return "paclock_pr1"

    @classmethod
    def display_name(cls) -> str:
        return "Paclock PR1"

    @classmethod
    def profiles(cls) -> dict[str, str]:
        return {"pr1": "PR1 6-pin", "pro": "PRO 7-pin"}

    @classmethod
    def keyways(cls) -> dict[str, str]:
        return {"pr1": "PR1"}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return "Key cuts are defined from bow to tip with maximum lift as 1 and minimum lift as 6<br><br><i>E.g. 6212121 for a PRO profile.</i>"

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")
        if profile == "pr1" and len(bitting) > 6:
            raise ValueError("Maximum supported cuts for PR1 profile is 6")
        if profile == "pro" and len(bitting) > 7:
            raise ValueError("Maximum supported cuts for PRO profile is 7")

        for cut in bitting:
            if int(cut) < 1 or int(cut) > 6:
                raise ValueError("Cut depths must be from 1 to 6")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if profile not in cls.profiles():
            raise ValueError("Invalid profile specified!")
        if keyway not in cls.keyways():
            raise ValueError("Invalid keyway specified!")

        if not resource_fetcher.pre_fetch_resource("resources/Paclock/PR1.svg"):
            raise ValueError("Unable to load Paclock SVG")

        paclock_svg = import_svg("resources/Paclock/PR1.svg", flip_y=False, label_by="inkscape:label")

        blank_profile = svgtools.get_starting_at_origin(paclock_svg, "#profile_" + profile)
        blank = extrude(blank_profile, cls.PR1_KEY_WIDTH)

        keyway_shape = svgtools.get_centered_around_origin(paclock_svg, "#keyway_" + keyway)
        outside_vertices = keyway_shape.vertices().filter_by_position(Axis.X, -1.05, -0.95) + keyway_shape.vertices().filter_by_position(Axis.X, 0.95, 1.05)
        keyway_shape = fillet(outside_vertices, 0.2 * MM)
        keyway_shape = keyway_shape.rotate(Axis.Z, 180)

        keyway_cutter = Rectangle(2.2 * MM, 7.6 * MM)
        keyway_cutter -= keyway_shape

        keyway_cutter = Sketch(Location((cls.PR1_KEY_X_DATUM, cls.PR1_KEY_Y_DATUM + 7.5 / 2 * MM, cls.PR1_KEY_WIDTH / 2), (0, 90, 0)) * keyway_cutter)
        keyway_cutter = extrude(keyway_cutter, 30 * MM)

        blank -= keyway_cutter

        return Part(blank)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        pr1_blank = cls.blank(profile, keyway)

        cuts: list[tuple[float, float]] = []
        for i, cut in enumerate(bitting):
            depth_index = int(cut) - 1

            cut_x = cls.PR1_KEY_X_DATUM + cls.PR1_KEY_CUT_SPACINGS[i]
            cut_y = cls.PR1_KEY_Y_DATUM + cls.PR1_KEY_CUT_DEPTHS[depth_index]

            cuts.append((cut_x, cut_y))

        cutter = key_cutters.angled_cutter(cuts, cls.PR1_KEY_CUT_WIDTH, 16.6, 0.25 * IN, 90)

        with BuildPart() as pr1_key:
            add(pr1_blank)

            with BuildSketch() as pr1_cutter:
                add(cutter)
            extrude(amount=cls.PR1_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
        return Part(pr1_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    # blank = PR1.blank("pro", "pr1")
    # export_step(blank, "pr1_blank.step")
    key = PR1.key("pro", "pr1", "6262626")
    show_all()
