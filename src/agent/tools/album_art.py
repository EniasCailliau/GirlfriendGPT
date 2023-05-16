"""Tool for generating album art.

The purpose of this tool is to illustrate how to wrap the GenerateImageTool
with a custom tool description & some prompt engineering to steer the image
one way or another.

The GenerateImageTool leaves the user + LLM in complete control of the image
generation prompt... but what if you wanted to make sure the prompt was:

- A particular style?
- A particular mood?
- Something else entirely, involving web scraping and other operations?

You can do that by wrapping the GenerateImageTool, as you see here, and then
sending in your own custom prompt.
"""
import json
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.data.plugin.plugin_instance import PluginInstance
from .image import GenerateImageTool

NAME = "GenerateAlbumArt"

DESCRIPTION = """
Useful for when you need to generate album art. 
Input: A description of the album that needs art
Output: the UUID of a generated image
"""


class GenerateAlbumArtTool(Tool):
    """Tool used to generate album art from a album description."""

    client: Steamship
    tool: GenerateImageTool

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME,
            func=self.run,
            description=DESCRIPTION,
            client=client,
            tool=GenerateImageTool(client),
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompt."""

        # Here we create a NEW prompt, which is based on the prompt provided
        # to this tool, but including extra terms.
        image_gen_prompt = f"album art, 4k, high def, pop art, professional, high quality, award winning, grammy, platinum, {prompt}"

        # Then we just return the results of the wrapped GenerateImageTool,
        # passing it the new prompt that we created.
        return self.tool.run(image_gen_prompt)
