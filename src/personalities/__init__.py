from .luna import luna
from .sacha import sacha
from sandra.py import sandra

__all__ = [
    "sacha",
    "luna",
    "sandra",
    "get_personality"
]


def get_personality(name: str):
    try:
        return {
            "luna": luna,
            "sacha": sacha,
            "sandra": sandra
        }[name]
    except Exception:
        raise Exception("The personality you selected does not exist!")
