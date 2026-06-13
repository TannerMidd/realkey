import binascii

from pyscript import document, web, when
from pyscript.ffi import to_js
from pyscript.js_modules import model_view  # type: ignore
from js import Blob, URL, URLSearchParams, window  # type: ignore

import html, urllib.parse
from build123d import *
from realkey import tab, tab_key, tab_follower, web_core

generate = web_core.Element(web.page["generate"])
save_stl = web_core.Element(web.page["save-stl"])
save_step = web_core.Element(web.page["save-step"])
copy_link = web_core.Element(web.page["copy-link"])
info = web_core.Element(web.page["info"])
model_description = web_core.Element(web.page["model-description"])
model_generating = web_core.Element(web.page["model-generating"])
meta_image = web.page["meta-image"]

bg_worker = None
stl_blob: Blob = None
step_blob: Blob = None  # Help me step blob Im stuck

tabs: dict[str, tab.Tab] = {
    "key": tab_key.KeyTab(web_core.Element(web.page["key-tab-button"]), web_core.Element(web.page["key-tab"])),
    "follower": tab_follower.FollowerTab(web_core.Element(web.page["follower-tab-button"]), web_core.Element(web.page["follower-tab"])),
}


async def main(background_worker):
    global bg_worker
    bg_worker = background_worker
    remove_loading()

    await apply_search_params()


def remove_loading():
    # defaults
    generate.enabled = False
    save_stl.enabled = False
    save_step.enabled = False
    copy_link.enabled = False
    info.html = ""
    model_generating.html = ""

    model_view.loadObject("resources/realkey.stl", 0.25, 0.95)
    model_description.html = "<i>Is this a real key?</i>"
    loader = web.page["loader"]
    loader.classes.add("hide")


async def apply_search_params():
    query_params = URLSearchParams.new(window.location.search)

    # legacy links, assume tab is key
    target_tab = "key"
    if "tab" in query_params:
        target_tab = urllib.parse.unquote(query_params["tab"])

    for key, tab in tabs.items():
        if key == target_tab:
            tab.show()
            tab.load_from_params(query_params)
        else:
            tab.hide()

    if "generate" in query_params:
        await start_generation()


def get_selected_tab() -> tab.Tab:
    for _, tab in tabs.items():
        if tab.selected:
            return tab
    return tabs["keys"]


def change_to_tab(tab_key: str):
    for key, tab in tabs.items():
        if key == tab_key:
            tab.show()
        else:
            tab.hide()


@when("click", "#key-tab-button")
def change_to_key_tab():
    change_to_tab("key")


@when("click", "#follower-tab-button")
def change_to_follower_tab():
    change_to_tab("follower")


@when("click", "#generate")
async def start_generation():
    generate.enabled = False
    save_stl.enabled = False
    save_step.enabled = False

    model_generating.html = "Generating..."

    data = await get_selected_tab().generate(bg_worker)
    if "error" in data:
        info.html = f"<span style='color:#800'>{data["error"]}</span>"
        model_generating.html = ""
        generate.enabled = True
        return

    global stl_blob, step_blob
    stl_blob = Blob.new([to_js(binascii.a2b_base64(data["stl"]))], {type: "model/stl"})
    step_blob = Blob.new([to_js(binascii.a2b_base64(data["step"]))], {type: "model/step"})

    roughness = data["roughness"] if "roughness" in data else 0.5
    metalness = data["metalness"] if "metalness" in data else 0.95
    color = data["color"] if "color" in data else 0xE3BD7A
    description = data["description"] if "description" in data else "There is no key..."

    stl_url = URL.createObjectURL(stl_blob)
    model_view.loadObject(stl_url, roughness, metalness, color)
    URL.revokeObjectURL(stl_url)
    info.html = ""
    model_generating.html = ""
    model_description.html = description

    generate.enabled = True
    save_stl.enabled = True
    save_step.enabled = True


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
