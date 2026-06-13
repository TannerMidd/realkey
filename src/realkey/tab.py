from abc import ABC, abstractmethod
from typing_extensions import Self

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

    def show(self):
        self._tab.hidden = False
        self._button.active = True

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
