"""Tool for generating images."""
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError

NAME = "GenerateSelfie"

DESCRIPTION = """
Useful for when you need to generate a selfie showing what you're doing or where you are. 
Input: A detailed stable-diffusion prompt describing where you are and what's visible in your environment.  
Output: the UUID of the generated selfie showing what you're doing or where you are. 
"""

PLUGIN_HANDLE = "stable-diffusion"

NEGATIVE_PROMPT = ("(bonnet), (hat), (beanie), cap, (((wide shot))), (cropped head), bad framing, "
                   "out of frame, deformed, cripple, old, fat, ugly, poor, missing arm, additional arms, "
                   "additional legs, additional head, additional face, dyed hair, black and white, grayscale")


class SelfieTool(Tool):
    """Tool used to generate images from a text-prompt."""

    client: Steamship

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def run(self, prompt: str, **kwargs) -> str:
        """Generate an image using the input prompt."""
        image_generator = self.client.use_plugin(
            plugin_handle=PLUGIN_HANDLE, config={"n": 1, "size": "768x768"}
        )

        prompt = prompt + (
           "professional portrait photograph of a gorgeous Norwegian girl with long wavy blonde hair, "
           f"{prompt}"
           "((sultry flirty look)), freckles, beautiful symmetrical face, cute natural makeup, "
           "((standing outside in snowy city street)), "
           "stunning modern urban upscale environment, ultra realistic, concept art, elegant, highly detailed, "
           "intricate, sharp focus, depth of field, f/1. 8, 85mm, medium shot, mid shot, (centered image composition), "
           "(professionally color graded), ((bright soft diffused light)), volumetric fog, "
           "trending on instagram, trending on tumblr, hdr 4k, 8k"
        )
        task = image_generator.generate(
            text=prompt,
            append_output_to_file=True,
            options={"negative_prompt": NEGATIVE_PROMPT},
        )
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id

        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
