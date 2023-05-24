from .luna import luna
from .sacha import sacha

__all__ = [
    "sacha",
    "luna",
    "get_personality"
]


def get_personality(name: str):
    try:
        return {
            "luna": luna,
            "sacha": sacha
        }[name]
    except Exception:
        raise Exception("The personality you selected does not exist!")
