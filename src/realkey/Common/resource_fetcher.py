import sys

if sys.platform == "emscripten":
    from pyscript.context import window
    from pyodide.http import pyxhr
    from js import URL

import os, pathlib


def get_base_url() -> str:
    if sys.platform != "emscripten":
        return ""

    tmpurl = URL.new(window.location.href)
    tmpurl.search = ""
    tmpurl.hash = ""

    return tmpurl.toString()


def pre_fetch_resource(resource: str) -> bool:
    if sys.platform != "emscripten":
        return True

    fetch_path = f"{get_base_url()}{resource}"

    if pathlib.Path(resource).is_file():
        return True

    os.makedirs(os.path.dirname(resource), exist_ok=True)

    response = pyxhr.get(fetch_path)
    if response.ok:
        data = response._xhr.response

        with open(resource, "wb") as r:
            r.write(data.encode("utf-8"))
        return True
    return False
