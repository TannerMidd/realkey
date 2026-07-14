from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from typing_extensions import Self
import urllib.parse

from realkey import web_core


class Tab(ABC):
    _instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, button: web_core.Element, tab: web_core.Element) -> None:
        super().__init__()
        self._button = button
        self._tab = tab

    @property
    def selected(self) -> bool:
        return not self._tab.hidden

    def hide(self):
        self._tab.hidden = True
        self._button.active = False
        self._button._web_element.setAttribute("aria-selected", "false")  # type: ignore
        self._button._web_element.setAttribute("tabindex", "-1")  # type: ignore
        self._tab._web_element.setAttribute("aria-hidden", "true")  # type: ignore

    def show(self):
        self._tab.hidden = False
        self._button.active = True
        self._button._web_element.setAttribute("aria-selected", "true")  # type: ignore
        self._button._web_element.setAttribute("tabindex", "0")  # type: ignore
        self._tab._web_element.setAttribute("aria-hidden", "false")  # type: ignore

    def _populate_param(self, query_params, param_name: str, set_value: Callable[[str], Any]) -> bool:
        """A helper method to set query parameters. If a given parameter name is provided, set_value is called with the value

        Args:
            query_params (_type_): A dictionary containing the query parameters from Javascripts URLSearchParams
            param_name (str): The name of the parameter to search for possible settings
            set_value (Callable[[str]]): A function that handles setting the value from the query parameters

        Returns:
            bool: False on any error, True if the param didnt exist or was set correctly
        """
        if param_name in query_params:
            target_value = urllib.parse.unquote(query_params[param_name])
            try:
                set_value(target_value)
                return True
            except:
                return False
        return True

    @abstractmethod
    def get_query_params(self) -> dict[str, str]:
        """Returns all current parameter values for the tab, used to generate shareable links"""

    @abstractmethod
    def load_from_params(self, query_params):
        """Loads the values for the given tab based"""

    @abstractmethod
    async def generate(self, bg_worker) -> dict[str, str]:
        """Generates the object this tab was designed for

        Returns:
            dict[str, str]: A return dictionary with keys and values according to the following specification:
                "stl" - A base64 encoding of the binary of a generated STL file
                "step" - A base64 encoding of the binary of a generated STEP file
                "description" - A string description of the generated object
                "roughness" - A roughness value from 0 to 1 used by the rendering engine when displaying the STL
                "metalness" - A metalness value from 0 to 1 used by the rendering engine when displaying the STL
                "color" - A color value used by the rendering engine when displaying the STL
        """
