from build123d import *

from realkey import key, key_cutters, resource_fetcher


class SGSDB(key.Key):
    SG_CUT_SPACINGS = {
        "60": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.367 * IN, 0.422 * IN],
        "87h": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.378 * IN],
        "87h_7cut": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.367 * IN, 0.415 * IN, 0.470 * IN],
        "96": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.367 * IN, 0.422 * IN],
        "96_7cut": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.367 * IN, 0.415 * IN, 0.470 * IN],
        "9609": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.378 * IN],
        "sy3b": [0.167 * IN, 0.222 * IN, 0.271 * IN, 0.319 * IN, 0.378 * IN],
    }
    SG_CUT_WIDTHS = {
        "60": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "87h": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "87h_7cut": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "96": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "96_7cut": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "9609": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
        "sy3b": [0.066 * IN, 0.052 * IN, 0.052 * IN, 0.052 * IN, 0.066 * IN],
    }
    SG_CUT_DEPTHS = {
        "60": [0.001 * IN, 0.017 * IN, 0.037 * IN, 0.057 * IN, 0.077 * IN, 0.097 * IN, 0.117 * IN, 0.137 * IN],
        "87h": [i * 0.020 * IN for i in range(8)],
        "87h_7cut": [i * 0.020 * IN for i in range(8)],
        "96": [0.001 * IN, 0.017 * IN, 0.037 * IN, 0.057 * IN, 0.077 * IN, 0.097 * IN, 0.117 * IN, 0.137 * IN],
        "96_7cut": [0.001 * IN, 0.017 * IN, 0.037 * IN, 0.057 * IN, 0.077 * IN, 0.097 * IN, 0.117 * IN, 0.137 * IN],
        "9609": [i * 0.020 * IN + 0.005 * IN for i in range(8)],
        "sy3b": [i * 0.020 * IN for i in range(8)],
    }

    SG_KEY_WIDTH = {
        "60": 0.070 * IN,
        "87h": 0.080 * IN,
        "87h_7cut": 0.080 * IN,
        "96": 0.070 * IN,
        "96_7cut": 0.070 * IN,
        "9609": 0.070 * IN,
        "sy3b": 0.063 * IN,
    }
    SG_X_DATUM = {
        "60": 2.15 * IN,
        "87h": 59.936 * MM,
        "87h_7cut": 59.936 * MM,
        "96": 2.15 * IN,
        "96_7cut": 2.15 * IN,
        "9609": 2.145 * IN,
        "sy3b": 2.15 * IN,
    }
    SG_Y_DATUM = {
        "60": 0.380 * IN,
        "87h": 8.45 * MM,
        "87h_7cut": 8.45 * MM,
        "96": 0.3425 * IN,
        "96_7cut": 0.3425 * IN,
        "9609": 0.395 * IN,
        "sy3b": 0.3785 * IN,
    }

    SG_THROAT_SPACING = {
        "60": 1.1400 * IN,
        "87h": 1.1300 * IN,
        "87h_7cut": 1.1300 * IN,
        "96": 1.1400 * IN,
        "96_7cut": 1.1400 * IN,
        "9609": 1.1400 * IN,
        "sy3b": 1.0000 * IN,
    }
    SG_THROAT_Y_DATUM = {
        "60": 0.305 * IN,
        "87h": 8.45 * MM,
        "87h_7cut": 8.45 * MM,
        "96": 0.3425 * IN,
        "96_7cut": 0.3425 * IN,
        "9609": 0.325 * IN,
        "sy3b": 0.350 * IN,
    }
    SG_THROAT_DEPTH = {
        "60": 0.080 * IN,
        "87h": 0.075 * IN,
        "87h_7cut": 0.075 * IN,
        "96": 0.080 * IN,
        "96_7cut": 0.080 * IN,
        "9609": 0.080 * IN,
        "sy3b": 0.080 * IN,
    }
    SG_THROAT_WIDTH = {
        "60": 0.105 * IN,
        "87h": 0.105 * IN,
        "87h_7cut": 0.105 * IN,
        "96": 0.105 * IN,
        "96_7cut": 0.105 * IN,
        "9609": 0.105 * IN,
        "sy3b": 0.105 * IN,
    }

    SG_GUARD_TIP_DEPTH = {"87h": 0.188 * IN, "87h_7cut": 0.188 * IN, "9609": 0.193 * IN, "sy3b": 0.156 * IN}

    SG_PROFILE_LOAD_DICT = {
        "60": "resources/SargentAndGreenleaf/60.step",
        "96": "resources/SargentAndGreenleaf/96.step",
        "96_7cut": "resources/SargentAndGreenleaf/96.step",
        "87h": "resources/SargentAndGreenleaf/87H.step",
        "87h_7cut": "resources/SargentAndGreenleaf/87H.step",
        "9609": "resources/SargentAndGreenleaf/9609.step",
        "sy3b": "resources/SargentAndGreenleaf/SY3B.step",
    }

    @classmethod
    def name(cls) -> str:
        return "sg_sdb"

    @classmethod
    def display_name(cls) -> str:
        return "S&G Safe Deposit Box"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {"Renter": {"60": "60", "96": "96", "96_7cut": "96 7-Cut"}, "Guard": {"87h": "87H", "87h_7cut": "87H 7-Cut", "9609": "9609", "sy3b": "SY3B"}}

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {"": {"lever": "Lever"}}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return "<b>Cuts:</b> Amount depends on profile, from 5 to 7, from tip to bow.<br><b>Depths:</b> Maximum Lift 0 to Minimum Lift 7.<br><b>Example:</b> <i>24622</i>"

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return (
            "<h2>S&G Safe Deposit Box Keys</h2>"
            "These are keys for S&G lever locks used in safe deposit boxes. Decoding can be done by looking at the levers on most S&G as they are labelled, except for the rekeyable 41XX and 45XX which need examination."
            "<div class='even-flex'>"
            "<table><caption>Profile</caption>"
            "<thead>"
            "<tr><th>Lock Series</th><th>Renter Key</th><th>Guard Key</th>"
            "</thead>"
            "<tbody>"
            "<tr><td>4100 Series</td><td>96 7-Cut</td><td>No guard</td></tr>"
            "<tr><td>4231</td><td>96</td><td>SY3B</td></tr>"
            "<tr><td>4420</td><td>96</td><td>87H</td></tr>"
            "<tr><td>4440</td><td>96</td><td>87H</td></tr>"
            "<tr><td>4442</td><td>60</td><td>87H</td></tr>"
            "<tr><td>4443</td><td>60</td><td>9609</td></tr>"
            "<tr><td>4444</td><td>96</td><td>87H</td></tr>"
            "<tr><td>4500 Series</td><td>96 7-Cut</td><td>87H 7-Cut</td></tr>"
            "</tbody>"
            "</table>"
            "<table><caption>Common Guard Keys</caption>"
            "<thead>"
            "<tr><th>Description</th><th>Bitting</th>"
            "</thead>"
            "<tbody>"
            "<tr><td>#3</td><td>40624</td>"
            "<tr><td>#4</td><td>20462</td>"
            "<tr><td>#7</td><td>26024</td>"
            "<tr><td>#8</td><td>26402</td>"
            "<tr><td>#12</td><td>04624</td>"
            "<tr><td>#52</td><td>0240262</td>"
            "<tr><td>#74</td><td>2204622</td>"
            "<tr><td>P4</td><td><i>24422</i> - Suspect</td>"
            "<tr><td>P101</td><td>64042</td>"
            "<tr><td>ST4</td><td>20462</td>"
            "<tr><td>SY3</td><td>20024</td>"
            "</tbody>"
            "</table>"
            "</div>"
        )

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")
        if profile in ["87h", "9609", "sy3b"] and len(bitting) > 5:
            raise ValueError(f"S&G {cls.profiles()[profile]} has a maximum of 5 cuts")
        if profile in ["60", "96"] and len(bitting) > 6:
            raise ValueError(f"S&G {cls.profiles()[profile]} has a maximum of 6 cuts")
        if profile in ["87h_7cut", "96_7cut"] and len(bitting) > 7:
            raise ValueError(f"S&G {cls.profiles()[profile]} has a maximum of 7 cuts")

        for cut in bitting:
            if int(cut) < 0 or int(cut) > 7:
                raise ValueError("Cut depths must be from 0 to 7")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        blank = None
        if profile in cls.SG_PROFILE_LOAD_DICT:
            res = cls.SG_PROFILE_LOAD_DICT[profile]
            if not resource_fetcher.pre_fetch_resource(res):
                raise ValueError("Unable to load S&G blank")
            with BuildPart() as step_blank:
                add(import_step(res))
            blank = step_blank.part
        if blank is None:
            raise ValueError("Issue loading blank")
        return Part(blank)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> key_cutters.Part:
        cls.validate_bitting(profile, keyway, bitting)

        sg_blank = cls.blank(profile, keyway)
        spacings = cls.SG_CUT_SPACINGS[profile]
        depths = cls.SG_CUT_DEPTHS[profile]
        widths = cls.SG_CUT_WIDTHS[profile]
        x_datum = cls.SG_X_DATUM[profile]
        y_datum = cls.SG_Y_DATUM[profile]
        throat_spacing = cls.SG_THROAT_SPACING[profile]
        throat_y_datum = cls.SG_THROAT_Y_DATUM[profile]
        throat_depth = cls.SG_THROAT_DEPTH[profile]
        throat_width = cls.SG_THROAT_WIDTH[profile]
        key_width = cls.SG_KEY_WIDTH[profile]

        lever_cuts: list[tuple[float, float, float]] = []
        for i, cut in enumerate(bitting):
            depth_index = int(cut)

            cut_x = x_datum - spacings[i]
            cut_y = y_datum + depths[depth_index]
            lever_cuts.append((cut_x, cut_y, widths[i]))

        # Add throat
        lever_cuts.append((x_datum - throat_spacing, throat_y_datum + throat_depth, throat_width))

        # Tip snip for guard keys
        if profile in cls.SG_GUARD_TIP_DEPTH:
            depth = cls.SG_GUARD_TIP_DEPTH[profile]
            lever_cuts.append((x_datum + 0.2 * IN, y_datum + depth, 0.4 * IN))

        lever_cutter = key_cutters.lever_cutter(lever_cuts, throat_y_datum - 0.001 * MM)

        with BuildPart() as sg_key:
            add(sg_blank)

            with BuildSketch():
                add(lever_cutter)
            extrude(amount=key_width * 2, mode=Mode.SUBTRACT)
        return Part(sg_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    # blank = SGLever.blank("87h", "lever")
    key = SGSDB.key("sy3b", "lever", "20462")
    show_all()
    # export_step(key, "guard_key.step")
