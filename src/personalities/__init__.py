from enum import Enum
import os
import glob
import sys

# Get the current directory
dir_path = os.path.dirname(os.path.realpath(__file__))

# Get a list of all Python files in the directory
python_files = glob.glob(os.path.join(dir_path, "*.py"))

# Add the directory of the __init__.py file to the path to be able to import the other files
sys.path.append(dir_path)

# Import all the Python files and add their contents to a dictionary
personalities: dict[str, str] = {}
for file in python_files:
    # Ignore the __init__.py file
    if file != __file__ and not file.endswith("__init__.py"):
        module_name = os.path.splitext(os.path.basename(file))[0]
        module = __import__(module_name)
        personalities[module_name] = getattr(module, module_name)

# Add all the personalities to the __all__ list
__all__ = list(personalities.keys()) + ["get_personality", "get_available_personalities"]

# Dynamically construct the enum Personality based on the personalities keys
# We use the uppercased version of the personality name as the enum key, and the personality name as the value

Personality= Enum("Personality", {k.upper(): k for k in personalities.keys()})

def get_personality(personality: str):
    try:
        personality = Personality(personality)
        return personalities[personality.value]
    except Exception:
        raise Exception(f"The personality you selected ({personality}) does not exist!")

def get_available_personalities(include_short_descriptions=False):

    # The current implementation for the descriptions is quite basic, but it works with all current examples
    # But it expects a certain format, which is probably not guaranteed for future examples
    if include_short_descriptions:
        # Get the short description for each personality, additionally get the name of the personality
        short_descriptions = {}
        for personality in personalities:
            # The variable contains a text describing the personality.
            # We can use the first line after the first comma which is a short description.
            # Additionally capitalize the first letter of the short description
            short_description = ",".join(personalities[personality].strip().split("\n")[0].split(",")[1:]).strip()
            short_description = short_description[0].upper() + short_description[1:]
            # To get the name we get the text between "You are" and the next comma
            name = personalities[personality].strip().split("\n")[0].split("You are")[1].split(",")[0].strip()

            # Add the short description and the name to the dictionary
            short_descriptions[personality] = (name, short_description)
        # We now map it to "Name - Short description"
        return [f"{personality} - {short_descriptions[personality][0]} - {short_descriptions[personality][1]}" for personality in personalities.keys()]
    else:
        return list(personalities.keys())