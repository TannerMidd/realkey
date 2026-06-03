import micropip


# Bootstrap load in build123d
async def bootstrap(ocp_index="https://yeicor.github.io/OCP.wasm"):
    # Prioritize the OCP.wasm package repository so that wasm-specific packages are preferred.
    micropip.set_index_urls([ocp_index, "https://pypi.org/simple"])

    # Install the required packages.
    await micropip.install(["ipython == 9.10.0", "build123d"])


# Load the boot strap
await bootstrap()

import binascii
from build123d import *
from realkey import key, resource_fetcher, ASSA, DOM, MIWA, Opnus, Paclock, SargentAndGreenleaf


def generate_key(key_tag: str, profile: str, keyway: str, bitting: str) -> dict[str, str]:
    key_class: key.Key = key.Key._list[key_tag]

    try:
        generated_key: Part | None = None
        if len(bitting) == 0:
            generated_key = key_class.blank(profile, keyway)
        else:
            generated_key = key_class.key(profile, keyway, bitting)
        if generated_key is None:
            return {"error": "No key or blank generated!"}

        export_stl(generated_key, "temp.stl")
        export_step(generated_key, "temp.step")

        returns: dict[str, str] = {}
        with open("temp.stl", "rb") as stl:
            returns["stl"] = binascii.b2a_base64(stl.read()).decode("utf-8")
        with open("temp.step", "rb") as step:
            returns["step"] = binascii.b2a_base64(step.read()).decode("utf-8")

        return returns
    except Exception as e:
        return {"error": f"{e}"}


def set_base_url(base_url: str):
    resource_fetcher.set_base_url(base_url)


__export__ = ["generate_key", "set_base_url"]
