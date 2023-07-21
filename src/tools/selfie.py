"""Tool for generating images."""
from typing import Any, List, Union

from steamship import Block, Task
from steamship.agents.schema import AgentContext
from steamship.agents.tools.image_generation.stable_diffusion import StableDiffusionTool
from steamship.utils.repl import ToolREPL

NEGATIVE_PROMPT = (
    "(nsfw:1.4),easynegative,(deformed, distorted,disfigured:1.3), poorly drawn, bad anatomy, wrong anatomy, extra limb,"
    " missing limb, (mutated hands and finger:1.4), disconnected limbs, mutation, mutated, ugly, "
    "disgusting, blurry, amputation"
)

PROMPT_TEMPLATE = (
    "Pixar style {description}, professional selfie of a gorgeous Norwegian girl with long wavy blonde hair, "
    "((sultry flirty look)), freckles, beautiful symmetrical face, cute natural makeup, "
    "woman((upper body selfie, happy)), masterpiece, best quality, ultra-detailed, solo, "
    "outdoors, (night), mountains, nature, (stars, moon) cheerful, happy, backpack, "
    "analog style (look at viewer:1.2) (skin texture) (film grain:1.3), (warm hue, warm tone)"
    "intricate, sharp focus, depth of field, f/1. 8, 85mm, medium shot, mid shot, "
    "(centered image composition), (professionally color graded)"
    "trending on instagram, trending on tumblr, hdr 4k, 8k"
)


class SelfieTool(StableDiffusionTool):
    """Tool to generate selfies for your companion.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    name: str = "SelfieTool"
    human_description: str = "Generates a selfie of yourself. Provide a text prompt that describes what you are doing"
    agent_description: str = None

    def run(
        self, tool_input: List[Block], context: AgentContext, **kwargs
    ) -> Union[List[Block], Task[Any]]:
        modified_inputs = [
            Block(text=PROMPT_TEMPLATE.format(description=block.text))
            for block in tool_input
        ]

        if not modified_inputs:
            modified_inputs = [Block(text=PROMPT_TEMPLATE.format(description="selfie"))]

        # Create the Stable Diffusion tool we want to wrap
        stable_diffusion_tool = StableDiffusionTool()

        # Now return the results of running Stable Diffusion on those modified prompts.
        return stable_diffusion_tool.run(
            modified_inputs,
            context,
            options={
                "negative_prompt": NEGATIVE_PROMPT,
                "guidance_scale": 7,
                "num_inference_steps": 40,
            },
        )


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    ToolREPL(SelfieTool()).run()
