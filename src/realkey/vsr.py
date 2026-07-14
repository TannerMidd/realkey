from re import L

from build123d import *

from realkey import geom_tools, key, resource_fetcher, svgtools


class _2000(key.Key):
    VSR_2000_TOP_ROW_DEPTH = 1.6 * MM
    VSR_2000_SIDE_ROW_DEPTH = 2.1 * MM

    VSR_2000_X_DATUM = 30.75 * MM
    VSR_2000_Y_DATUM = 9.625 * MM
    VSR_2000_KEY_WIDTH = 2.45 * MM
    VSR_2000_KEY_HEIGHT = 6.75 * MM
    VSR_2000_Y_CENTER = 13 * MM
    VSR_2000_X_MAX = 55 * MM

    VSR_2000_L_CUT_SPACINGS = [5 * MM + 3.5 * MM * i for i in range(5)]
    VSR_2000_R_CUT_SPACINGS = [3.25 * MM + 3.5 * MM * i for i in range(6)]
    VSR_2000_T_CUT_SPACINGS = [7.75 + 3.5 * MM * i for i in range(4)]

    VSR_2000_CORE_DIAMETER = 0.375 * IN
    VSR_TOP_PASSIVE_ANGLE = 30
    VSR_SIDE_ANGLE = 65

    VSR_2000_PIN_OFFSET = [1.5625 * MM, 1.2125 * MM, 0.85 * MM, 0.5 * MM, 0.1 * MM]
    VSR_2000_TPIN_OFFSET = 0.1 * MM
    VSR_2000_PIN_HEAD_HEIGHT = [0.5 * MM, 0.85 * MM, 1.2 * MM, 1.5 * MM, 1.9 * MM]

    VSR_2000_PIN_DIA_1 = 2.5 * MM
    VSR_2000_PIN_DIA_2 = 2 * MM
    VSR_2000_PIN_PRO = 2.7 * MM

    @classmethod
    def tag(cls) -> str:
        return "vsr_2000"

    @classmethod
    def display_name(cls) -> str:
        return "VSR 2000"

    @classmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        return {"": {"1": "1"}}

    @classmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        return {"": {"1": "1"}}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "<b>Cuts:</b> Up to 6 right side, 3 top side, 5 left side, all defined from bow to tip.<br>"
            "<i>Separate each sides cuts with a space.</i><br>"
            "<b>Depths:</b> From maximum lift 1 to minimum lift 5. Top appears to only use depths 1 and 3, sides 2 through 5.<br>"
            "<b>Example:</b> <i>553534 331 24233</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return (
            "<h2>VSR 2000 Bitting</h2>"
            "<div class='even-flex'>"
            "<table><caption>Pin Measurements</caption>"
            "<thead><tr><th>Cut</th><th>Height</th><th>Head Height</th></tr></thead>"
            "<tbody>"
            "<tr><td>1</td><td>3.2mm</td><td>0.5mm</td></tr>"
            "<tr><td>2</td><td>3.55mm</td><td>0.85mm</td></tr>"
            "<tr><td>3</td><td>3.9mm</td><td>1.2mm</td></tr>"
            "<tr><td>4</td><td>4.2mm</td><td>1.5mm</td></tr>"
            "<tr><td>5</td><td>4.6mm</td><td>1.9mm</td></tr>"
            "</tbody>"
            "<tfoot>"
            "<tr><td colspan='3'>Shaft - 2.7mm length by 2mm diameter, head diameter - 2.5mm</td></tr>"
            "</tfoot>"
            "</table>"
            "</div>"
            "<div><h3>Pinning Info</h3>"
            "The left and right side pinning can ony support cuts 2 through 5. Cut 1 cannot be lifted to correct height even with a full width key blade. The sides use 2mm inset on each chamber, allowing 0.7mm protrusion into the keyway by default.<br>" \
            "The top appears to only use cuts 1 and 3. The 3rd space is offset to the side and always has a 1 cut in it, unsprung, to act as warding. The top chambers have a 1.8mm inset on each chamber, causing protrusion into the chamber to be slightly different than side pins. Cut 5 cannot fit in the top row.<br>"
            "Drivers are balanced, with the top stack using slightly shorter drivers for the same cut to make up for the difference in resting height.<br>"
        )

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        rows = bitting.split()
        if len(rows) != 3:
            raise ValueError("Specify right, top, and left cuts separated by spaces")

        r_bitting, t_bitting, l_bitting = rows

        if len(r_bitting) > 6:
            raise ValueError("Only up to 6 cuts allowed on the right side")
        if len(t_bitting) > 3:
            raise ValueError("Only up to 3 cuts allowed on the top side")
        if len(l_bitting) > 5:
            raise ValueError("Only up to 5 cuts allowed on the left side")

        if not r_bitting.isnumeric() or not t_bitting.isnumeric() or not l_bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")

        for cut in r_bitting:
            if int(cut) < 2 or int(cut) > 5:
                raise ValueError("Right-side cut depths must be from 2 to 5")
        for cut in t_bitting:
            if int(cut) not in [1, 3]:
                raise ValueError("Top cut depths must be 1 or 3")
        if len(t_bitting) == 3 and t_bitting[2] != "1":
            raise ValueError("The third top cut must be 1")
        for cut in l_bitting:
            if int(cut) < 2 or int(cut) > 5:
                raise ValueError("Left-side cut depths must be from 2 to 5")
        return

    @classmethod
    def blank(cls, profile: str, keyway: str) -> key.Part:
        blank = None
        res = "resources/VSR/2000-1-1.step"
        if not resource_fetcher.pre_fetch_resource(res):
            raise ValueError("Unable to load S&G blank")
        with BuildPart() as step_blank:
            add(import_step(res))

            xm = cls.VSR_2000_X_MAX
            with BuildSketch(Plane.XZ):
                with BuildLine():
                    Polyline(
                        (xm - 2.5, cls.VSR_2000_KEY_WIDTH),
                        (xm, cls.VSR_2000_KEY_WIDTH),
                        (xm, 0),
                        (xm - 2.5, 0),
                        (xm - 0.5, 1.0),
                        (xm - 0.5, cls.VSR_2000_KEY_WIDTH - 1 * MM),
                        (xm - 2.5, cls.VSR_2000_KEY_WIDTH),
                    )
                make_face()
            extrude(amount=-30 * MM, mode=Mode.SUBTRACT)

        blank = step_blank.part

        if blank is None:
            raise ValueError("Issue loading blank")
        return blank

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> key.Part:
        cls.validate_bitting(profile, keyway, bitting)

        vsr_blank = cls.blank(profile, keyway)

        r_bitting, t_bitting, l_bitting = bitting.split()

        # We use a model of a slightly larger than real pin to make cuts.
        # Its the correct height but intentionally fattened to give some fore-aft tolerance
        def fat_vsr_pin(cut: int):
            indx = cut - 1

            with BuildPart() as pin:
                with Locations((0, 0, 0.5 * MM)):
                    Cone(0.6 * MM, 1.25 * MM, 1 * MM)
                with BuildSketch(Plane.XY.offset(1 * MM)):
                    Circle(1.25 * MM)
                extrude(amount=1.7 * MM)
                with BuildSketch(Plane.XY.offset(2.7 * MM)):
                    Circle(1.5 * MM)
                extrude(amount=cls.VSR_2000_PIN_HEAD_HEIGHT[indx])
            if pin.part is None:
                raise ValueError("Invalid pin")
            return pin.part

        # These planes are used to position pins in the correct orientation
        core_center_x = cls.VSR_2000_X_DATUM
        core_center_y = cls.VSR_2000_Y_DATUM + cls.VSR_2000_CORE_DIAMETER / 2
        core_center_z = cls.VSR_2000_KEY_WIDTH / 2
        right_side_plane = Plane.XY.offset(core_center_z).shift_origin((core_center_x, core_center_y, core_center_z)).rotated((90 - cls.VSR_SIDE_ANGLE, 0, 0))
        left_side_plane = Plane.XY.offset(core_center_z).shift_origin((core_center_x, core_center_y, core_center_z)).rotated((90 + cls.VSR_SIDE_ANGLE, 0, 0))
        top_side_plane = Plane.XY.offset(core_center_z).shift_origin((core_center_x, core_center_y, core_center_z)).rotated((-90, 0, 0))
        top_passive_plane = Plane.XY.offset(core_center_z).shift_origin((core_center_x, core_center_y, core_center_z)).rotated((-90 - cls.VSR_TOP_PASSIVE_ANGLE, 0, 0))
        rl_mirror_plane = Plane.XY.offset(core_center_z)
        top_mirror_plane = Plane.XZ.offset(-cls.VSR_2000_Y_CENTER)

        with BuildPart() as vsr_key:
            add(vsr_blank)

            with BuildPart(right_side_plane, mode=Mode.SUBTRACT) as r_pins:
                for i, rp in enumerate(r_bitting):
                    pin = int(rp)
                    x = cls.VSR_2000_R_CUT_SPACINGS[i]
                    offset = cls.VSR_2000_PIN_OFFSET[pin - 1]

                    with Locations((x, 0, offset)):
                        add(fat_vsr_pin(pin))

            r_h_mirror = mirror(r_pins.part, rl_mirror_plane, mode=Mode.PRIVATE)
            r_pins_mirror = mirror(r_h_mirror, top_mirror_plane, mode=Mode.SUBTRACT)

            with BuildPart(left_side_plane, mode=Mode.SUBTRACT) as l_pins:
                for i, lp in enumerate(l_bitting):
                    pin = int(lp)
                    x = cls.VSR_2000_L_CUT_SPACINGS[i]
                    offset = cls.VSR_2000_PIN_OFFSET[pin - 1]

                    with Locations((x, 0, offset)):
                        add(fat_vsr_pin(pin))

            l_h_mirror = mirror(l_pins.part, rl_mirror_plane, mode=Mode.PRIVATE)
            l_pins_mirror = mirror(l_h_mirror, top_mirror_plane, mode=Mode.SUBTRACT)

            with BuildPart(top_side_plane, mode=Mode.SUBTRACT) as t_pins:
                for i, tp in enumerate(t_bitting):
                    if i == 2:
                        i += 1

                    pin = int(tp)
                    x = cls.VSR_2000_T_CUT_SPACINGS[i]
                    offset = cls.VSR_2000_PIN_OFFSET[pin - 1] - cls.VSR_2000_TPIN_OFFSET

                    with Locations((x, 0, offset)):
                        add(fat_vsr_pin(pin))

            t_pins_mirror = mirror(t_pins.part, top_mirror_plane, mode=Mode.SUBTRACT)

            with BuildPart(top_passive_plane, mode=Mode.SUBTRACT) as tp_pin:
                offset = cls.VSR_2000_PIN_OFFSET[0]

                with Locations((cls.VSR_2000_T_CUT_SPACINGS[2], 0, offset)):
                    add(fat_vsr_pin(1))

            t_p_h_mirror = mirror(tp_pin.part, top_mirror_plane, mode=Mode.PRIVATE)
            tp_pin_mirror = mirror(t_p_h_mirror, rl_mirror_plane, mode=Mode.SUBTRACT)

        if vsr_key.part is None:
            raise ValueError("Unable to generate key")
        return vsr_key.part


if __name__ == "__main__":
    from ocp_vscode import *

    # vsr_2000_blank = _2000.blank("1", "1")
    # export_step(vsr_2000_blank, "vsr_2000_blank.step")
    vsr_key = _2000.key("1", "1", "553534 331 24233")
    export_step(vsr_key, "vsr_key.step")
    show_all()
