from build123d import *

from realkey.Common import key, resource_fetcher, svgtools

class Desmo(key.Key):
    DESMO_KEY_BLADE_HEIGHT = 9.5 * MM
    DESMO_KEY_WIDTH = 3 * MM
    DESMO_KEY_X_DATUM = 27.725 * MM
    DESMO_KEY_Y_DATUM = 22 * MM
    DESMO_KEY_TOP = 16.75 * MM

    DESMO_CUT_SPACINGS = [i * 3.5 * MM + 4.5 * MM for i in range(10)]
    DESMO_CUT_DEPTHS = [i * -0.5 * MM + 3.5 * MM for i in range(6)]

    DESMO_PIN_DIAMETER = 3 * MM
    DESMO_PIN_HEIGHT = 1 * MM
    DESMO_TRACK_TOLERANCE = 0.75 * MM

    @classmethod
    def name(cls) -> str:
        return "assa_desmo"

    @classmethod
    def display_name(cls) -> str:
        return "ASSA Desmo"

    @classmethod
    def profiles(cls) -> dict[str, str]:
        return {"6pin": "6-Pin", "8pin": "8-Pin", "10pin": "10-Pin"}

    @classmethod
    def keyways(cls) -> dict[str, str]:
        return {"desmo": "Desmo"}

    @classmethod
    def basic_bitting_definition(cls) -> str:
        return (
            "Cuts proceed from right side bow to tip, then left side bow to tip, with 1 being the maximum lift and 6 being the minimum lift<br><br>"
            "<i>E.g. 145362 represents 145 on the right, 362 on the left</i>"
        )

    @classmethod
    def advanced_bitting_definition(cls) -> str | None:
        return None

    @classmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        if not bitting.isnumeric():
            raise ValueError("Only numeric cuts are allowed")
        if profile == "6pin" and len(bitting) > 6:
            raise ValueError("6 pin profile only supports a maximum of 6 cuts")
        if profile == "8pin" and len(bitting) > 8:
            raise ValueError("8 pin profile only supports a maximum of 8 cuts")
        if profile == "10pin" and len(bitting) > 10:
            raise ValueError("10 pin profile only supports a maximum of 10 cuts")
        if len(bitting) % 2 != 0:
            raise ValueError("Number of cuts must be even")
        for cut in bitting:
            if int(cut) < 1 or int(cut) > 6:
                raise ValueError("Cut depths must be from 1 to 6")

    @classmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        if profile not in cls.profiles():
            raise ValueError("Invalid profile specified!")
        if keyway not in cls.keyways():
            raise ValueError("Invalid keyway specified!")

        if not resource_fetcher.pre_fetch_resource("resources/ASSA/Desmo.svg"):
            raise ValueError("Unable to load ASSA Desmo SVG")
        assa_svg = import_svg("resources/ASSA/Desmo.svg", flip_y=False, label_by="inkscape:label")
        profile_face = svgtools.get_starting_at_origin(assa_svg, "#profile_desmo_" + profile)
        keyway_face = svgtools.get_centered_around_origin(assa_svg, "#keyway_" + keyway)
        keyway_face = keyway_face.rotate(Axis.Z, -90)

        with BuildPart() as desmo_blank:
            with BuildSketch():
                add(profile_face)
            extrude(amount=cls.DESMO_KEY_WIDTH)

            with BuildSketch(Plane.YZ.offset(cls.DESMO_KEY_X_DATUM)):
                with Locations((cls.DESMO_KEY_Y_DATUM - cls.DESMO_KEY_BLADE_HEIGHT / 2, cls.DESMO_KEY_WIDTH / 2)):
                    Rectangle(cls.DESMO_KEY_BLADE_HEIGHT + 5.0 * MM, cls.DESMO_KEY_WIDTH)
                    add(keyway_face, mode=Mode.SUBTRACT)
            extrude(amount=50 * MM, mode=Mode.SUBTRACT)
        return Part(desmo_blank.part)

    @classmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        cls.validate_bitting(profile, keyway, bitting)

        desmo_blank = cls.blank(profile, keyway)

        right_track = [(0.0, 0.0)] * 18
        left_track = [(0.0, 0.0)] * 18

        right_cuts = bitting[: int(len(bitting) / 2)]
        left_cuts = bitting[int(len(bitting) / 2) :]

        def calculate_tracks(track: list[tuple[float, float]], cuts: str):
            for i, cut in enumerate(cuts):
                depth_index = int(cut) - 1
                # We must skip past the key retention spot located at index 2
                cut_index = i if i < 2 else i + 1

                cut_x = cls.DESMO_CUT_SPACINGS[cut_index]
                cut_x += cls.DESMO_KEY_X_DATUM

                cut_y = cls.DESMO_KEY_Y_DATUM
                cut_y -= cls.DESMO_CUT_DEPTHS[depth_index] + cls.DESMO_PIN_HEIGHT / 2  # Cuts are "centered" in the track, measurements were taken to the bottom of track

                # The cut height for the notch appears to match the next cut on ASSA cut keys
                if i == 2:
                    track[4] = (cls.DESMO_KEY_X_DATUM + cls.DESMO_CUT_SPACINGS[2] - cls.DESMO_PIN_DIAMETER / 2, cut_y)
                    track[5] = (cls.DESMO_KEY_X_DATUM + cls.DESMO_CUT_SPACINGS[2] + cls.DESMO_PIN_DIAMETER / 2, cut_y)

                track[cut_index * 2] = (cut_x - cls.DESMO_PIN_DIAMETER / 2, cut_y)
                track[cut_index * 2 + 1] = (cut_x + cls.DESMO_PIN_DIAMETER / 2, cut_y)

                # Extend the cut out to the tip.. Different pin count Desmos do this differently, but this is practical
                if i == len(cuts) - 1:
                    while cut_index < 8:
                        cut_index += 1
                        track[cut_index * 2] = (cls.DESMO_CUT_SPACINGS[cut_index] + cls.DESMO_KEY_X_DATUM - cls.DESMO_PIN_DIAMETER / 2, cut_y)
                        track[cut_index * 2 + 1] = (cls.DESMO_CUT_SPACINGS[cut_index] + cls.DESMO_KEY_X_DATUM + cls.DESMO_PIN_DIAMETER / 2, cut_y)

        calculate_tracks(right_track, right_cuts)
        calculate_tracks(left_track, left_cuts)

        def build_track(track_points: list[tuple[float, float]], z_height: float) -> Part:
            with BuildPart() as track:
                with BuildPart(Plane.XZ.offset(-track_points[0][1])):
                    with Locations((track_points[0][0], z_height)):
                        Cylinder(cls.DESMO_PIN_DIAMETER / 2 + cls.DESMO_TRACK_TOLERANCE / 2, cls.DESMO_PIN_HEIGHT)

                for v_0, v_1 in zip(track_points[0:-1], track_points[1:]):
                    if v_0[1] != v_1[1]:
                        # Angle cut

                        # Slope used for adjustments
                        s = (v_1[1] - v_0[1]) / (v_1[0] - v_0[0])
                        ramp_up = s < 0

                        # On a real key, this is just a sweep of the pin across the track
                        # On this design, it uses maximal fitting ramps so that a 3D printed key works too
                        # This can make the ramps look quite gnarly, but it generates working keys for all bittings

                        v0b = [0, 0, z_height]  # current pin bottom center
                        v0t = [0, 0, z_height]  # current pin top center
                        v1b = [0, 0, z_height]  # next pin bottom center
                        v1t = [0, 0, z_height]  # next pin top center

                        if ramp_up:
                            v0b[0] = v_0[0] - cls.DESMO_PIN_DIAMETER / 2
                            v0b[1] = v_0[1] + cls.DESMO_PIN_HEIGHT / 2
                            v0t[0] = v_0[0]
                            v0t[1] = v_0[1] - cls.DESMO_PIN_HEIGHT / 2
                            v1b[0] = v_1[0]
                            v1b[1] = v_1[1] + cls.DESMO_PIN_HEIGHT / 2
                            v1t[0] = v_1[0] + cls.DESMO_PIN_DIAMETER / 2
                            v1t[1] = v_1[1] - cls.DESMO_PIN_HEIGHT / 2

                            b_slope = (v1b[1] - v0b[1]) / (v1b[0] - v0b[0])
                            v1b[0] -= (cls.DESMO_PIN_HEIGHT / 2) / b_slope
                            v1b[1] -= cls.DESMO_PIN_HEIGHT / 2
                            v0t[0] += (cls.DESMO_PIN_HEIGHT / 2) / b_slope
                            v0t[1] += cls.DESMO_PIN_HEIGHT / 2
                        else:
                            v0b[0] = v_0[0]
                            v0b[1] = v_0[1] + cls.DESMO_PIN_HEIGHT / 2
                            v0t[0] = v_0[0] - cls.DESMO_PIN_DIAMETER / 2
                            v0t[1] = v_0[1] - cls.DESMO_PIN_HEIGHT / 2
                            v1b[0] = v_1[0] + cls.DESMO_PIN_DIAMETER / 2
                            v1b[1] = v_1[1] + cls.DESMO_PIN_HEIGHT / 2
                            v1t[0] = v_1[0]
                            v1t[1] = v_1[1] - cls.DESMO_PIN_HEIGHT / 2

                            b_slope = (v1b[1] - v0b[1]) / (v1b[0] - v0b[0])
                            v0b[0] -= (cls.DESMO_PIN_HEIGHT / 2) / b_slope
                            v0b[1] -= cls.DESMO_PIN_HEIGHT / 2
                            v1t[0] += (cls.DESMO_PIN_HEIGHT / 2) / b_slope
                            v1t[1] += cls.DESMO_PIN_HEIGHT / 2

                        with BuildSketch(Plane.XZ.offset(-v0b[1])):
                            with Locations((v0b[0], z_height)):
                                Circle(cls.DESMO_PIN_DIAMETER / 2 + cls.DESMO_TRACK_TOLERANCE / 2)
                        with BuildLine() as b:
                            Line(Vertex(v0b), Vertex(v1b))
                        sweep()
                        with BuildSketch(Plane.XZ.offset(-v0t[1])):
                            with Locations((v0t[0], z_height)):
                                Circle(cls.DESMO_PIN_DIAMETER / 2 + cls.DESMO_TRACK_TOLERANCE / 2)
                        with BuildLine() as t:
                            Line(Vertex(v0t), Vertex(v1t))
                        sweep()
                    else:
                        # Straight cut
                        with BuildSketch(Plane.YZ.offset(v_0[0])):
                            with Locations((v_0[1], z_height)):
                                Rectangle(cls.DESMO_PIN_HEIGHT, cls.DESMO_PIN_DIAMETER + cls.DESMO_TRACK_TOLERANCE)
                        with BuildLine():
                            Line(v_0, v_1)
                        sweep()
            return Part(track.part)

        with BuildPart() as desmo_key:
            add(desmo_blank)
            add(build_track(right_track, -cls.DESMO_PIN_DIAMETER / 4), mode=Mode.SUBTRACT)
            add(build_track(left_track, cls.DESMO_KEY_WIDTH + cls.DESMO_PIN_DIAMETER / 4), mode=Mode.SUBTRACT)

            # The tip cut on Desmo follows the tip and goes all the way to the track equally
            tip_x = 55 * MM
            if profile == "8pin":
                tip_x = 51.5 * MM
            if profile == "6pin":
                tip_x = 48 * MM

            tip_edges = desmo_blank.edges().filter_by_position(Axis.X, tip_x, 100)
            tip_edges = tip_edges.group_by(Axis.Z)[0] + tip_edges.group_by(Axis.Z)[-1]

            # We cut the tip to ramp into the last track smoothly
            with BuildPart(mode=Mode.SUBTRACT):
                for tip_edge in tip_edges:
                    v_0 = tip_edge.vertices()[0]
                    v_1 = tip_edge.vertices()[1]

                    v_0n = [float(v_0.X), float(v_0.Y), float(v_0.Z)]
                    v_1n = [float(v_1.X), float(v_1.Y), float(v_1.Z)]

                    is_left = True if v_0.Z > cls.DESMO_KEY_WIDTH else False
                    z_off = (cls.DESMO_KEY_WIDTH / 8) if is_left else -(cls.DESMO_KEY_WIDTH / 8)

                    if v_0n[1] > cls.DESMO_KEY_TOP and v_0n[1] < cls.DESMO_KEY_Y_DATUM:
                        v_0n[1] = left_track[-1][1] if is_left else right_track[-1][1]
                        v_1n[0] += cls.DESMO_PIN_DIAMETER

                    if v_1n[1] > cls.DESMO_KEY_TOP and v_1n[1] < cls.DESMO_KEY_Y_DATUM:
                        v_1n[1] = left_track[-1][1] if is_left else right_track[-1][1]
                        v_0n[0] += cls.DESMO_PIN_DIAMETER

                    with BuildSketch(Plane.XZ.offset(-v_0n[1])):
                        with Locations((v_0n[0], v_0n[2] + z_off)):
                            Ellipse(x_radius=cls.DESMO_PIN_DIAMETER * 3 / 2, y_radius=cls.DESMO_PIN_DIAMETER / 2)
                    with BuildLine():
                        Line(Vertex(v_0n), Vertex(v_1n))
                    sweep()

            with BuildLine(Plane.XY.offset(cls.DESMO_KEY_WIDTH)):
                Polyline(left_track)
            with BuildLine(Plane.XY):
                Polyline(right_track)
        return Part(desmo_key.part)


if __name__ == "__main__":
    from ocp_vscode import *

    # desmo_blank = Desmo.blank("8pin", "desmo")
    desmo_key = Desmo.key("8pin", "desmo", "24421322")
    # desmo_key = Desmo.key("6pin", "desmo", "632145")
    # export_step(desmo_key, "desmo_key.step")
    # export_step(blank, "desmo_blank.step")
    show_all()
