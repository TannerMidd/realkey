from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


if importlib.util.find_spec("build123d") is None:
    build123d = types.ModuleType("build123d")

    class Part:
        def __init__(self, value=None):
            self.value = value

    class Face:
        pass

    class Wire:
        pass

    class Sketch:
        pass

    class VectorLike:
        pass

    class ShapeList(list):
        @classmethod
        def __class_getitem__(cls, item):
            return cls

    class Vector:
        def __init__(self, *components):
            if len(components) == 1 and not isinstance(components[0], (int, float)):
                components = tuple(components[0])
            self.X, self.Y, self.Z = components

    class Axis:
        X = "x"
        Y = "y"
        Z = "z"

    class Mode:
        PRIVATE = "private"
        SUBTRACT = "subtract"

    exported = {
        "MM": 1.0,
        "IN": 25.4,
        "THOU": 0.0254,
        "Part": Part,
        "Face": Face,
        "Wire": Wire,
        "Sketch": Sketch,
        "VectorLike": VectorLike,
        "ShapeList": ShapeList,
        "Vector": Vector,
        "Axis": Axis,
        "Mode": Mode,
    }
    for name, value in exported.items():
        setattr(build123d, name, value)
    build123d.__all__ = list(exported)
    sys.modules["build123d"] = build123d
