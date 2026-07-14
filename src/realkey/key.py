from build123d import Part
from abc import ABC, abstractmethod


class Key(ABC):
    """A class that all Keys should extend and define the methods of for a common key generation scheme"""

    _list = {}

    def __init_subclass__(cls, **kwargs):
        """Used to have a list of all current keys available for generation"""
        super().__init_subclass__(**kwargs)
        tag = cls.tag()
        existing = Key._list.get(tag)
        if existing is not None and existing is not cls:
            raise ValueError(f'Key tag "{tag}" is already registered by {existing.__name__}')
        Key._list[tag] = cls

    @classmethod
    @abstractmethod
    def tag(cls) -> str:
        """Returns the tag of this key used for lookup"""

    @classmethod
    @abstractmethod
    def display_name(cls) -> str:
        """Returns the display name of this key"""

    @classmethod
    @abstractmethod
    def profiles(cls) -> dict[str, dict[str, str]]:
        """Returns the possible profiles for this key"""

    @classmethod
    @abstractmethod
    def keyways(cls) -> dict[str, dict[str, str]]:
        """Returns the possible keyways for this key"""

    @classmethod
    @abstractmethod
    def basic_bitting_definition(cls) -> str:
        """Provides an explanation for how the bitting string should be interpreted"""

    @classmethod
    @abstractmethod
    def advanced_bitting_definition(cls) -> str | None:
        """Provides detailed decoding instructions to assist in bitting"""

    @classmethod
    @abstractmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        """Validates if the bitting is valid for the given profile and keyway"""

    @classmethod
    @abstractmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        """Returns a blank for the key with the given profile and keyway"""

    @classmethod
    @abstractmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        """Returns a cut key for the key with the given profile, keyway, and bitting"""
