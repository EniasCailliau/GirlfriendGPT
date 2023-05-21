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

NEGATIVE_PROMPT = "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face, blurry, draft, grainy"


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

        # logging.info(f"[{self.name}] {prompt}")
        # if not isinstance(prompt, str):
        #     prompt = json.dumps(prompt)

        prompt = ("A selfie of a futuristic, human-like robot looking seductive into the lens of her phone"
                  "detailed clothing, hyperrealistic, fantasy, surrealist, highly detailed, sharp focus, sci-fi, "
                  "stunningly beautiful, dystopian, cinematic lighting, dark, 4K, dramatic lighting")
        task = image_generator.generate(text=prompt, append_output_to_file=True,
                                        options={"negative_prompt": NEGATIVE_PROMPT}, )
        task.wait()
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id

        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")
