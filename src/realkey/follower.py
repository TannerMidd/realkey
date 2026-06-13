from abc import ABC, abstractmethod
from typing import NamedTuple

from build123d import *
from build123d import Part


class FollowerConfigData(NamedTuple):
    length: float
    diameter: float
    top_tag: str
    top_config: dict[str, float]
    bottom_tag: str
    bottom_config: dict[str, float]


FOLLOWER_DEFINITIONS: dict[str, FollowerConfigData | None] = {
    "Custom": None,
    "Generic 10mm": FollowerConfigData(70 * MM, 10 * MM, "flat_end", {}, "flat_end", {}),
    "Generic 12.5mm": FollowerConfigData(70 * MM, 12.5 * MM, "flat_end", {}, "flat_end", {}),
    "Generic 12.8mm": FollowerConfigData(70 * MM, 12.8 * MM, "flat_end", {}, "flat_end", {}),
    "Generic 14mm": FollowerConfigData(70 * MM, 14 * MM, "flat_end", {}, "flat_end", {}),
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
    def generate(cls, config_data: dict[str, float]) -> tuple[Part | None, float]:
        """Generates the follower end

        Args:
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
    def generate(cls, config_data: dict[str, float]) -> tuple[Part | None, float]:
        return (None, 0)


class Follower:
    @classmethod
    def generate(cls, config_data: FollowerConfigData) -> Part:
        print(f"{config_data}")
        top_cls: FollowerEnd = FollowerEnd._list[config_data.top_tag]
        bottom_cls: FollowerEnd = FollowerEnd._list[config_data.bottom_tag]

        top_part, top_length = top_cls.generate(config_data.top_config)
        bottom_part, bottom_length = bottom_cls.generate(config_data.bottom_config)

        remaining_length = config_data.length - top_length - bottom_length
        radius = config_data.diameter / 2

        end_offset = remaining_length / 2
        if top_part is not None:
            top_part.position += (0, 0, end_offset)
        if bottom_part is not None:
            bottom_part = bottom_part.rotate(Axis.X, 180)
            bottom_part.position -= (0, 0, end_offset)

        CHAMFER_AMOUNT = 1*MM
        with BuildPart() as follower:
            Cylinder(radius=radius, height=remaining_length)
            if top_part is not None:
                add(top_part)
            if bottom_part is not None:
                add(bottom_part)

            with BuildPart(mode=Mode.SUBTRACT) as top_chamfer:
                with Locations((0, 0, end_offset)):
                    Cylinder(radius + CHAMFER_AMOUNT * 2, CHAMFER_AMOUNT*2)
                    Cylinder(radius - CHAMFER_AMOUNT / 2, CHAMFER_AMOUNT*2, mode=Mode.SUBTRACT)
                bottom_edges = top_chamfer.edges(Select.LAST).sort_by(Axis.Z)[0]
                chamfer(bottom_edges, CHAMFER_AMOUNT)

            with BuildPart(mode=Mode.SUBTRACT) as bottom_chamfer:
                with Locations((0, 0, -end_offset)):
                    Cylinder(radius + CHAMFER_AMOUNT * 2, CHAMFER_AMOUNT*2)
                    Cylinder(radius - CHAMFER_AMOUNT / 2, CHAMFER_AMOUNT*2, mode=Mode.SUBTRACT)
                top_edges = bottom_chamfer.edges(Select.LAST).sort_by(Axis.Z)[-1]
                chamfer(top_edges, CHAMFER_AMOUNT)

        if follower.part is None:
            raise ValueError("Unable to generate follower")
        return follower.part

if __name__ == "__main__":
    from ocp_vscode import *

    follower = Follower.generate(FollowerConfigData(70,10,"flat_end",{},"flat_end",{}))
    show_all()
