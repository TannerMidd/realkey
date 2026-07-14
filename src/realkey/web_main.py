from __future__ import annotations

import base64
import json
import re
import urllib.parse
from typing import Any

from pyscript import document, web, when
from pyscript.ffi import to_js
from pyscript.js_modules import model_view  # type: ignore
from js import Blob, navigator, URL, window  # type: ignore

from realkey import fabrication, tab, tab_follower, tab_key, web_core


generate = web_core.Element(web.page["generate"])
generate_label = web_core.Element(web.page["generate-label"])
save_stl = web_core.Element(web.page["save-stl"])
save_step = web_core.Element(web.page["save-step"])
save_3mf = web_core.Element(web.page["save-3mf"])
copy_link = web_core.Element(web.page["copy-link"])
info = web_core.Element(web.page["info"])
model_description = web_core.Element(web.page["model-description"])
model_generating = web_core.Element(web.page["model-generating"])
model_workspace = web_core.Element(web.page["model-view"])
meta_image = web.page["meta-image"]
share_settings = web_core.CheckboxElement(web.page["share-settings"])
share_generate = web_core.CheckboxElement(web.page["share-generate"])
share_dialog = web_core.Element(web.page["share-dialog"])
fabrication_profile_select = web_core.SelectElement(web.page["fabrication-profile"])
fabrication_report = web_core.Element(web.page["fabrication-report"])
fabrication_nozzle = web_core.StringValueElement(web.page["fabrication-nozzle"])
fabrication_layer_height = web_core.StringValueElement(web.page["fabrication-layer-height"])
fabrication_build_width = web_core.StringValueElement(web.page["fabrication-build-width"])
fabrication_build_depth = web_core.StringValueElement(web.page["fabrication-build-depth"])
fabrication_build_height = web_core.StringValueElement(web.page["fabrication-build-height"])
fabrication_wall_lines = web_core.StringValueElement(web.page["fabrication-wall-lines"])
fabrication_profile_settings = web_core.Element(web.page["fabrication-profile-settings"])


bg_worker = None
stl_blob: Blob | None = None
step_blob: Blob | None = None
three_mf_blob: Blob | None = None
_generated_filename = "realkey-model"
_latest_metrics: dict[str, object] | None = None
_latest_export_warnings: list[str] = []
_generation_revision = 0
_startup_notice = ""
_WORKSPACE_STORAGE_KEY = "realkey.workspace.v1"


tabs: dict[str, tab.Tab] = {
    "key": tab_key.KeyTab(web_core.Element(web.page["key-tab-button"]), web_core.Element(web.page["key-tab"])),
    "follower": tab_follower.FollowerTab(web_core.Element(web.page["follower-tab-button"]), web_core.Element(web.page["follower-tab"])),
}


async def main(background_worker):
    global bg_worker
    bg_worker = background_worker
    _initialize_fabrication_controls()
    await _apply_startup_state()
    await _remove_loading()
    if _startup_notice:
        info.text = _startup_notice


async def _remove_loading():
    generate.enabled = False
    _set_downloads_enabled(False)
    model_generating.text = ""
    model_workspace._web_element.removeAttribute("aria-busy")  # type: ignore
    fabrication_report.text = "Generate a model to run profile-based fabrication checks."

    try:
        await model_view.loadObject("resources/realkey.stl", 0.25, 0.95)
        model_description.text = "Example model — configure a model and generate locally"
    except Exception as error:
        model_description.text = "Preview unavailable"
        info.text = f"The controls are ready, but the initial preview could not load: {error}"
    finally:
        web.page["loader"].classes.add("hide")

    # The selected tab owns final validation of the Generate action.
    selected_tab, _ = get_selected_tab()
    selected_tab.show()


def _set_downloads_enabled(enabled: bool, *, has_3mf: bool = False):
    save_stl.enabled = enabled
    save_step.enabled = enabled
    save_3mf.enabled = enabled and has_3mf


def _parse_url_params() -> dict[str, str]:
    # New links keep physical-access settings in the fragment so they are not
    # sent to the host. Query parsing remains for backwards compatibility.
    fragment = str(window.location.hash).removeprefix("#")
    query = str(window.location.search).removeprefix("?")
    encoded = fragment if fragment else query
    return dict(urllib.parse.parse_qsl(encoded, keep_blank_values=True))


def _stored_workspace() -> dict[str, object] | None:
    try:
        payload = window.localStorage.getItem(_WORKSPACE_STORAGE_KEY)
        if payload is None or str(payload) in ("", "null"):
            return None
        parsed = json.loads(str(payload))
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


async def _apply_startup_state():
    global _startup_notice
    shared_params = _parse_url_params()
    if shared_params:
        _apply_tab_params(shared_params)
        _apply_fabrication_params(shared_params)
        if len(shared_params) > 1:
            _startup_notice = "Shared settings loaded. Review them, then select Generate to run CAD locally."
        persist_workspace_state()
        return

    stored = _stored_workspace()
    if stored is None:
        _apply_tab_params({"tab": "key"})
        return

    params = stored.get("params", {})
    if isinstance(params, dict):
        plain_params = {str(key): str(value) for key, value in params.items()}
        plain_params["tab"] = str(stored.get("tab", "key"))
        _apply_tab_params(plain_params)

    profile_data = stored.get("fabrication")
    if isinstance(profile_data, dict):
        try:
            _apply_profile_controls(fabrication.PrinterProfile.from_dict(profile_data))
        except ValueError:
            _apply_profile_controls(fabrication.GENERIC_PLA_PROFILE)


def _apply_tab_params(params: dict[str, str]):
    target_tag = params.get("tab", "key")
    if target_tag not in tabs:
        target_tag = "key"

    for tag, tab_instance in tabs.items():
        if tag == target_tag:
            tab_instance.show()
            tab_instance.load_from_params(params)
        else:
            tab_instance.hide()


def _apply_fabrication_params(params: dict[str, str]):
    profile_id = params.get("printer")
    if not profile_id:
        return
    if profile_id != "custom":
        try:
            _apply_profile_controls(fabrication.get_builtin_profile(profile_id))
        except KeyError:
            pass
        return

    try:
        profile = fabrication.PrinterProfile(
            profile_id="custom",
            name="Custom local profile",
            material="Custom",
            nozzle_diameter_mm=float(params["nozzle"]),
            layer_height_mm=float(params["layer"]),
            build_width_mm=float(params["build_x"]),
            build_depth_mm=float(params["build_y"]),
            build_height_mm=float(params["build_z"]),
            minimum_wall_lines=int(params["wall_lines"]),
        )
    except (KeyError, TypeError, ValueError):
        return
    _apply_profile_controls(profile)


def get_selected_tab() -> tuple[tab.Tab, str]:
    for tag, tab_instance in tabs.items():
        if tab_instance.selected:
            return tab_instance, tag
    return tabs["key"], "key"


def change_to_tab(tab_key: str):
    if tab_key not in tabs:
        tab_key = "key"
    _, current_tag = get_selected_tab()
    if current_tag != tab_key:
        on_model_input_changed()
    for key, tab_instance in tabs.items():
        if key == tab_key:
            tab_instance.show()
        else:
            tab_instance.hide()
    persist_workspace_state()


def set_generation_context(model_type: str):
    labels = {
        "blank": "Generate blank",
        "key": "Generate key",
        "follower": "Generate follower",
    }
    generate_label.text = labels.get(model_type, "Generate model")


@when("click", "#key-tab-button")
def change_to_key_tab():
    change_to_tab("key")


@when("click", "#follower-tab-button")
def change_to_follower_tab():
    change_to_tab("follower")


def on_model_input_changed():
    """Invalidate artifacts that no longer match the editable model inputs."""
    global stl_blob, step_blob, three_mf_blob, _latest_metrics, _generation_revision
    _generation_revision += 1
    had_artifact = stl_blob is not None or step_blob is not None or three_mf_blob is not None
    stl_blob = None
    step_blob = None
    three_mf_blob = None
    _latest_metrics = None
    _set_downloads_enabled(False)
    model_generating.text = ""
    if had_artifact:
        model_description.text = "Inputs changed — generate again to refresh the model and exports."
    fabrication_report.text = "Inputs changed. Generate again to refresh fabrication checks."
    persist_workspace_state()


def _decode_blob(encoded: object, mime_type: str) -> Blob:
    raw = base64.b64decode(str(encoded), validate=True)
    return Blob.new([to_js(raw)], {"type": mime_type})


@when("click", "#generate")
async def start_generation():
    global stl_blob, step_blob, three_mf_blob, _generated_filename
    global _latest_metrics, _latest_export_warnings, _generation_revision

    if bg_worker is None:
        info.text = "The CAD worker is not ready yet."
        return

    try:
        profile_snapshot = _profile_from_controls()
    except ValueError as error:
        info.text = f"Fabrication profile needs attention: {error}"
        return

    selected_tab, _ = get_selected_tab()
    _generation_revision += 1
    job_revision = _generation_revision
    generate.enabled = False
    _set_downloads_enabled(False)
    info.text = ""
    model_generating.text = "Generating geometry and exports…"
    model_workspace._web_element.setAttribute("aria-busy", "true")  # type: ignore
    preview_url = None

    try:
        data = await selected_tab.generate(bg_worker)
        if job_revision != _generation_revision:
            return
        if "error" in data:
            raise RuntimeError(str(data["error"]))

        next_stl = _decode_blob(data["stl"], "model/stl")
        next_step = _decode_blob(data["step"], "model/step")
        next_3mf = _decode_blob(data["3mf"], "model/3mf") if "3mf" in data else None

        roughness = data.get("roughness", 0.5)
        metalness = data.get("metalness", 0.95)
        color = data.get("color", 0xE3BD7A)
        description = str(data.get("description", "Generated realkey model"))

        preview_url = URL.createObjectURL(next_stl)
        await model_view.loadObject(preview_url, roughness, metalness, color)
        if job_revision != _generation_revision:
            return

        stl_blob = next_stl
        step_blob = next_step
        three_mf_blob = next_3mf
        _generated_filename = _slugify(description)
        metrics_data = data.get("metrics")
        _latest_metrics = dict(metrics_data) if isinstance(metrics_data, dict) else None
        raw_warnings = data.get("warnings", [])
        _latest_export_warnings = [str(item) for item in raw_warnings]

        model_description.text = description
        _render_fabrication_report(profile_snapshot)
        _set_downloads_enabled(True, has_3mf=three_mf_blob is not None)
    except Exception as error:
        if job_revision == _generation_revision:
            info.text = f"Generation failed: {error}"
            fabrication_report.text = "No fabrication report is available for the failed job."
            _set_downloads_enabled(False)
    finally:
        if preview_url is not None:
            URL.revokeObjectURL(preview_url)
        if job_revision == _generation_revision:
            model_generating.text = ""
            generate.enabled = True
            model_workspace._web_element.removeAttribute("aria-busy")  # type: ignore


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return slug[:120] or "realkey-model"


def save_shared(blob: Blob | None, extension: str):
    if blob is None:
        return
    url = URL.createObjectURL(blob)
    try:
        hidden_link = document.createElement("a")  # type: ignore
        hidden_link.setAttribute("download", f"{_generated_filename}.{extension}")
        hidden_link.setAttribute("href", url)
        hidden_link.click()
    finally:
        URL.revokeObjectURL(url)


@when("click", "#save-stl")
def save_as_stl():
    save_shared(stl_blob, "stl")


@when("click", "#save-step")
def save_as_step():
    save_shared(step_blob, "step")


@when("click", "#save-3mf")
def save_as_3mf():
    save_shared(three_mf_blob, "3mf")


def _share_params() -> dict[str, str]:
    current_tab, tab_tag = get_selected_tab()
    params = {"tab": tab_tag}
    if share_settings.checked:
        params.update(current_tab.get_query_params())
        profile = _profile_from_controls()
        params["printer"] = profile.profile_id
        if profile.profile_id == "custom":
            params.update(
                {
                    "nozzle": str(profile.nozzle_diameter_mm),
                    "layer": str(profile.layer_height_mm),
                    "build_x": str(profile.build_width_mm),
                    "build_y": str(profile.build_depth_mm),
                    "build_z": str(profile.build_height_mm),
                    "wall_lines": str(profile.minimum_wall_lines),
                }
            )
    if share_generate.checked:
        # The receiver still makes the final Generate gesture; this flag only
        # presents a clear review prompt on load.
        params["generate"] = "review"
    return params


@when("click", "#copy-link")
def create_share_link():
    try:
        base_url = f"{window.location.origin}{window.location.pathname}"
        share_url = f"{base_url}#{urllib.parse.urlencode(_share_params())}"
        navigator.clipboard.writeText(share_url)
        info.text = "Fragment link copied. Treat it as sensitive if you included model settings."
        share_dialog.hide_popover()
    except Exception as error:
        info.text = f"The link could not be copied: {error}"


def _initialize_fabrication_controls():
    options = {profile.profile_id: profile.name for profile in fabrication.BUILTIN_PROFILES}
    options["custom"] = "Custom local profile"
    fabrication_profile_select.populate("", {"": options})
    _apply_profile_controls(fabrication.GENERIC_PLA_PROFILE)


def _apply_profile_controls(profile: fabrication.PrinterProfile):
    selected_id = profile.profile_id if profile.profile_id in {
        item.profile_id for item in fabrication.BUILTIN_PROFILES
    } else "custom"
    fabrication_profile_select.selected_value = selected_id
    fabrication_nozzle.value = str(profile.nozzle_diameter_mm)
    fabrication_layer_height.value = str(profile.layer_height_mm)
    fabrication_build_width.value = str(profile.build_width_mm)
    fabrication_build_depth.value = str(profile.build_depth_mm)
    fabrication_build_height.value = str(profile.build_height_mm)
    fabrication_wall_lines.value = str(profile.minimum_wall_lines)
    if selected_id == "custom":
        fabrication_profile_settings._web_element.setAttribute("open", "")  # type: ignore
    else:
        fabrication_profile_settings._web_element.removeAttribute("open")  # type: ignore


def _profile_from_controls() -> fabrication.PrinterProfile:
    profile_id = fabrication_profile_select.selected_value
    if profile_id != "custom":
        builtin = fabrication.get_builtin_profile(profile_id)
        # Controls are synchronized for built-ins, so returning the canonical
        # object keeps report/caching output deterministic.
        return builtin
    return fabrication.PrinterProfile(
        profile_id="custom",
        name="Custom local profile",
        material="Custom",
        nozzle_diameter_mm=float(fabrication_nozzle.stripped_value),
        layer_height_mm=float(fabrication_layer_height.stripped_value),
        build_width_mm=float(fabrication_build_width.stripped_value),
        build_depth_mm=float(fabrication_build_depth.stripped_value),
        build_height_mm=float(fabrication_build_height.stripped_value),
        minimum_wall_lines=int(fabrication_wall_lines.stripped_value),
    )


@when("change", "#fabrication-profile")
def fabrication_profile_changed():
    try:
        profile_id = fabrication_profile_select.selected_value
        if profile_id != "custom":
            _apply_profile_controls(fabrication.get_builtin_profile(profile_id))
        else:
            fabrication_profile_settings._web_element.setAttribute("open", "")  # type: ignore
        profile = _profile_from_controls()
        _render_fabrication_report(profile)
        persist_workspace_state()
        get_selected_tab()[0].show()
    except (KeyError, ValueError) as error:
        fabrication_report.text = f"Profile needs attention: {error}"
        generate.enabled = False


@when("input", "#fabrication-nozzle, #fabrication-layer-height, #fabrication-build-width, #fabrication-build-depth, #fabrication-build-height, #fabrication-wall-lines")
def custom_profile_changed():
    fabrication_profile_select.selected_value = "custom"
    try:
        profile = _profile_from_controls()
        _render_fabrication_report(profile)
        persist_workspace_state()
        get_selected_tab()[0].show()
    except ValueError as error:
        fabrication_report.text = f"Profile needs attention: {error}"
        generate.enabled = False


def _append_text(parent: Any, tag: str, value: str, class_name: str = "") -> Any:
    element = document.createElement(tag)  # type: ignore
    element.textContent = value
    if class_name:
        element.className = class_name
    parent.appendChild(element)
    return element


def _render_fabrication_report(profile: fabrication.PrinterProfile):
    report_root = fabrication_report._web_element
    report_root.replaceChildren()  # type: ignore
    if _latest_metrics is None:
        _append_text(report_root, "p", "Generate a model to run profile-based fabrication checks.")
        return

    try:
        metrics = fabrication.ModelMetrics.from_dict(_latest_metrics)
        report = fabrication.analyze_printability(metrics, profile)
    except ValueError as error:
        _append_text(report_root, "p", f"Fabrication metrics were invalid: {error}", "report-error")
        return

    status_labels = {
        "no_issues_detected": "No profile-limit issues detected",
        "review_recommended": "Review recommended",
        "outside_profile_limits": "Outside profile limits",
    }
    _append_text(
        report_root,
        "h3",
        status_labels.get(report.status, report.status.replace("_", " ").title()),
        f"report-status status-{report.status}",
    )
    _append_text(
        report_root,
        "p",
        (
            f"{metrics.size_x_mm:.2f} × {metrics.size_y_mm:.2f} × {metrics.size_z_mm:.2f} mm · "
            f"{profile.name} · {profile.layer_height_mm:g} mm layers"
        ),
        "report-metrics",
    )

    if report.issues:
        issue_list = document.createElement("ul")  # type: ignore
        issue_list.className = "fabrication-issues"
        for issue in report.issues:
            item = document.createElement("li")  # type: ignore
            item.className = f"fabrication-issue severity-{issue.severity.value}"
            _append_text(item, "strong", issue.message)
            _append_text(item, "span", issue.recommendation)
            issue_list.appendChild(item)
        report_root.appendChild(issue_list)

    for warning in _latest_export_warnings:
        _append_text(report_root, "p", warning, "fabrication-issue severity-warning")
    _append_text(report_root, "p", report.notice, "report-notice")


def persist_workspace_state():
    try:
        current_tab, tab_tag = get_selected_tab()
        profile = _profile_from_controls()
        payload = {
            "version": 1,
            "tab": tab_tag,
            "params": current_tab.get_query_params(),
            "fabrication": profile.to_dict(),
        }
        window.localStorage.setItem(
            _WORKSPACE_STORAGE_KEY,
            json.dumps(payload, allow_nan=False, separators=(",", ":")),
        )
    except Exception:
        # Local storage can be disabled in privacy modes; it must never block
        # generation or sharing.
        pass
