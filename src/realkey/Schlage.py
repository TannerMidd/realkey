from build123d import *

from realkey import key, key_cutters, resource_fetcher, svgtools

SCHLAGE_ROOT_DEPTHS = [0.335 * IN - i * 0.015 * IN for i in range(10)]
SCHLAGE_CUT_SPACINGS = [0.231 * IN + 0.1562 * IN * i for i in range(6)]
SCHLAGE_CUT_ANGLE = 100
SCHLAGE_CUT_WIDTH = 0.031 * IN


class EverestBlank:
    EVEREST_KEY_WIDTH = 2.75 * MM
    EVEREST_KEY_BLADE_HEIGHT = 0.343 * IN

    EVEREST_X_DATUM = 31.400 * MM
    EVEREST_Y_DATUM = 10.725 * MM
    EVEREST_SIDEBAR_Y_DATUM = 19.437 * MM
    EVEREST_SIDEBAR_WIDTH = 1.2 * MM

    EVEREST_CUT_DEPTHS = [0.343 * IN - i for i in SCHLAGE_ROOT_DEPTHS]

    EVEREST_PRIMUS_SIDEBAR_SPACINGS = [(a + b) / 2 for a, b in zip(SCHLAGE_CUT_SPACINGS[0:-1], SCHLAGE_CUT_SPACINGS[1:])]
    EVEREST_PRIMUS_SIDEBAR_OFFSET = 0.032 * IN

    EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS = [0.036 * IN, 0.060 * IN]
    EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS = [0.024 * IN + i * 0.024 * IN for i in range(3)]

    EVEREST_PRIMUS_SIDEBAR_CUT_DATA = [
        [-EVEREST_PRIMUS_SIDEBAR_OFFSET, EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS[1]],
        [-EVEREST_PRIMUS_SIDEBAR_OFFSET, EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS[0]],
        [0, EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS[1]],
        [0, EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS[0]],
        [EVEREST_PRIMUS_SIDEBAR_OFFSET, EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS[1]],
        [EVEREST_PRIMUS_SIDEBAR_OFFSET, EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS[0]],
        [EVEREST_PRIMUS_SIDEBAR_OFFSET, EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS[2]],
    ]

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest": {"e_6pin": "6-Pin", "e_ctrl": "Control"},
            "Everest Primus": {"ep_6pin": "6-Pin", "ep_ctrl": "Control"},
            "Everest 29": {"e29_6pin": "6-Pin", "e29_ctrl": "Control"},
            "Everest 29 Primus": {"e29p_6pin": "6-Pin", "e29p_ctrl": "Control"},
        }

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest": {
                "c000": "C000",
                "c100": "C100",
                "c200": "C200",
                "c150": "C150",
                "c120": "C120",
                "c230": "C230",
                "c134": "C134",
                "c145": "C145",
                "c135": "C135",
                "c125": "C125",
                "c124": "C124",
                "c123": "C123",
                "c234": "C234",
                "c235": "C235",
                "c245": "C245",
                "c345": "C345",
            },
            "Everest 29": {
                "s000": "S000",
                "s100": "S100",
                "s200": "S200",
                "s150": "S150",
                "s120": "S120",
                "s230": "S230",
                "s134": "S134",
                "s145": "S145",
                "s135": "S135",
                "s125": "S125",
                "s124": "S124",
                "s123": "S123",
                "s234": "S234",
                "s235": "S235",
                "s245": "S245",
                "s345": "S345",
            },
        }

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if not resource_fetcher.pre_fetch_resource("resources/Schlage/Everest.svg"):
            raise ValueError("Unable to load Schlage Everest SVG")

        paclock_svg = import_svg("resources/Schlage/Everest.svg", flip_y=False, label_by="inkscape:label")

        lookup_profile = ""
        if profile in ["e_6pin", "ep_6pin"]:
            lookup_profile = "e_6pin"
        if profile in ["e_ctrl", "ep_ctrl"]:
            lookup_profile = "e_ctrl"
        if profile in ["e29_6pin", "e29p_6pin"]:
            lookup_profile = "e29_6pin"
        if profile in ["e29_ctrl", "e29p_ctrl"]:
            lookup_profile = "e29_ctrl"

        blank_profile = svgtools.get_starting_at_origin(paclock_svg, "#profile_" + lookup_profile)
        blank = extrude(blank_profile, cls.EVEREST_KEY_WIDTH)

        keyway_shape = svgtools.get_centered_around_origin(paclock_svg, "#keyway_" + keyway)
        keyway_cutter = Rectangle(cls.EVEREST_KEY_WIDTH, cls.EVEREST_KEY_BLADE_HEIGHT + 0.025)
        keyway_cutter -= keyway_shape

        keyway_cutter = Sketch(Location((cls.EVEREST_X_DATUM, cls.EVEREST_Y_DATUM + cls.EVEREST_KEY_BLADE_HEIGHT / 2, cls.EVEREST_KEY_WIDTH / 2), (0, 90, 0)) * keyway_cutter)
        keyway_cutter = extrude(keyway_cutter, 40 * MM)
        blank -= keyway_cutter

        with BuildPart() as sidebar_ramp:
            with BuildSketch():
                with BuildLine():
                    Polyline((59.950, 19.275), (63.14, 16), (56.76, 16), (59.950, 19.275))
                make_face()
            extrude(amount=cls.EVEREST_SIDEBAR_WIDTH - 0.001)
        blank -= sidebar_ramp.part

        if profile in ["e_6pin", "e_ctrl", "e29_6pin", "e29_ctrl"]:
            with BuildPart() as everest_cutout:
                with BuildSketch():
                    with BuildLine():
                        Polyline(
                            (cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[2], cls.EVEREST_SIDEBAR_Y_DATUM - cls.EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS[0]),
                            (cls.EVEREST_X_DATUM + cls.EVEREST_PRIMUS_SIDEBAR_SPACINGS[3], cls.EVEREST_SIDEBAR_Y_DATUM - cls.EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS[0]),
                            (cls.EVEREST_X_DATUM + cls.EVEREST_PRIMUS_SIDEBAR_SPACINGS[4], 16),
                            (cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[1], 16),
                            (cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[2], cls.EVEREST_SIDEBAR_Y_DATUM - cls.EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS[0]),
                        )
                    make_face()
                extrude(amount=cls.EVEREST_SIDEBAR_WIDTH - 0.001)
            blank -= everest_cutout.part

        return Part(blank)


class Everest(key.Key, EverestBlank):
    @classmethod
    def name(cls) -> str:
        return "schlage_everest"

    @classmethod
    def display_name(cls) -> str:
        return "Schlage Everest"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest": {"e_6pin": "6-Pin", "e_ctrl": "Control"},
            "Everest 29": {"e29_6pin": "29 6-Pin", "e29_ctrl": "29 Control"},
        }

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest": {
                "c000": "C000",
                "c100": "C100",
                "c200": "C200",
                "c150": "C150",
                "c120": "C120",
                "c230": "C230",
                "c134": "C134",
                "c145": "C145",
                "c135": "C135",
                "c125": "C125",
                "c124": "C124",
                "c123": "C123",
                "c234": "C234",
                "c235": "C235",
                "c245": "C245",
                "c345": "C345",
            },
            "Everest 29": {
                "s000": "S000",
                "s100": "S100",
                "s200": "S200",
                "s150": "S150",
                "s120": "S120",
                "s230": "S230",
                "s134": "S134",
                "s145": "S145",
                "s135": "S135",
                "s125": "S125",
                "s124": "S124",
                "s123": "S123",
                "s234": "S234",
                "s235": "S235",
                "s245": "S245",
                "s345": "S345",
            },
        }

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 6, defined from bow to tip.<br>"
            "<b>Depths:</b> Maximum Lift 0 to Minimum Lift 9<br>"
            "<b>Example:</b> <i>326163</i><br>"
            "<i>Make sure warding channels are clean after printing or key will be difficult to use!</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

        if len(bitting) > 6:
            raise ValueError("Only up to 6 cuts are allowed")

        for cut in bitting:
            if int(cut) < 0 or int(cut) > 9:
                raise ValueError("Cut depths must be from 0 to 9")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        return EverestBlank.blank(profile, keyway)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        everest_blank = cls.blank(profile, keyway)

        cut_points: list[tuple[float, float]] = []

        for i, cut in enumerate(bitting):
            depth_index = int(cut)
            spacing_index = i

            cut_x = cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[spacing_index]
            cut_y = cls.EVEREST_Y_DATUM + cls.EVEREST_CUT_DEPTHS[depth_index]
            cut_points.append((cut_x, cut_y))
        angled_cutter = key_cutters.smooth_angled_cutter(cut_points, SCHLAGE_CUT_WIDTH, cls.EVEREST_Y_DATUM - 0.25 * MM, SCHLAGE_CUT_ANGLE)

        with BuildPart() as everest_key:
            add(everest_blank)

            with BuildSketch() as mb_c:
                add(angled_cutter)
            extrude(amount=cls.EVEREST_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
        everest_key.part = everest_key.part.rotate(Axis.X, 180)
        return Part(everest_key.part)


class EverestPrimus(key.Key, EverestBlank):
    @classmethod
    def name(cls) -> str:
        return "schlage_everest_primus"

    @classmethod
    def display_name(cls) -> str:
        return "Schlage Everest Primus"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest Primus": {"ep_6pin": "6-Pin", "ep_ctrl": "Control"},
            "Everest 29 Primus": {"e29p_6pin": "29 6-Pin", "e29p_ctrl": "29 Control"},
        }

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest": {
                "c000": "C000",
                "c100": "C100",
                "c200": "C200",
                "c150": "C150",
                "c120": "C120",
                "c230": "C230",
                "c134": "C134",
                "c145": "C145",
                "c135": "C135",
                "c125": "C125",
                "c124": "C124",
                "c123": "C123",
                "c234": "C234",
                "c235": "C235",
                "c245": "C245",
                "c345": "C345",
            },
            "Everest 29": {
                "s000": "S000",
                "s100": "S100",
                "s200": "S200",
                "s150": "S150",
                "s120": "S120",
                "s230": "S230",
                "s134": "S134",
                "s145": "S145",
                "s135": "S135",
                "s125": "S125",
                "s124": "S124",
                "s123": "S123",
                "s234": "S234",
                "s235": "S235",
                "s245": "S245",
                "s345": "S345",
            },
        }

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 6, defined from bow to tip. Sidebar up to 5, defined from bow to tip.<br>"
            "<i>Separate main cuts from sidebar with a space.</i><br>"
            "<b>Depths:</b> Maximum Lift 0 to Minimum Lift 9, Sidebar 1 through 7<br><b>Example:</b> <i>326163 23645</i><br>"
            "<i>Make sure warding channels are clean after printing or key will be difficult to use!</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        main_bitting, sidebar_bitting = bitting.split(" ")
        if not main_bitting.isnumeric() or not sidebar_bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

        if len(main_bitting) > 6:
            raise ValueError("Only up to 6 main cuts are allowed")
        if len(sidebar_bitting) > 5:
            raise ValueError("Only up to 5 sidebar cuts are allowed")

        for cut in main_bitting:
            if int(cut) < 0 or int(cut) > 9:
                raise ValueError("Main cut depths must be from 0 to 9")
        for cut in sidebar_bitting:
            if int(cut) < 1 or int(cut) > 7:
                raise ValueError("Sidebar cuts must be from 1 to 7")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        return EverestBlank.blank(profile, keyway)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        primus_blank = cls.blank(profile, keyway)
        main_bitting, sidebar_bitting = bitting.split(" ")

        main_cut_points: list[tuple[float, float]] = []
        sidebar_cut_points: list[tuple[float, float]] = []

        for i, cut in enumerate(main_bitting):
            depth_index = int(cut)
            spacing_index = i

            cut_x = cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[spacing_index]
            cut_y = cls.EVEREST_Y_DATUM + cls.EVEREST_CUT_DEPTHS[depth_index]
            main_cut_points.append((cut_x, cut_y))

        for i, cut in enumerate(sidebar_bitting):
            pin_index = int(cut) - 1
            spacing_index = i

            x_offset, y_offset = cls.EVEREST_PRIMUS_SIDEBAR_CUT_DATA[pin_index]
            cut_x = cls.EVEREST_X_DATUM + cls.EVEREST_PRIMUS_SIDEBAR_SPACINGS[spacing_index] + x_offset
            cut_y = cls.EVEREST_SIDEBAR_Y_DATUM - y_offset
            sidebar_cut_points.append((cut_x, cut_y))

        main_angled_cutter = key_cutters.smooth_angled_cutter(main_cut_points, SCHLAGE_CUT_WIDTH, cls.EVEREST_Y_DATUM - 0.25 * MM, SCHLAGE_CUT_ANGLE)
        sidebar_angled_cutter = key_cutters.angled_cutter(sidebar_cut_points, SCHLAGE_CUT_WIDTH, cls.EVEREST_SIDEBAR_Y_DATUM - 0.1 * IN, 10 * MM, SCHLAGE_CUT_ANGLE)

        with BuildPart() as primus_key:
            add(primus_blank)

            with BuildSketch() as mb_c:
                add(main_angled_cutter)
            extrude(amount=cls.EVEREST_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
            with BuildSketch() as sb_c:
                add(sidebar_angled_cutter)
            extrude(amount=cls.EVEREST_SIDEBAR_WIDTH - 0.005, mode=Mode.SUBTRACT)
        primus_key.part = primus_key.part.rotate(Axis.X, 180)
        return Part(primus_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    # sb = EverestPrimus.blank("e29p_ctrl", "c124")
    # export_step(sb, "e29_blank.step")
    # key = EverestPrimus.key("ep_6pin", "c124", "326163 23645")
    # export_step(key, "ep_key.step")
    key = Everest.key("e29_6pin", "s123", "878587")
    # export_step(key, "ep_key.step")
    show_all()
