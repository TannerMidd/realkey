from build123d import Part
import abc

class Key(abc.ABC):
    """A class that all Keys should extend and define the methods of for a common key generation scheme"""

    _list = {}

    def __init_subclass__(cls, **kwargs):
        """Used to have a list of all current keys available for generation"""
        Key._list[cls.name()] = cls

    @classmethod
    @abc.abstractmethod
    def name(cls) -> str:
        """Returns the name of this key used for lookup"""

    @classmethod
    @abc.abstractmethod
    def display_name(cls) -> str:
        """Returns the display name of this key"""

    @classmethod
    @abc.abstractmethod
    def profiles(cls) -> dict[str, str]:
        """Returns the possible profiles for this key"""
    
    @classmethod
    @abc.abstractmethod
    def keyways(cls) -> dict[str, str]:
        """Returns the possible keyways for this key"""

    @classmethod
    @abc.abstractmethod
    def basic_bitting_definition(cls) -> str:
        """Provides an explanation for how the bitting string should be interpreted"""

    @classmethod
    @abc.abstractmethod
    def advanced_bitting_definition(cls) -> str | None:
        """Provides detailed decoding instructions to assist in bitting"""

    @classmethod
    @abc.abstractmethod
    def validate_bitting(cls, profile: str, keyway: str, bitting: str):
        """Validates if the bitting is valid for the given profile and keyway"""

    @classmethod
    @abc.abstractmethod
    def blank(cls, profile: str, keyway: str) -> Part:
        """Returns a blank for the key with the given profile and keyway"""

    @classmethod
    @abc.abstractmethod
    def key(cls, profile: str, keyway: str, bitting: str) -> Part:
        """Returns a cut key for the key with the given profile, keyway, and bitting"""