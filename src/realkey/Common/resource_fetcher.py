import sys

if sys.platform == "emscripten":
    from pyscript import RUNNING_IN_WORKER
    from pyodide.http import pyxhr
    from js import URL

import os, pathlib

_base_url: str = ""


def set_base_url(base_url: str):
    global _base_url
    _base_url = base_url


def pre_fetch_resource(resource: str) -> bool:
    if sys.platform != "emscripten":
        return True

    if _base_url == "":
        raise AttributeError("No Base URL has been set for resource fetching!")

    fetch_path = f"{_base_url}/{resource}"

    if pathlib.Path(resource).is_file():
        return True

    os.makedirs(os.path.dirname(resource), exist_ok=True)

    print(f"Downloading {fetch_path}")
    response = pyxhr.get(fetch_path)
    if response.ok:
        data = response._xhr.response

        with open(resource, "wb") as r:
            r.write(data.encode("utf-8"))
        return True
    return False
