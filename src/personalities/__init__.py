from pathlib import Path
from typing import List, Dict

from pydantic import BaseModel

dir_path = Path(__file__).parent

# Get a list of all Python files in the directory
personality_files = dir_path.glob("*.json")


class Personality(BaseModel):
    name: str
    byline: str
    identity: List[str]
    behavior: List[str]


personalities: Dict[str, Personality] = {}
for personality_file in personality_files:
    personality = Personality.parse_file(personality_file)
    personalities[personality_file.stem] = personality


def get_personality(name: str):
    try:
        # personality_name = PersonalityName(name)
        return personalities[name]
    except Exception:
        raise Exception(f"The personality you selected ({name}) does not exist!")
