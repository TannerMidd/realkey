import micropip


# Keeps build123d from pulling the wrong ones
print("[BG] Mocking cadquery-ocp-novtk and lib3mf")
micropip.add_mock_package("cadquery-ocp-novtk", "7.9.3.1", modules={})
micropip.add_mock_package("lib3mf", "2.5.0", modules={})

# Install the required packages.
print("[BG] Installing packages - cadquery-ocp-novtk")
await micropip.install("cadquery-ocp-novtk-OCP.wasm==7.9.3.1.post202606201016", keep_going=True)
print("[BG] Installing packages - lib3mf")
await micropip.install("lib3mf-OCP.wasm==2.5.0.post202606200901", keep_going=True)
print("[BG] Installing packages - cadquery_ocp_proxy")
await micropip.install("cadquery_ocp_proxy==7.9.3.1.1", keep_going=True)
print("[BG] Installing packages - build123d")
await micropip.install("build123d==0.11.0", keep_going=True)
print("[BG] Installing packages - typing-extensions")
await micropip.install("typing-extensions==4.15.0", keep_going=True)
print("[BG] Packages installed")

import base64
import io
import math
import os
import uuid
from typing import Any

from build123d import *
from realkey import key, resource_fetcher, assa, dom, miwa, opnus, paclock, sargentandgreenleaf, schlage, vsr, follower


def _encode_file(path: str) -> str:
    with open(path, "rb") as export_file:
        return base64.b64encode(export_file.read()).decode("ascii")


def _coordinate(vector: Any, name: str, index: int) -> float:
    value = getattr(vector, name, None)
    if value is None:
        value = tuple(vector)[index]
    return float(value)


def _measure(part: Part) -> dict[str, float | None]:
    """Return cheap, deterministic measurements used by the foreground audit."""
    size = part.bounding_box().size
    measurements: dict[str, float | None] = {
        "size_x_mm": _coordinate(size, "X", 0),
        "size_y_mm": _coordinate(size, "Y", 1),
        "size_z_mm": _coordinate(size, "Z", 2),
        # Generic BRep minimum-wall analysis is intentionally not guessed. A
        # future worker pass can populate this without changing the protocol.
        "minimum_feature_mm": None,
        "minimum_wall_mm": None,
    }
    if not all(math.isfinite(value) and value >= 0 for value in measurements.values() if value is not None):
        raise ValueError("Generated model has invalid physical measurements")
    return measurements


def _encode_3mf(part: Part, part_number: str) -> tuple[str | None, str | None]:
    """Create a unit-aware additive-manufacturing export when lib3mf is ready."""
    try:
        stream = io.BytesIO()
        mesher = Mesher()
        mesher.add_shape(part, part_number=part_number)
        mesher.write_stream(stream, "3mf")
        return base64.b64encode(stream.getvalue()).decode("ascii"), None
    except Exception as error:
        # STL and STEP remain useful if a browser/lib3mf combination cannot
        # produce 3MF; surface the degraded export instead of losing the job.
        return None, f"3MF export unavailable: {error}"


def shared_generate(part: Part, part_number: str = "realkey-model") -> dict[str, Any]:
    export_id = uuid.uuid4().hex
    stl_path = f"realkey-{export_id}.stl"
    step_path = f"realkey-{export_id}.step"

    try:
        export_stl(part, stl_path)
        export_step(part, step_path)

        returns: dict[str, Any] = {
            "stl": _encode_file(stl_path),
            "step": _encode_file(step_path),
            "metrics": _measure(part),
        }
        three_mf, warning = _encode_3mf(part, part_number)
        if three_mf is not None:
            returns["3mf"] = three_mf
        if warning is not None:
            returns["warnings"] = [warning]
        return returns
    finally:
        for path in (stl_path, step_path):
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def generate_key(key_tag: str, profile: str, keyway: str, bitting: str) -> dict[str, Any]:
    try:
        if key_tag not in key.Key._list:
            return {"error": "Unknown key type", "error_code": "unknown_key"}
        key_class: key.Key = key.Key._list[key_tag]
        generated_key: Part | None = None
        if len(bitting) == 0:
            generated_key = key_class.blank(profile, keyway)
        else:
            generated_key = key_class.key(profile, keyway, bitting)
        if generated_key is None:
            return {"error": "No key or blank generated", "error_code": "empty_model"}

        return shared_generate(generated_key, f"{key_tag}-{profile}-{keyway}")
    except Exception as e:
        return {"error": str(e), "error_code": "key_generation_failed"}


def generate_key_art(key_tag: str, profile: str, keyway: str, bitting: str) -> dict[str, str]:
    try:
        if key_tag not in key.Key._list:
            return {"error": "Unknown key type"}
        key_class: key.Key = key.Key._list[key_tag]
        generated_key: Part | None = None
        if len(bitting) == 0:
            generated_key = key_class.blank(profile, keyway)
        else:
            generated_key = key_class.key(profile, keyway, bitting)
        if generated_key is None:
            return {"error": "No key or blank generated!"}

        view_port_origin = (100, 50, 80)
        visible, hidden = generated_key.project_to_viewport(view_port_origin)
        max_dimension = max(*Compound(children=visible + hidden).bounding_box().size)
        exporter = ExportSVG(scale=100 / max_dimension)
        exporter.add_layer("Visible")
        exporter.add_layer("Hidden", line_color=(99, 99, 99), line_type=LineType.ISO_DOT)
        exporter.add_shape(visible, layer="Visible")
        exporter.add_shape(hidden, layer="Hidden")
        svg_path = f"realkey-{uuid.uuid4().hex}.svg"
        try:
            exporter.write(svg_path)
            return {"svg": _encode_file(svg_path)}
        finally:
            try:
                os.remove(svg_path)
            except FileNotFoundError:
                pass
    except Exception as e:
        return {"error": f"{e}"}


def _plain_dict(value: Any) -> dict[str, float]:
    if hasattr(value, "to_py"):
        value = value.to_py()
    return {str(name): float(number) for name, number in dict(value).items()}


def generate_follower(length: float, diameter: float, top_tag: str, top_config: dict[str, float], bottom_tag: str, bottom_config: dict[str, float]) -> dict[str, Any]:
    try:
        config = follower.FollowerConfigData(
            float(length),
            float(diameter),
            str(top_tag),
            _plain_dict(top_config),
            str(bottom_tag),
            _plain_dict(bottom_config),
        )
        generated_follower = follower.Follower.generate(config)
        if generated_follower is None:
            return {"error": "No follower generated", "error_code": "empty_model"}

        return shared_generate(generated_follower, "realkey-follower")

    except Exception as e:
        return {"error": f"{e.__class__.__name__}: {e}", "error_code": "follower_generation_failed"}


def set_base_url(base_url: str):
    resource_fetcher.set_base_url(base_url)


__export__ = ["generate_key", "generate_follower", "set_base_url"]
