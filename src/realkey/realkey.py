from pyscript import document, web, when
from pyscript.ffi import to_js
from pyscript.js_modules import key3d
from js import Blob, navigator, URL, URLSearchParams, window

import binascii, html, urllib.parse
from realkey.Common import key
from realkey.ASSA import ASSA
from realkey.DOM import DOM
from realkey.MIWA import MIWA
from realkey.Opnus import Opnus
from realkey.Paclock import Paclock
from realkey.SargentAndGreenleaf import SargentAndGreenleaf

from build123d import *

key_select: web.ElementCollection = web.page["key-select"]
profile_select: web.ElementCollection = web.page["profile-select"]
keyway_select: web.ElementCollection = web.page["keyway-select"]
show_advanced: web.ElementCollection = web.page["show-advanced"]
bitting_instructions: web.ElementCollection = web.page["bitting-instructions"]
bitting: web.ElementCollection = web.page["bitting"]
generate: web.ElementCollection = web.page["generate"]
save_stl: web.ElementCollection = web.page["save-stl"]
save_step: web.ElementCollection = web.page["save-step"]
copy_link: web.ElementCollection = web.page["copy-link"]
info: web.ElementCollection = web.page["info"]
model_overlay: web.ElementCollection = web.page["model-overlay"]
advanced_bitting_info: web.ElementCollection = web.page["advanced-bitting-info"]

keygen = None
stl_blob: Blob = None
step_blob: Blob = None  # Help me step blob Im stuck


async def main(bg_keygen):
    global keygen
    keygen = bg_keygen
    remove_loading()
    load_keys()
    await apply_search_params()


def remove_loading():
    # defaults
    global profile_select, keyway_select, show_advanced, bitting_instructions, bitting, generate, save_stl, save_step, copy_link, info, model_overlay, advanced_bitting_info

    disable_element(key_select)
    disable_element(profile_select)
    disable_element(keyway_select)
    disable_element(bitting)
    if not "hide" in show_advanced.classes:
        show_advanced.classes.add("hide")
    bitting_instructions.innerHTML = ""
    bitting.value = ""
    disable_element(generate)
    disable_element(save_stl)
    disable_element(save_step)
    disable_element(copy_link)
    info.innerHTML = ""
    model_overlay.innerHTML = ""
    advanced_bitting_info.innerHTML = ""

    key3d.loadKey("resources/realkey.stl")
    loader = web.page["loader"]
    loader.classes.add("hide")


def load_keys():
    global key_select
    populate_select(key_select, "Choose a key", {k: v.display_name() for k, v in key.Key._list.items()})
    enable_element(key_select)


async def apply_search_params():
    global key_select, profile_select, keyway_select, bitting

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
    global key_select
    key_tag = key_select.options.selected.value
    if key_tag == "null" or key_tag is None:
        return None

    return key.Key._list[key_tag]


def get_selected_profile() -> str:
    global profile_select
    return str(profile_select.options.selected.value)


def get_selected_keyway() -> str:
    global keyway_select
    return str(keyway_select.options.selected.value)


def get_bitting() -> str:
    global bitting
    return str(bitting.value)


@when("change", "#key-select")
def load_profiles_and_keyways():
    global profile_select, keyway_select, bitting_instructions, bitting, generate, info, model_overlay, save_stl, save_step, copy_link
    selected_key = get_selected_key()
    info.innerHTML = ""
    model_overlay.innerHTML = ""

    if selected_key is None:
        populate_select(profile_select, "No profiles loaded...", {})
        populate_select(keyway_select, "No keyways loaded...", {})
        if not "hide" in show_advanced.classes:
            show_advanced.classes.add("hide")
        advanced_bitting_info.innerHTML = ""
        bitting_instructions.innerHTML = ""
        bitting.value = ""
        disable_element(profile_select)
        disable_element(keyway_select)
        disable_element(bitting)
        disable_element(generate)
        disable_element(save_stl)
        disable_element(save_step)
        disable_element(copy_link)
        return

    populate_select(profile_select, "", selected_key.profiles())
    populate_select(keyway_select, "", selected_key.keyways())
    decode_definition = selected_key.advanced_bitting_definition()
    if decode_definition is not None:
        show_advanced.classes.discard("hide")
        advanced_bitting_info.innerHTML = decode_definition
    else:
        if not "hide" in show_advanced.classes:
            show_advanced.classes.add("hide")
        advanced_bitting_info.innerHTML = ""
    bitting_instructions.innerHTML = selected_key.basic_bitting_definition()
    bitting.value = ""
    enable_element(profile_select)
    enable_element(keyway_select)
    enable_element(bitting)
    enable_element(generate)


@when("keyup", "#bitting")
def bitting_change():
    global info

    selected_key = get_selected_key()
    if selected_key is None:
        return
    try:
        profile = get_selected_profile()
        keyway = get_selected_keyway()
        bitting = get_bitting()
        selected_key.validate_bitting(profile, keyway, bitting)
        info.innerHTML = ""
    except Exception as e:
        info.innerHTML = f"<span style='color:#800'>{e}</span>"


@when("click", "#generate")
async def generate_key():
    global generate, preview, save_stl, save_step, copy_link, info, model_overlay, keygen, stl_blob, step_blob
    disable_element(generate)
    disable_element(save_stl)
    disable_element(save_step)
    disable_element(copy_link)

    selected_key = get_selected_key()
    if selected_key is None:
        return

    model_overlay.innerHTML = "Generating..."
    profile = get_selected_profile()
    keyway = get_selected_keyway()
    bitting = get_bitting()

    gen_keys = (await keygen.generate_key(selected_key.name(), profile, keyway, bitting)).to_py()
    if "error" in gen_keys:
        decoded_error = gen_keys["error"]
        info.innerHTML = f"<span style='color:#800'>{decoded_error}</span>"
        model_overlay.innerHTML = ""
        enable_element(generate)
        return

    stl_bytes = binascii.a2b_base64(gen_keys["stl"])
    step_bytes = binascii.a2b_base64(gen_keys["step"])
    stl_blob = Blob.new([to_js(stl_bytes)], {type: "model/stl"})
    step_blob = Blob.new([to_js(step_bytes)], {type: "model/step"})

    stl_url = URL.createObjectURL(stl_blob)
    key3d.loadKey(stl_url)
    URL.revokeObjectURL(stl_url)
    model_overlay.innerHTML = ""

    enable_element(generate)
    enable_element(save_stl)
    enable_element(save_step)
    enable_element(copy_link)


def save_shared(blob, extension: str):
    global key_select

    key = str(key_select.options.selected.innerHTML)
    profile = get_selected_profile()
    keyway = get_selected_keyway()
    bitting = get_bitting()

    url = URL.createObjectURL(blob)
    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", html.unescape(f"{key}_{profile}_{keyway}_{bitting}.{extension}"))
    hidden_link.setAttribute("href", url)
    hidden_link.click()
    URL.revokeObjectURL(url)


@when("click", "#save-stl")
def save_as_stl():
    global stl_blob
    if stl_blob is None:
        return

    save_shared(stl_blob, "stl")


@when("click", "#save-step")
def save_as_step():
    global step_blob
    if step_blob is None:
        return

    save_shared(step_blob, "step")


@when("click", "#copy-link")
def copy_link_to_clipboard():
    selected_key = get_selected_key()
    if selected_key is None:
        return
    profile = get_selected_profile()
    keyway = get_selected_keyway()
    bitting = get_bitting()

    tmpurl = URL.new(window.location.href)
    tmpurl.search = ""
    tmpurl.hash = ""

    url = tmpurl.toString() + "?key=" + urllib.parse.quote(selected_key.name(), safe="")
    if profile != "null":
        url += "&profile=" + urllib.parse.quote(profile, safe="")
    if keyway != "null":
        url += "&keyway=" + urllib.parse.quote(keyway, safe="")
    if bitting != "":
        url += "&bitting=" + urllib.parse.quote(bitting, safe="")
    url += "&generate"

    navigator.clipboard.writeText(url)


def populate_select(select_element: web.ElementCollection, null_string: str, dict: dict[str, str]):
    select_element.options.clear()
    if len(null_string) > 0:
        select_element.options.add(value="null", html=null_string)

    for value, html in dict.items():
        select_element.options.add(value=value, html=html)


def enable_element(element: web.ElementCollection):
    element.removeAttribute("disabled")


def disable_element(element: web.ElementCollection):
    element.disabled = True


def uncheck_element(element: web.ElementCollection):
    element.removeAttribute("checked")
