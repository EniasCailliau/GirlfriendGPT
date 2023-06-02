from enum import Enum

from .alix_earle import alix_earle
from .angele import angele
from .jack_dawson import jack_dawson
from .jordan_belfort import jordan_belfort
from .luna import luna
from .makima import makima
from .sacha import sacha
from .sandra import sandra

__all__ = [
    "sacha",
    "luna",
    "angele",
    "makima",
    "sandra",
    "alix_earle",
    "jack_dawson",
    "jordan_belfort",
    "get_personality",
]


class Personality(str, Enum):
    SACHA = "sacha"
    LUNA = "luna"
    ANGELE = "angele"
    MAKIMA = "makima"
    SANDRA = "sandra"
    ALIX_EARLE = "alix_earle"
    JACK_DAWSON = "jack_dawson"
    JORDON_BELFORT = "jordan_belfort"


def get_personality(personality: str):
    try:
        personality = Personality(personality)
        return {
            "sacha": sacha,
            "luna": luna,
            "angele": angele,
            "makima": makima,
            "sandra": sandra,
            "alix_earle": alix_earle,
            "jack_dawson": jack_dawson,
            "jordan_belfort": jordan_belfort,
        }[personality.value]
    except Exception:
        raise Exception(f"The personality you selected ({personality}) does not exist!")
