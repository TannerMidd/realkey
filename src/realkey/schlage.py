from build123d import *
from realkey import key, key_cutters, resource_fetcher, svgtools

SCHLAGE_ROOT_DEPTHS = [0.335 * IN - i * 0.015 * IN for i in range(10)]
SCHLAGE_CUT_SPACINGS = [0.231 * IN + 0.1562 * IN * i for i in range(6)]
SCHLAGE_CUT_ANGLE = 100
SCHLAGE_CUT_WIDTH = 0.031 * IN


class EverestKeyway:
    KEYWAY_NOTCHES: dict[str, list[int]] = {
        "000": [0, 1, 2, 3, 4],
        "100": [0, 1, 2, 3],
        "200": [0, 1, 2, 4],
        "150": [1, 2, 3],
        "120": [0, 1, 2],
        "230": [0, 1, 4],
        "134": [0, 3],
        "145": [2, 3],
        "135": [1, 3],
        "125": [1, 2],
        "124": [0, 2],
        "123": [0, 1],
        "234": [0, 4],
        "235": [1, 4],
        "245": [2, 4],
        "345": [3, 4],
    }

    @classmethod
    def build_keyway(cls, keyway_tag: str) -> Face:
        family = keyway_tag[0]
        species = keyway_tag[1:]

        if not resource_fetcher.pre_fetch_resource("resources/Schlage/Everest.svg"):
            raise ValueError("Unable to load Schlage Everest SVG")
        everest_svg = import_svg("resources/Schlage/Everest.svg", flip_y=False, label_by="inkscape:label")
        keyway_base = svgtools.get_starting_at_origin(everest_svg, "#keyway_" + family)

        notches = cls.KEYWAY_NOTCHES[species]

        with BuildSketch() as keyway:
            add(keyway_base)

            if 0 in notches:
                with BuildLine():
                    Polyline((0, 7.25), (0.5, 7.15), (0.5, 6.65), (0, 6.55), (0, 7.25))
                make_face(mode=Mode.SUBTRACT)
            if 1 in notches:
                with BuildLine():
                    Polyline((0, 6.75), (0.5, 6.65), (0.5, 6.15), (0, 6.05), (0, 6.75))
                make_face(mode=Mode.SUBTRACT)
            if 2 in notches:
                with BuildLine():
                    Polyline((0, 6.25), (0.5, 6.15), (0.5, 5.65), (0, 5.55), (0, 6.25))
                make_face(mode=Mode.SUBTRACT)
            if 3 in notches:
                with BuildLine():
                    Polyline((0, 5.75), (0.5, 5.65), (0.5, 5.15), (0, 5.05), (0, 5.75))
                make_face(mode=Mode.SUBTRACT)
            if 4 in notches:
                if family == "b" or family == "r":
                    with BuildLine():
                        Polyline((0, 4.75), (0.5, 4.75), (1.650, 3.345), (0, 3.345), (0, 4.75))
                    make_face(mode=Mode.SUBTRACT)
                if family == "c" or family == "s":
                    with BuildLine():
                        Polyline((0, 4.45), (0.775, 4.35), (0.775, 3.85), (0, 3.75), (0, 4.45))
                    make_face(mode=Mode.SUBTRACT)

        r = keyway.face()
        r.position -= r.bounding_box().center()

        return r

    @classmethod
    def b_keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest Restricted SL/SFIC": {
                "b000": "B000",
                "b100": "B100",
                "b200": "B200",
                "b150": "B150",
                "b120": "B120",
                "b230": "B230",
                "b134": "B134",
                "b145": "B145",
                "b135": "B135",
                "b125": "B125",
                "b124": "B124",
                "b123": "B123",
                "b234": "B234",
                "b235": "B235",
                "b245": "B245",
                "b345": "B345",
            }
        }

    @classmethod
    def c_keyways(cls) -> dict[str, dict[str, str]]:
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
            }
        }

    @classmethod
    def d_keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest Restricted": {
                "d000": "D000",
                "d100": "D100",
                "d200": "D200",
                "d150": "D150",
                "d120": "D120",
                "d230": "D230",
                "d134": "D134",
                "d145": "D145",
                "d135": "D135",
                "d125": "D125",
                "d124": "D124",
                "d123": "D123",
                "d234": "D234",
                "d235": "D235",
                "d245": "D245",
                "d345": "D345",
            }
        }

    @classmethod
    def r_keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest 29 Restricted SL/SFIC": {
                "r000": "R000",
                "r100": "R100",
                "r200": "R200",
                "r150": "R150",
                "r120": "R120",
                "r230": "R230",
                "r134": "R134",
                "r145": "R145",
                "r135": "R135",
                "r125": "R125",
                "r124": "R124",
                "r123": "R123",
                "r234": "R234",
                "r235": "R235",
                "r245": "R245",
                "r345": "R345",
            }
        }

    @classmethod
    def s_keyways(cls) -> dict[str, dict[str, str]]:
        return {
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
            }
        }

    @classmethod
    def t_keyways(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest 29 Restricted": {
                "t000": "T000",
                "t100": "T100",
                "t200": "T200",
                "t150": "T150",
                "t120": "T120",
                "t230": "T230",
                "t134": "T134",
                "t145": "T145",
                "t135": "T135",
                "t125": "T125",
                "t124": "T124",
                "t123": "T123",
                "t234": "T234",
                "t235": "T235",
                "t245": "T245",
                "t345": "T345",
            }
        }


class EverestBlank:
    EVEREST_KEY_WIDTH = 2.75 * MM
    EVEREST_KEY_BLADE_HEIGHT = 0.343 * IN
    EVEREST_SL_KEY_BLADE_HEIGHT = 8.15 * MM

    EVEREST_X_DATUM = 31.400 * MM
    EVEREST_Y_DATUM = 10.725 * MM
    EVEREST_Y2_DATUM = 19.338 * MM
    EVEREST_SL_Y_DATUM = 11 * MM
    EVEREST_SIDEBAR_Y_DATUM = 19.437 * MM
    EVEREST_SIDEBAR_WIDTH = 1.2 * MM

    EVEREST_PRIMUS_SIDEBAR_SPACINGS = [(a + b) / 2 for a, b in zip(SCHLAGE_CUT_SPACINGS[0:-1], SCHLAGE_CUT_SPACINGS[1:])]
    EVEREST_PRIMUS_SIDEBAR_OFFSET = 32 * THOU

    EVEREST_PRIMUS_SIDEBAR_ROOT_DEPTHS = [36 * THOU, 60 * THOU]
    EVEREST_PRIMUS_SIDEBAR_OFFSET_ROOT_DEPTHS = [24 * THOU + i * 24 * THOU for i in range(3)]

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
            "Everest SL": {"esl_7pin": "SL 7-Pin", "esl_ctrl": "SL Control"},
            "Everest Primus": {"ep_6pin": "Primus 6-Pin", "ep_ctrl": "Primus Control"},
            "Everest 29": {"e29_6pin": "29 6-Pin", "e29_ctrl": "29 Control"},
            "Everest 29SL": {"e29sl_7pin": "29SL 7-Pin", "e29sl_ctrl": "29SL Control"},
            "Everest 29 Primus": {"e29p_6pin": "29 Primus 6-Pin", "e29p_ctrl": "29 Primus Control"},
        }

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return EverestKeyway.c_keyways() | EverestKeyway.r_keyways() | EverestKeyway.s_keyways()

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if not resource_fetcher.pre_fetch_resource("resources/Schlage/Everest.svg"):
            raise ValueError("Unable to load Schlage Everest SVG")

        everest_svg = import_svg("resources/Schlage/Everest.svg", flip_y=False, label_by="inkscape:label")

        lookup_profile = ""
        if profile in ["e_6pin", "ep_6pin"]:
            lookup_profile = "e_6pin"
        if profile in ["e_ctrl", "ep_ctrl"]:
            lookup_profile = "e_ctrl"
        if profile in ["esl_7pin"]:
            lookup_profile = "esl_7pin"
        if profile in ["esl_ctrl"]:
            lookup_profile = "esl_ctrl"
        if profile in ["e29_6pin", "e29p_6pin"]:
            lookup_profile = "e29_6pin"
        if profile in ["e29_ctrl", "e29p_ctrl"]:
            lookup_profile = "e29_ctrl"
        if profile in ["e29sl_7pin"]:
            lookup_profile = "e29sl_7pin"
        if profile in ["e29sl_ctrl"]:
            lookup_profile = "e29sl_ctrl"

        y_datum = cls.EVEREST_Y_DATUM
        blade_height = cls.EVEREST_KEY_BLADE_HEIGHT
        if profile in ["esl_7pin", "esl_ctrl", "e29sl_7pin", "e29sl_ctrl"]:
            y_datum = cls.EVEREST_SL_Y_DATUM
            blade_height = cls.EVEREST_SL_KEY_BLADE_HEIGHT

        blank_profile = svgtools.get_starting_at_origin(everest_svg, "#profile_" + lookup_profile)
        blank = extrude(blank_profile, cls.EVEREST_KEY_WIDTH)

        keyway_shape = EverestKeyway.build_keyway(keyway)
        keyway_cutter = Rectangle(cls.EVEREST_KEY_WIDTH, blade_height + 0.025)
        keyway_cutter -= keyway_shape

        keyway_cutter = Sketch(Location((cls.EVEREST_X_DATUM, y_datum + blade_height / 2, cls.EVEREST_KEY_WIDTH / 2), (0, 90, 0)) * keyway_cutter)
        keyway_cutter = extrude(keyway_cutter, 40 * MM)
        blank -= keyway_cutter

        tip_x = 63.15
        if profile in ["esl_7pin", "esl_ctrl", "e29sl_7pin", "e29sl_ctrl"]:
            tip_x = 66.5
        with BuildPart() as sidebar_ramp:
            with BuildSketch():
                with BuildLine():
                    Polyline((tip_x - 4 * MM, 19.275), (tip_x - 2 * MM, 19.275), (tip_x, 16), (tip_x - 8 * MM, 16), (tip_x - 4 * MM, 19.275))
                make_face()
            extrude(amount=cls.EVEREST_SIDEBAR_WIDTH - 0.001)
        blank -= sidebar_ramp.part

        if profile in ["e_6pin", "e_ctrl", "esl_7pin", "esl_ctrl", "e29_6pin", "e29_ctrl", "e29sl_7pin", "e29sl_ctrl"]:
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
    def tag(cls) -> str:
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
        return EverestKeyway.c_keyways() | EverestKeyway.s_keyways()

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 6, defined from bow to tip.<br>"
            "<b>Depths:</b> Maximum Lift 0 to Minimum Lift 9<br>"
            "<b>Example:</b> <i>879597</i><br>"
            "<i>Make sure warding channels are clean after printing or key will be difficult to use!</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if len(bitting) > 6:
            raise ValueError("Only up to 6 cuts are allowed")

        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

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
            cut_y = cls.EVEREST_Y2_DATUM - SCHLAGE_ROOT_DEPTHS[depth_index]
            cut_points.append((cut_x, cut_y))
        # Add a ghost cut at the same height to trim any trailing steeple
        cut_points.append((cut_points[-1][0] + 10*MM, cut_points[-1][1]))
        angled_cutter = key_cutters.smooth_angled_cutter(cut_points, SCHLAGE_CUT_WIDTH, cls.EVEREST_Y_DATUM - 0.25 * MM, SCHLAGE_CUT_ANGLE)

        with BuildPart() as everest_key:
            add(everest_blank)

            with BuildSketch() as mb_c:
                add(angled_cutter)
            extrude(amount=cls.EVEREST_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
        if everest_key.part is None:
            raise ValueError("Unable to generate key")
        return Part(everest_key.part)


class EverestSL(key.Key, EverestBlank):
    EVEREST_SL_Y_DATUM = 19.15 * MM

    EVEREST_SL_SPACINGS = [1.096 * IN - 0.15 * IN * i for i in range(7)]
    EVEREST_SL_DEPTHS = [0.3187 * IN - 0.0125 * IN * i for i in range(9)]
    EVEREST_SL_CUT_WIDTH = 0.056 * IN
    EVEREST_SL_ANGLE = 90

    @classmethod
    def tag(cls) -> str:
        return "schlage_everest_sl"

    @classmethod
    def display_name(cls) -> str:
        return "Schlage Everest SL/SFIC"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {
            "Everest SL": {"esl_7pin": "7-Pin", "esl_ctrl": "Control"},
            "Everest SL29": {"e29sl_7pin": "29 7-Pin", "e29sl_ctrl": "29 Control"},
        }

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return EverestKeyway.b_keyways() | EverestKeyway.r_keyways()

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 7, defined from tip to bow.<br>"
            "<b>Depths:</b> Maximum Lift 0 to Minimum Lift 9<br>"
            "<b>Example:</b> <i>2701507</i><br>"
            "<i>Make sure warding channels are clean after printing or key will be difficult to use!</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if len(bitting) > 7:
            raise ValueError("Only up to 7 cuts are allowed")

        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

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

            cut_x = cls.EVEREST_X_DATUM + cls.EVEREST_SL_SPACINGS[spacing_index]
            cut_y = cls.EVEREST_SL_Y_DATUM - cls.EVEREST_SL_DEPTHS[depth_index]
            cut_points.append((cut_x, cut_y))
        angled_cutter = key_cutters.smooth_angled_cutter(cut_points, cls.EVEREST_SL_CUT_WIDTH, cls.EVEREST_Y_DATUM - 0.25 * MM, cls.EVEREST_SL_ANGLE)

        with BuildPart() as everest_key:
            add(everest_blank)

            with BuildSketch() as mb_c:
                add(angled_cutter)
            extrude(amount=cls.EVEREST_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
        if everest_key.part is None:
            raise ValueError("Unable to generate key")
        return Part(everest_key.part)


class EverestPrimus(key.Key, EverestBlank):
    @classmethod
    def tag(cls) -> str:
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
        return EverestKeyway.c_keyways() | EverestKeyway.s_keyways()

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 6, defined from bow to tip. Sidebar up to 5, defined from bow to tip.<br>"
            "<i>Separate main cuts from sidebar with a space.</i><br>"
            "<b>Depths:</b> Maximum Lift 0 to Minimum Lift 9, Sidebar 1 through 7<br>"
            "<b>Example:</b> <i>326163 23645</i><br>"
            "<i>Make sure warding channels are clean after printing or key will be difficult to use!</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def _split_bitting(cls, bitting: str) -> tuple[str, str]:
        rows = bitting.split()
        if len(rows) != 2:
            raise ValueError("Specify main and sidebar cuts separated by whitespace")
        return rows[0], rows[1]

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        main_bitting, sidebar_bitting = cls._split_bitting(bitting)
        if len(main_bitting) > 6:
            raise ValueError("Only up to 6 main cuts are allowed")
        if len(sidebar_bitting) > 5:
            raise ValueError("Only up to 5 sidebar cuts are allowed")

        if not main_bitting.isnumeric() or not sidebar_bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

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
        main_bitting, sidebar_bitting = cls._split_bitting(bitting)

        main_cut_points: list[tuple[float, float]] = []
        sidebar_cut_points: list[tuple[float, float]] = []

        for i, cut in enumerate(main_bitting):
            depth_index = int(cut)
            spacing_index = i

            cut_x = cls.EVEREST_X_DATUM + SCHLAGE_CUT_SPACINGS[spacing_index]
            cut_y = cls.EVEREST_Y2_DATUM - SCHLAGE_ROOT_DEPTHS[depth_index]
            main_cut_points.append((cut_x, cut_y))
        # Add a ghost cut at the same height to trim any trailing steeple
        main_cut_points.append((main_cut_points[-1][0] + 10*MM, main_cut_points[-1][1]))

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
        if primus_key.part is None:
            raise ValueError("Unable to generate key")
        return Part(primus_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    #keyway = EverestKeyway.build_keyway("r235")
    # sb = EverestPrimus.blank("e29p_ctrl", "s124")
    # export_step(sb, "e29_blank.step")
    # key = EverestPrimus.key("ep_6pin", "c124", "326163 23645")
    # export_step(key, "ep_key.step")
    key = Everest.key("e29_6pin", "s123", "879597")
    # export_step(key, "ep_key.step")
    # key = EverestSL.key("e29sl_ctrl", "r125", "2701507")
    # export_step(key, "e29sl_key.step")
    show_all()
