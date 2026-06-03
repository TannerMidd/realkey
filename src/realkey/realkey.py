from pyscript import document, web, when
from pyscript.ffi import to_js
from pyscript.js_modules import key3d  # type: ignore
from js import Blob, navigator, URL, URLSearchParams, window  # type: ignore

import binascii, html, urllib.parse
from build123d import *
from realkey import key, web_core, ASSA, DOM, MIWA, Opnus, Paclock, SargentAndGreenleaf

key_select = web_core.SelectElement(web.page["key-select"])
profile_select = web_core.SelectElement(web.page["profile-select"])
keyway_select = web_core.SelectElement(web.page["keyway-select"])
show_advanced = web_core.Element(web.page["show-advanced"])
bitting_instructions = web_core.Element(web.page["bitting-instructions"])
bitting = web_core.ValueElement(web.page["bitting"])
generate = web_core.Element(web.page["generate"])
save_stl = web_core.Element(web.page["save-stl"])
save_step = web_core.Element(web.page["save-step"])
copy_link = web_core.Element(web.page["copy-link"])
info = web_core.Element(web.page["info"])
model_description = web_core.Element(web.page["model-description"])
model_overlay = web_core.Element(web.page["model-overlay"])
advanced_bitting_info = web_core.Element(web.page["advanced-bitting-info"])

keygen = None
stl_blob: Blob = None
step_blob: Blob = None  # Help me step blob Im stuck


async def main(bg_keygen):
    global keygen
    keygen = bg_keygen
    remove_loading()
    key_select.populate("Choose a key", {k: v.display_name() for k, v in key.Key._list.items()})
    key_select.enabled = True
    await apply_search_params()


def remove_loading():
    # defaults
    key_select.enabled = False
    profile_select.enabled = False
    keyway_select.enabled = False
    bitting.enabled = False
    show_advanced.hidden = True
    bitting_instructions.html = ""
    bitting.value = ""
    generate.enabled = False
    save_stl.enabled = False
    save_step.enabled = False
    copy_link.enabled = False
    info.html = ""
    model_overlay.html = ""
    advanced_bitting_info.html = ""

    key3d.loadKey("resources/realkey.stl")
    model_description.html = "<i>Is this a real key?</i>"
    loader = web.page["loader"]
    loader.classes.add("hide")


async def apply_search_params():
    query_params = URLSearchParams.new(window.location.search)
    if "key" in query_params:
        target_key = urllib.parse.unquote(query_params.get("key"))
        for option in key_select.options:
            if option.value == target_key:
                option.selected = True
                load_profiles_and_keyways()
                break
    else:
        return
    if "profile" in query_params:
        target_profile = urllib.parse.unquote(query_params.get("profile"))
        for option in profile_select.options:
            if option.value == target_profile:
                option.selected = True
                break
    if "keyway" in query_params:
        target_keyway = urllib.parse.unquote(query_params.get("keyway"))
        for option in keyway_select.options:
            if option.value == target_keyway:
                option.selected = True
                break
    if "bitting" in query_params:
        target_bitting = urllib.parse.unquote(query_params.get("bitting"))
        bitting.value = target_bitting
    if "generate" in query_params:
        await generate_key()


def get_selected_key() -> key.Key | None:
    key_tag = key_select.selected_value
    if key_tag == "null":
        return None

    return key.Key._list[key_tag]


def get_pretty_name() -> str:
    return f"{key_select.selected_html} - {profile_select.selected_html} - {keyway_select.selected_html} - {bitting.value if len(bitting.value) > 0 else 'Blank'}"


@when("change", "#key-select")
def load_profiles_and_keyways():
    selected_key = get_selected_key()
    info.html = ""
    model_overlay.html = ""

    if selected_key is None:
        profile_select.populate("No profiles loaded...", {})
        keyway_select.populate("No keyways loaded...", {})
        show_advanced.hidden = True
        advanced_bitting_info.html = ""
        bitting_instructions.html = ""
        bitting.value = ""
        profile_select.enabled = False
        keyway_select.enabled = False
        bitting.enabled = False
        generate.enabled = False
        return

    profile_select.populate("", selected_key.profiles())
    keyway_select.populate("", selected_key.keyways())
    decode_definition = selected_key.advanced_bitting_definition()
    if decode_definition is not None:
        show_advanced.hidden = False
        advanced_bitting_info.html = decode_definition
    else:
        show_advanced.hidden = True
        advanced_bitting_info.html = ""
    bitting_instructions.html = selected_key.basic_bitting_definition()
    bitting.value = ""
    profile_select.enabled = True
    keyway_select.enabled = True
    bitting.enabled = True
    generate.enabled = True


@when("keyup", "#bitting")
def bitting_change():
    if len(bitting.value) == 0:
        return
    selected_key = get_selected_key()
    if selected_key is None:
        return
    try:
        selected_key.validate_bitting(profile_select.selected_value, keyway_select.selected_value, bitting.value)
        info.html = ""
    except Exception as e:
        info.html = f"<span style='color:#800'>{e}</span>"


@when("click", "#generate")
async def generate_key():
    global stl_blob, step_blob
    generate.enabled = False
    save_stl.enabled = False
    save_step.enabled = False
    copy_link.enabled = False

    selected_key = get_selected_key()
    if selected_key is None:
        return

    model_overlay.html = "Generating..."
    gen_keys = (await keygen.generate_key(selected_key.name(), profile_select.selected_value, keyway_select.selected_value, bitting.value)).to_py()  # type: ignore
    if "error" in gen_keys:
        decoded_error = gen_keys["error"]
        info.html = f"<span style='color:#800'>{decoded_error}</span>"
        model_overlay.html = ""
        generate.enabled = True
        return

    stl_bytes = binascii.a2b_base64(gen_keys["stl"])
    step_bytes = binascii.a2b_base64(gen_keys["step"])
    stl_blob = Blob.new([to_js(stl_bytes)], {type: "model/stl"})
    step_blob = Blob.new([to_js(step_bytes)], {type: "model/step"})

    stl_url = URL.createObjectURL(stl_blob)
    key3d.loadKey(stl_url)
    URL.revokeObjectURL(stl_url)
    model_overlay.html = ""
    model_description.html = get_pretty_name()

    generate.enabled = True
    save_stl.enabled = True
    save_step.enabled = True
    copy_link.enabled = True


def save_shared(blob, extension: str):
    url = URL.createObjectURL(blob)
    hidden_link = document.createElement("a")  # type: ignore
    hidden_link.setAttribute("download", html.unescape(f"{model_description.html}.{extension}"))
    hidden_link.setAttribute("href", url)
    hidden_link.click()
    URL.revokeObjectURL(url)


@when("click", "#save-stl")
def save_as_stl():
    if stl_blob is None:
        return

    save_shared(stl_blob, "stl")


@when("click", "#save-step")
def save_as_step():
    if step_blob is None:
        return

    save_shared(step_blob, "step")


@when("click", "#copy-link")
def copy_link_to_clipboard():
    selected_key = get_selected_key()
    if selected_key is None:
        return
    profile = profile_select.selected_value
    keyway = keyway_select.selected_value
    bttn = bitting.value

    tmpurl = URL.new(window.location.href)
    tmpurl.search = ""
    tmpurl.hash = ""

    url = tmpurl.toString() + "?key=" + urllib.parse.quote(selected_key.name(), safe="")
    if profile != "null":
        url += "&profile=" + urllib.parse.quote(profile, safe="")
    if keyway != "null":
        url += "&keyway=" + urllib.parse.quote(keyway, safe="")
    if bttn != "":
        url += "&bitting=" + urllib.parse.quote(bttn, safe="")
    url += "&generate"

    navigator.clipboard.writeText(url)
