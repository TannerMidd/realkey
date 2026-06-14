from abc import ABC, abstractmethod
from math import atan2, degrees
from typing import NamedTuple

from build123d import *
from build123d import Part

from realkey import geom_tools


class FollowerConfigData(NamedTuple):
    length: float
    diameter: float
    top_tag: str
    top_config: dict[str, float]
    bottom_tag: str
    bottom_config: dict[str, float]


FOLLOWER_DEFINITIONS: dict[str, FollowerConfigData | None] = {
    "Custom": None,
    "Kaba Ace": FollowerConfigData(
        50 * MM,
        9.95 * MM,
        "cross",
        {"cross_depth": 5.25 * MM, "cross_x_width": 2.25 * MM, "cross_y_width": 2.25 * MM},
        "pin_slot",
        {"pin_slot_depth": 5 * MM, "pin_slot_width": 3 * MM},
    ),
    "Keso 2000S": FollowerConfigData(
        50 * MM,
        10.95 * MM,
        "tongue",
        {"tongue_depth": 4.75 * MM, "tongue_width": 3.25 * MM},
        "pin_slot",
        {"pin_slot_depth": 5 * MM, "pin_slot_width": 3 * MM},
    ),
    "Schlage": FollowerConfigData(70 * MM, 0.495 * IN, "schlage", {}, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}),
    "Generic 10mm": FollowerConfigData(70 * MM, 10 * MM, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}, "flat_end", {}),
    "Generic 12.5mm": FollowerConfigData(70 * MM, 12.5 * MM, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}, "flat_end", {}),
    "Generic 12.7mm": FollowerConfigData(70 * MM, 12.7 * MM, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}, "flat_end", {}),
    "Generic 12.8mm": FollowerConfigData(70 * MM, 12.8 * MM, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}, "flat_end", {}),
    "Generic 14mm": FollowerConfigData(70 * MM, 14 * MM, "slot", {"slot_depth": 5.25 * MM, "slot_width": 5.5 * MM}, "flat_end", {}),
}


class FollowerEnd(ABC):
    _list: dict = {}

    def __init_subclass__(cls, **kwargs):
        """Used to have a list of all current follower ends available for generation"""
        FollowerEnd._list[cls.tag()] = cls

    @classmethod
    @abstractmethod
    def tag(cls) -> str:
        """Returns the tag of this follower end used for lookup"""

    @classmethod
    @abstractmethod
    def display_name(cls) -> str:
        """Returns the display name of this follower end"""

    @classmethod
    @abstractmethod
    def config(cls) -> dict[str, str]:
        """Returns a set of configurable options for this follower end

        Returns:
            dict[str,str]: a dict of str tags to str descriptions for different measurements for this follower end
        """

    @classmethod
    @abstractmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        """Generates the follower end

        Args:
            follower_length (float): the length of the follower being generated if needed
            follower_diameter (float): the diameter of the follower being generated if needed
            config_data (dict[str, float]): a dict containing config tag str to float values for the config

        Returns:
            tuple[Part, float]: A tuple containing the generated part and a float representing its total length
        """


class FlatEndFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "flat_end"

    @classmethod
    def display_name(cls) -> str:
        return "Flat End"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {}

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        return (None, 0)


class SlotFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "slot"

    @classmethod
    def display_name(cls) -> str:
        return "Slot"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "slot_depth": "Depth",
            "slot_width": "Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["slot_depth"]
        width = config_data["slot_width"]

        with BuildPart() as end:
            Cylinder(radius, depth)
            with BuildSketch(Plane.ZX):
                with Locations((depth / 2, 0)):
                    RectangleRounded(depth * 2, width, width / 5)
            extrude(amount=follower_diameter, both=True, mode=Mode.SUBTRACT)
        return (end.part, depth)


class VSlotFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "v_slot"

    @classmethod
    def display_name(cls) -> str:
        return "V Slot"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "v_slot_depth": "Depth",
            "v_slot_width": "Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["v_slot_depth"]
        width = config_data["v_slot_width"]

        rounded_radius = radius / 5

        with BuildPart() as end:
            Cylinder(radius, depth)
            with BuildSketch(Plane.XZ) as tt:
                with Locations((0, -depth / 2 + rounded_radius)):
                    Circle(radius=rounded_radius)
                with Locations((-width / 2 + rounded_radius, depth / 2)):
                    Circle(radius=rounded_radius)
                with Locations((width / 2 - rounded_radius, depth / 2)):
                    Circle(radius=rounded_radius)
                make_hull()
            extrude(amount=follower_diameter, both=True, mode=Mode.SUBTRACT)
        return (end.part, depth)


class TongueFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "tongue"

    @classmethod
    def display_name(cls) -> str:
        return "Tongue"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "tongue_depth": "Depth",
            "tongue_width": "Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["tongue_depth"]
        width = config_data["tongue_width"]

        with BuildPart() as end:
            Box(follower_diameter * 2, width, depth)
            add(geom_tools.Tube(radius, radius * 4, depth), mode=Mode.SUBTRACT)
        return (end.part, depth)


class CrossFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "cross"

    @classmethod
    def display_name(cls) -> str:
        return "Cross"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "cross_depth": "Depth",
            "cross_x_width": "X Width",
            "cross_y_width": "Y Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["cross_depth"]
        x_width = config_data["cross_x_width"]
        y_width = config_data["cross_y_width"]

        with BuildPart() as end:
            Box(follower_diameter + 0.5 * MM, x_width, depth)
            Box(y_width, follower_diameter, depth)
            add(geom_tools.Tube(radius, radius * 2, depth), mode=Mode.SUBTRACT)
        return (end.part, depth)


class PinSlotFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "pin_slot"

    @classmethod
    def display_name(cls) -> str:
        return "Pin Slot"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "pin_slot_depth": "Depth",
            "pin_slot_width": "Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["pin_slot_depth"]
        width = config_data["pin_slot_width"]

        with BuildPart() as end:
            Cylinder(radius, depth)
            with BuildSketch(Plane.XZ) as sv:
                with Locations((0, depth)):
                    SlotOverall(depth * 2, width, 90)
            extrude(amount=radius * 2, mode=Mode.SUBTRACT)
            extrude(sv.sketch, amount=-radius * 1 / 3, mode=Mode.SUBTRACT)
            top_edge = end.edges().group_by(Axis.Z)[-1]
            fillet(top_edge, width / 5)
        return (end.part, depth)


class HollowFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "hollow"

    @classmethod
    def display_name(cls) -> str:
        return "Hollow"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "hollow_depth": "Depth",
            "hollow_wall_thickness": "Wall Thickness",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["hollow_depth"]
        wall_thickness = config_data["hollow_wall_thickness"]

        with BuildPart() as end:
            add(geom_tools.Tube(radius - wall_thickness, radius, depth))
        return (end.part, depth)


class SlottedHollowFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "slotted_hollow"

    @classmethod
    def display_name(cls) -> str:
        return "Slotted Hollow"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {
            "slotted_hollow_depth": "Depth",
            "slotted_hollow_wall_thickness": "Wall Thickness",
            "slotted_hollow_width": "Slot Width",
        }

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        radius = follower_diameter / 2
        depth = config_data["slotted_hollow_depth"]
        wall_thickness = config_data["slotted_hollow_wall_thickness"]
        slot_width = config_data["slotted_hollow_width"]

        with BuildPart() as end:
            add(geom_tools.Tube(radius - wall_thickness, radius, depth))

            with BuildSketch(Plane.XZ) as sv:
                with Locations((0, depth)):
                    SlotOverall(depth * 2, slot_width, 90)
            extrude(amount=radius * 2, mode=Mode.SUBTRACT)
        return (end.part, depth)


class SchlageFollowerEnd(FollowerEnd):
    @classmethod
    def tag(cls) -> str:
        return "schlage"

    @classmethod
    def display_name(cls) -> str:
        return "Schlage"

    @classmethod
    def config(cls) -> dict[str, str]:
        return {}

    @classmethod
    def generate(cls, follower_length: float, follower_diameter: float, config_data: dict[str, float]) -> tuple[Part | None, float]:
        placement_radius = 5.5 * MM
        inner_radius = 3 * MM
        pin_radius = 0.75 * MM
        outer_radius = placement_radius + pin_radius
        ridge_depth = 1.25 * MM
        total_depth = 5.25 * MM
        lobe_count = 14

        with BuildPart() as end:
            Cylinder(outer_radius, total_depth)
            Cylinder(inner_radius, total_depth, mode=Mode.SUBTRACT)

            with BuildSketch(Plane.XY.offset(total_depth / 2 - ridge_depth)):
                Circle(radius=outer_radius)
                Circle(radius=placement_radius, mode=Mode.SUBTRACT)
                with PolarLocations(placement_radius, lobe_count):
                    Circle(radius=pin_radius, mode=Mode.SUBTRACT)
            extrude(amount=ridge_depth, mode=Mode.SUBTRACT)
        return (end.part, total_depth)


class Follower:
    @classmethod
    def generate(cls, config_data: FollowerConfigData) -> Part:
        print(f"{config_data}")
        top_cls: FollowerEnd = FollowerEnd._list[config_data.top_tag]
        bottom_cls: FollowerEnd = FollowerEnd._list[config_data.bottom_tag]

        top_part, top_length = top_cls.generate(config_data.length, config_data.diameter, config_data.top_config)
        bottom_part, bottom_length = bottom_cls.generate(config_data.length, config_data.diameter, config_data.bottom_config)

        remaining_length = config_data.length - top_length - bottom_length
        radius = config_data.diameter / 2

        end_offset = remaining_length / 2
        print(end_offset)
        if top_part is not None:
            top_part.position += (0, 0, end_offset + top_length / 2)
            if config_data.top_config:
                top_part = top_part.rotate(Axis.Z, config_data.top_config["rotation"])
        if bottom_part is not None:
            bottom_part = bottom_part.rotate(Axis.X, 180)
            bottom_part.position -= (0, 0, end_offset + bottom_length / 2)
            if config_data.bottom_config:
                bottom_part = bottom_part.rotate(Axis.Z, config_data.bottom_config["rotation"])

        chamfer_amount = config_data.diameter / 14
        with BuildPart() as follower:
            Cylinder(radius=radius, height=remaining_length)
            if top_part is not None:
                add(top_part)
                with BuildPart(mode=Mode.SUBTRACT) as top_chamfer:
                    chamfer_amount *= 1.4
                    with Locations((0, 0, end_offset + top_length)):
                        add(geom_tools.Tube(radius - chamfer_amount / 2, radius + chamfer_amount * 2, chamfer_amount * 2 + 0.001))
                    bottom_edges = top_chamfer.edges().group_by(Axis.Z)[0].sort_by(Axis.X)[-1]
                    chamfer(bottom_edges, chamfer_amount)
            else:
                top_edge = follower.edges().sort_by(Axis.Z)[-1]
                chamfer(top_edge, chamfer_amount)
            if bottom_part is not None:
                add(bottom_part)
                with BuildPart(mode=Mode.SUBTRACT) as bottom_chamfer:
                    chamfer_amount *= 1.4
                    with Locations((0, 0, -end_offset - bottom_length)):
                        add(geom_tools.Tube(radius - chamfer_amount / 2, radius + chamfer_amount * 2, chamfer_amount * 2 + 0.001))
                    top_edges = bottom_chamfer.edges().group_by(Axis.Z)[-1].sort_by(Axis.X)[-1]
                    chamfer(top_edges, chamfer_amount)
            else:
                bottom_edge = follower.edges().sort_by(Axis.Z)[0]
                chamfer(bottom_edge, chamfer_amount)
        if follower.part is None:
            raise ValueError("Unable to generate follower")
        return follower.part


if __name__ == "__main__":
    from ocp_vscode import *

    follower = Follower.generate(FollowerConfigData(70, 10, "v_slot", {"v_slot_depth": 2, "v_slot_width": 2.5}, "flat_end", {}))
