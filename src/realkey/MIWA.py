from build123d import *

from realkey import key, key_cutters, resource_fetcher, svgtools


class SR(key.Key):
    SR_KEY_X_DATUM = 28 * MM
    SR_KEY_Y_DATUM = 7.375 * MM
    SR_KEY_WIDTH = 2 * MM
    SR_KEY_BLADE_HEIGHT = 8.25 * MM
    SR_KEY_BLADE_WIDTH = 0.75 * MM
    SR_KEY_OFFSET = 1.0 * MM

    SR_CUT_SPACINGS = [i * 2.25 * MM + 5.5 * MM for i in range(11)]
    SR_CUT_DEPTHS = [0 * MM, 0.625 * MM, 1.575 * MM, 2 * MM]  # last cut jumps to 2mm based on known cuts
    SR_CUT_WIDTH = 1 * MM
    SR_CUT_ANGLE = 120

    @classmethod
    def tag(cls) -> str:
        return "miwa_sr"

    @classmethod
    def display_name(cls) -> str:
        return "MIWA SR"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {"": {"10cut": "10-cut"}}

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {"": {"sr": "SR"}}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return "<b>Cuts:</b> Up to 10, defined from bow to tip.<br><b>Depths:</b> Maximum lift 0 to minimum lift 3<br><b>Example:</b> <i>1101203021</i>"

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return (
            "<h2>MIWA SR Bitting</h2>"
            "<div class='even-flex'>"
            "<table><caption>Key Width</caption>"
            "<thead><tr><th>Cut</th><th>Width</th></tr></thead>"
            "<tbody>"
            f"<tr><td>0</td><td>{cls.SR_KEY_BLADE_HEIGHT - 2 * cls.SR_CUT_DEPTHS[0]}mm</td></tr>"
            f"<tr><td>1</td><td>{cls.SR_KEY_BLADE_HEIGHT - 2 * cls.SR_CUT_DEPTHS[1]}mm</td></tr>"
            f"<tr><td>2</td><td>{cls.SR_KEY_BLADE_HEIGHT - 2 * cls.SR_CUT_DEPTHS[2]}mm</td></tr>"
            f"<tr><td>3</td><td>{cls.SR_KEY_BLADE_HEIGHT - 2 * cls.SR_CUT_DEPTHS[3]}mm</td></tr>"
            "</tbody></table>"
            "<table><caption>Cut Depth</caption>"
            "<thead><tr><th>Cut</th><th>Width</th></tr></thead>"
            "<tbody>"
            f"<tr><td>0</td><td>{cls.SR_CUT_DEPTHS[0]}mm</td></tr>"
            f"<tr><td>1</td><td>{cls.SR_CUT_DEPTHS[1]}mm</td></tr>"
            f"<tr><td>2</td><td>{cls.SR_CUT_DEPTHS[2]}mm</td></tr>"
            f"<tr><td>3</td><td>{cls.SR_CUT_DEPTHS[3]}mm</td></tr>"
            "</tbody></table>"
            "<table><caption>Cut Spacing</caption>"
            "<thead><tr><th>Cut</th><th>Spacing</th></tr></thead>"
            "<tbody>"
            f"<tr><td>1</td><td>{cls.SR_CUT_SPACINGS[0]}mm</td></tr>"
            f"<tr><td>2</td><td>{cls.SR_CUT_SPACINGS[1]}mm</td></tr>"
            f"<tr><td>3</td><td>{cls.SR_CUT_SPACINGS[2]}mm</td></tr>"
            f"<tr><td>4</td><td>{cls.SR_CUT_SPACINGS[3]}mm</td></tr>"
            f"<tr><td>5</td><td>{cls.SR_CUT_SPACINGS[4]}mm</td></tr>"
            f"<tr><td>6</td><td>{cls.SR_CUT_SPACINGS[5]}mm</td></tr>"
            f"<tr><td>7</td><td>{cls.SR_CUT_SPACINGS[6]}mm</td></tr>"
            f"<tr><td>8</td><td>{cls.SR_CUT_SPACINGS[7]}mm</td></tr>"
            f"<tr><td>9</td><td>{cls.SR_CUT_SPACINGS[9]}mm</td></tr>"
            f"<tr><td>10</td><td>{cls.SR_CUT_SPACINGS[10]}mm</td></tr>"
            "</tbody></table>"
            "</div>"
            "<div><h3>Keyed</h3>"
            "An example key decoding is provided below, note the dead space after the 8th bitting, this is because the SR lacks a slider/wafer in this position."
            "<div class='even-flex'><img src='resources/MIWA/SR_Key_Decode.png'/></div>"
            "</div><h3>Keyless</h3>"
            "Removing the core from the housing, bitting can be read from where to wafers sit at rest. An example decoding is provided below."
            "<div class='even-flex'><img src='resources/MIWA/SR_Lock_Decode.png'/></div>"
            "</div>"
        )

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if len(bitting) > 10:
            raise ValueError("Only up to 10 cuts are allowed")
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

        for cut in bitting:
            if int(cut) < 0 or int(cut) > 3:
                raise ValueError("Cut depths must be from 0 to 3")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if not resource_fetcher.pre_fetch_resource("resources/MIWA/SR.svg"):
            raise ValueError("Unable to load MIWA SR SVG")
        miwa_svg = import_svg("resources/MIWA/SR.svg", flip_y=False, label_by="inkscape:label")
        profile_face = svgtools.get_starting_at_origin(miwa_svg, "#profile_sr_" + profile)
        keyway_face = svgtools.get_centered_around_origin(miwa_svg, "#keyway_" + keyway)
        keyway_face.translate((1, 0, 0))

        with BuildPart() as sr_blank:
            with BuildSketch():
                add(profile_face)
            extrude(amount=cls.SR_KEY_WIDTH)

            with BuildSketch(Plane.YZ.offset(cls.SR_KEY_X_DATUM)):
                with Locations((cls.SR_KEY_Y_DATUM + cls.SR_KEY_BLADE_HEIGHT / 2, cls.SR_KEY_WIDTH / 2)):
                    Rectangle(cls.SR_KEY_BLADE_HEIGHT + 5.0 * MM, cls.SR_KEY_WIDTH)
                    kw = add(keyway_face, mode=Mode.PRIVATE)
                    offset(kw, amount=-0.125 * MM, kind=Kind.INTERSECTION, mode=Mode.SUBTRACT)
            extrude(amount=50 * MM, mode=Mode.SUBTRACT)
        return Part(sr_blank.part)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        sr_blank = cls.blank(profile, keyway)
        mirror_plane = Plane.XZ.offset(-cls.SR_KEY_Y_DATUM - cls.SR_KEY_BLADE_HEIGHT / 2)

        cut_points: list[tuple[float, float]] = []
        for i, cut in enumerate(bitting):
            depth_index = int(cut)
            if i == 8:
                cut_points.append((cls.SR_KEY_X_DATUM + cls.SR_CUT_SPACINGS[8], cls.SR_KEY_Y_DATUM))
            spacing_index = i if i < 8 else i + 1  # there is a blank cut at position 8

            cut_x = cls.SR_KEY_X_DATUM + cls.SR_CUT_SPACINGS[spacing_index]
            cut_y = cls.SR_KEY_Y_DATUM + cls.SR_CUT_DEPTHS[depth_index]
            cut_points.append((cut_x, cut_y))

        angled_cutter = key_cutters.smooth_angled_cutter(cut_points, cls.SR_CUT_WIDTH, cls.SR_KEY_Y_DATUM - 0.25 * MM, cls.SR_CUT_ANGLE)

        with BuildPart() as sr_key:
            add(sr_blank)

            with BuildSketch():
                add(angled_cutter)
                mirra = mirror(about=mirror_plane)
            extrude(amount=cls.SR_KEY_WIDTH * 2, mode=Mode.SUBTRACT)
        return Part(sr_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    # sr_blank = SR.blank("10cut", "sr")
    # export_step(sr_blank, "sr_blank.step")
    sr_key = SR.key("10cut", "sr", "1101203021")
    # export_step(sr_key, "sr_key.step")
    show_all()
