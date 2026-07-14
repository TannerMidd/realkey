from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from realkey import follower, geom_tools, key, key_cutters, sargentandgreenleaf, schlage, vsr


class _Context:
    def __init__(self, *, part=None, sketch=None):
        self.part = part
        self.sketch = sketch

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_key_registry_rejects_conflicting_duplicate_tag():
    tag = "_test_duplicate_key"
    key.Key._list.pop(tag, None)

    class RegisteredKey(key.Key):
        @classmethod
        def tag(cls):
            return tag

        @classmethod
        def display_name(cls):
            return "Registered"

        @classmethod
        def profiles(cls):
            return {"": {"profile": "Profile"}}

        @classmethod
        def keyways(cls):
            return {"": {"keyway": "Keyway"}}

        @classmethod
        def basic_bitting_definition(cls):
            return ""

        @classmethod
        def advanced_bitting_definition(cls):
            return None

        @classmethod
        def validate_bitting(cls, profile, keyway, bitting):
            return None

        @classmethod
        def blank(cls, profile, keyway):
            return None

        @classmethod
        def key(cls, profile, keyway, bitting):
            return None

    try:
        with pytest.raises(ValueError, match="already registered"):

            class DuplicateKey(RegisteredKey):
                pass

        assert key.Key._list[tag] is RegisteredKey
    finally:
        key.Key._list.pop(tag, None)


def test_follower_registry_rejects_conflicting_duplicate_tag():
    tag = "_test_duplicate_follower_end"
    follower.FollowerEnd._list.pop(tag, None)

    class RegisteredEnd(follower.FollowerEnd):
        @classmethod
        def tag(cls):
            return tag

        @classmethod
        def display_name(cls):
            return "Registered"

        @classmethod
        def config(cls):
            return {}

        @classmethod
        def generate(cls, follower_length, follower_diameter, config_data):
            return None, 0.0

    try:
        with pytest.raises(ValueError, match="already registered"):

            class DuplicateEnd(RegisteredEnd):
                pass

        assert follower.FollowerEnd._list[tag] is RegisteredEnd
    finally:
        follower.FollowerEnd._list.pop(tag, None)


def test_geom_tools_max_uses_vector_y_coordinate():
    class Shape:
        def __init__(self, x, y, z):
            self.maximum = SimpleNamespace(X=x, Y=y, Z=z)

        def bounding_box(self):
            return SimpleNamespace(max=self.maximum)

    maximum = geom_tools.max([Shape(1, 2, 3), Shape(4, 8, 6)])

    assert (maximum.X, maximum.Y, maximum.Z) == (4, 8, 6)


def test_angled_cutter_preserves_angle_when_width_is_capped(monkeypatch):
    captured = []
    sketch = object()
    monkeypatch.setattr(key_cutters, "BuildSketch", lambda: _Context(sketch=sketch), raising=False)
    monkeypatch.setattr(key_cutters, "BuildLine", lambda: _Context(), raising=False)
    monkeypatch.setattr(key_cutters, "Polyline", lambda *points: captured.append(points), raising=False)
    monkeypatch.setattr(key_cutters, "make_face", lambda: None, raising=False)

    result = key_cutters.angled_cutter([(0.0, 10.0)], 2.0, 0.0, 4.0, 60.0)

    capped_dx = 1.0
    expected_dy = capped_dx * math.tan(math.radians(30.0))
    assert captured[0][2][1] == pytest.approx(10.0 + expected_dy)
    assert result is sketch


def test_all_known_follower_presets_pass_core_validation():
    for name, config in follower.FOLLOWER_DEFINITIONS.items():
        if config is not None:
            config.validate()


@pytest.mark.parametrize(
    "config, message",
    [
        (
            follower.FollowerConfigData(math.nan, 10.0, "flat_end", {}, "flat_end", {}),
            "length must be finite",
        ),
        (
            follower.FollowerConfigData(50.0, math.inf, "flat_end", {}, "flat_end", {}),
            "diameter must be finite",
        ),
        (
            follower.FollowerConfigData(0.0, 10.0, "flat_end", {}, "flat_end", {}),
            "length must be between",
        ),
        (
            follower.FollowerConfigData(50.0, 10.0, "missing", {}, "flat_end", {}),
            "Unknown top follower end",
        ),
        (
            follower.FollowerConfigData(20.0, 10.0, "slot", {"slot_depth": 3.0}, "flat_end", {}),
            "missing: slot_width",
        ),
        (
            follower.FollowerConfigData(20.0, 10.0, "slot", {"slot_depth": 3.0, "slot_width": 11.0}, "flat_end", {}),
            "cannot exceed the follower diameter",
        ),
        (
            follower.FollowerConfigData(
                20.0,
                10.0,
                "hollow",
                {"hollow_depth": 3.0, "hollow_wall_thickness": 5.0},
                "flat_end",
                {},
            ),
            "must be less than the follower radius",
        ),
        (
            follower.FollowerConfigData(
                20.0,
                10.0,
                "slot",
                {"slot_depth": 10.0, "slot_width": 3.0},
                "slot",
                {"slot_depth": 10.0, "slot_width": 3.0},
            ),
            "Combined follower end depths",
        ),
    ],
)
def test_follower_config_rejects_invalid_cad_inputs(config, message):
    with pytest.raises(ValueError, match=message):
        config.validate()


def test_follower_generate_validates_before_cad_work():
    config = follower.FollowerConfigData(math.nan, 10.0, "flat_end", {}, "flat_end", {})

    with pytest.raises(ValueError, match="length must be finite"):
        follower.Follower.generate(config)


def test_follower_joint_chamfers_do_not_compound(monkeypatch):
    chamfer_amounts = []

    class Position:
        def __iadd__(self, value):
            return self

        def __isub__(self, value):
            return self

    class FakePart:
        def __init__(self):
            self.position = Position()

        def rotate(self, axis, amount):
            return self

    class EdgeGroup:
        def sort_by(self, axis):
            return [object()]

    class BuildPartContext(_Context):
        def __init__(self):
            super().__init__(part=FakePart())

        def edges(self):
            return SimpleNamespace(group_by=lambda axis: [EdgeGroup()])

    class TestEnd:
        @classmethod
        def config(cls):
            return {}

        @classmethod
        def generate(cls, follower_length, follower_diameter, config_data):
            return FakePart(), 2.0

    monkeypatch.setitem(follower.FollowerEnd._list, "_test_top", TestEnd)
    monkeypatch.setitem(follower.FollowerEnd._list, "_test_bottom", TestEnd)
    monkeypatch.setattr(follower, "BuildPart", lambda *args, **kwargs: BuildPartContext(), raising=False)
    monkeypatch.setattr(follower, "Locations", lambda *args, **kwargs: _Context(), raising=False)
    monkeypatch.setattr(follower, "Cylinder", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(follower, "add", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(follower, "chamfer", lambda edge, amount: chamfer_amounts.append(amount), raising=False)
    monkeypatch.setattr(follower, "Axis", SimpleNamespace(X="x", Z="z"), raising=False)
    monkeypatch.setattr(follower, "Mode", SimpleNamespace(SUBTRACT="subtract"), raising=False)
    monkeypatch.setattr(follower.geom_tools, "Tube", lambda *args, **kwargs: object())

    follower.Follower.generate(
        follower.FollowerConfigData(20.0, 10.0, "_test_top", {}, "_test_bottom", {})
    )

    assert chamfer_amounts == pytest.approx([1.0, 1.0])


def test_vsr_enforces_documented_row_cut_constraints():
    vsr._2000.validate_bitting("1", "1", "553534 331 24233")

    invalid_bittings = [
        "153534 331 24233",
        "553534 321 24233",
        "553534 333 24233",
        "553534 331 14233",
        "553534 331",
    ]
    for bitting in invalid_bittings:
        with pytest.raises(ValueError):
            vsr._2000.validate_bitting("1", "1", bitting)


def test_sg_profiles_require_their_declared_cut_count():
    for profile, cut_count in sargentandgreenleaf.SGSDB.SG_PROFILE_CUT_COUNTS.items():
        sargentandgreenleaf.SGSDB.validate_bitting(profile, "lever", "0" * cut_count)
        with pytest.raises(ValueError, match=f"requires exactly {cut_count} cuts"):
            sargentandgreenleaf.SGSDB.validate_bitting(profile, "lever", "0" * (cut_count + 1))


def test_sg_grouped_profile_errors_are_domain_errors_not_key_errors():
    with pytest.raises(ValueError, match="S&G 87H requires exactly 5 cuts"):
        sargentandgreenleaf.SGSDB.validate_bitting("87h", "lever", "000000")


def test_primus_parser_normalizes_whitespace_and_rejects_extra_rows():
    assert schlage.EverestPrimus._split_bitting("326163  \t 23645") == ("326163", "23645")
    schlage.EverestPrimus.validate_bitting("ep_6pin", "c124", "326163  \t 23645")

    with pytest.raises(ValueError, match="main and sidebar"):
        schlage.EverestPrimus.validate_bitting("ep_6pin", "c124", "326163 23645 1")


def test_primus_generation_uses_the_same_whitespace_parser(monkeypatch):
    generated_part = object()
    monkeypatch.setattr(
        schlage.EverestPrimus,
        "blank",
        classmethod(lambda cls, profile, keyway: object()),
    )
    monkeypatch.setattr(schlage, "BuildPart", lambda *args, **kwargs: _Context(part=generated_part), raising=False)
    monkeypatch.setattr(schlage, "BuildSketch", lambda *args, **kwargs: _Context(), raising=False)
    monkeypatch.setattr(schlage, "add", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(schlage, "extrude", lambda *args, **kwargs: None, raising=False)
    monkeypatch.setattr(schlage, "Part", lambda value: value)
    monkeypatch.setattr(schlage, "Mode", SimpleNamespace(SUBTRACT="subtract"), raising=False)
    monkeypatch.setattr(schlage.key_cutters, "smooth_angled_cutter", lambda *args, **kwargs: object())
    monkeypatch.setattr(schlage.key_cutters, "angled_cutter", lambda *args, **kwargs: object())

    result = schlage.EverestPrimus.key("ep_6pin", "c124", "326163   \t23645")

    assert result is generated_part
