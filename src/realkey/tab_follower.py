from pyscript import web, when
from pyscript.ffi import to_js
from realkey import follower, tab, web_core, web_main
import urllib.parse

follower_select = web_core.SelectElement(web.page["follower-select"])
follower_length = web_core.LengthInputElement(web.page["follower-length"])
follower_diameter = web_core.LengthInputElement(web.page["follower-diameter"])
follower_top_select = web_core.SelectElement(web.page["follower-top-select"])
follower_top_div = web_core.Element(web.page["follower-top-div"])
follower_bottom_select = web_core.SelectElement(web.page["follower-bottom-select"])
follower_bottom_div = web_core.Element(web.page["follower-bottom-div"])


def run_validation():
    web_main.info.html = ""
    web_main.generate.enabled = True


def load_follower():
    selected_tag = follower_select.selected_value

    config = follower.FOLLOWER_DEFINITIONS[selected_tag]
    if config is None:
        return

    follower_length.value = config.length
    follower_diameter.value = config.diameter
    follower_top_select.selected_value = config.top_tag
    # load_follower_end
    follower_bottom_select.selected_value = config.bottom_tag
    # load_follower_end


@when("change", "#follower-select")
def follower_change():
    load_follower()
    run_validation()


class FollowerTab(tab.Tab):
    def __init__(self, button: web_core.Element, tab: web_core.Element) -> None:
        super().__init__(button, tab)

        follower_select.populate("", {"": {k: k for k in follower.FOLLOWER_DEFINITIONS.keys()}})
        follower_select.enabled = True

        follower_top_select.populate("", {"": {k: v.display_name() for k, v in follower.FollowerEnd._list.items()}})
        follower_top_select.enabled = True

        follower_bottom_select.populate("", {"": {k: v.display_name() for k, v in follower.FollowerEnd._list.items()}})
        follower_bottom_select.enabled = True

    def show(self):
        super().show()
        run_validation()

    def load_from_params(self, query_params):
        if "follower" in query_params:
            target_follower = urllib.parse.unquote(query_params["follower"])
            try:
                follower_select.selected_value = target_follower
                follower_change()
            except:
                pass

    async def generate(self, bg_worker) -> dict[str, str]:
        gen_follower = (
            await bg_worker.generate_follower(
                follower_length.stripped_value, follower_diameter.stripped_value, follower_top_select.selected_value, {}, follower_bottom_select.selected_value, {}
            )
        ).to_py()  # type: ignore
        if "error" in gen_follower:
            return gen_follower

        gen_follower["description"] = "Follower"
        gen_follower["roughness"] = 0.25
        gen_follower["metalness"] = 0.95
        gen_follower["color"] = 0xC0C0C0

        return gen_follower
