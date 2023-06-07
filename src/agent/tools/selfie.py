"""Tool for generating images."""
import logging

from langchain.agents import Tool
from steamship import Steamship, Block
from steamship.base.error import SteamshipError

NAME = "GenerateSelfie"

DESCRIPTION = """
Useful for when you need to generate a selfie showing what you're doing or where you are. 
Input: A detailed stable-diffusion prompt describing where you are and what's visible in your environment.  
Output: the UUID of the generated selfie showing what you're doing or where you are. 
"""

PLUGIN_HANDLE = "stable-diffusion"

NEGATIVE_PROMPT = " (nsfw:1.4),easynegative,(deformed, distorted,disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, (mutated hands and finger:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation"


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
            "professional selfie of a gorgeous Norwegian girl with long wavy blonde hair, "
            "((sultry flirty look)), freckles, beautiful symmetrical face, cute natural makeup, "
            "woman((upper body selfie, happy)), masterpiece, best quality, ultra-detailed, solo, "
            "outdoors, (night), mountains, nature, (stars, moon) cheerful, happy, backpack, "
            "analog style (look at viewer:1.2) (skin texture) (film grain:1.3), (warm hue, warm tone)"
            "intricate, sharp focus, depth of field, f/1. 8, 85mm, medium shot, mid shot, "
            "(centered image composition), (professionally color graded)"
            "trending on instagram, trending on tumblr, hdr 4k, 8k"
        )
        task = image_generator.generate(
            text=prompt,
            append_output_to_file=True,
            options={
                "negative_prompt": NEGATIVE_PROMPT,
                "guidance_scale": 7,
                "num_inference_steps": 40,
            },
        )
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id

        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
