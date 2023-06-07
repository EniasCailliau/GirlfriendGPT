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

        prompt = "sfw, best quality, ultra high res, ultra-detailed face and eyes, detailed body, detailed clothes, kodak portra 400, (photorealistic:1. 4), pretty lady in the city, detailed background, (street in city:1. 2), (black shirt:1. 4), plaid skirt, (short blonde hair:1. 4), looking back, close mouth, blush, narrow waist, light green eyes, make-up <lora:aigirl:0. 6>, professional light, face focus, (light on the face)"
        task = image_generator.generate(
            text=prompt,
            append_output_to_file=True,
            options={
                "negative_prompt": NEGATIVE_PROMPT,
                "guidance_scale": 7,
                "num_inference_steps": 40,
                "scheduler": "K_EULER_ANCESTRAL",
            },
        )
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id

        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
