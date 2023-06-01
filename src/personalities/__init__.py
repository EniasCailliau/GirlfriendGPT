from .luna import luna
from .sacha import sacha
from .sandra import sandra
from .angele import angele
from .makima import makima

__all__ = [
    "sacha",
    "luna",
    "angele",
    "makima",
    "sandra",
  "angele",
    "get_personality"
]


def get_personality(name: str):
    try:
        return {
            "luna": luna,
            "sacha": sacha,
            "Angèle": angele,
            "Makima": makima
            "sandra": sandra,
        }[name]
    except Exception:
        raise Exception("The personality you selected does not exist!")
