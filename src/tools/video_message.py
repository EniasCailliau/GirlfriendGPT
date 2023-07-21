"""Tool for generating images."""

from steamship import Steamship
from steamship.agents.tools.video_generation import DIDVideoGeneratorTool
from steamship.utils.repl import ToolREPL


class VideoMessageTool(DIDVideoGeneratorTool):
    """Tool to generate selfies for your companion.

    This example illustrates wrapping a tool (StableDiffusionTool) with a fixed prompt template that is combined with user input.
    """

    name: str = "VideoMessageTool"
    human_description: str = "Generate a video message of yourself saying a message. Provide a text prompt that sends your message"
    agent_description: str = None

    def __init__(self, client: Steamship):
        super().__init__(
            client=client,
            source_url="https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/617d79ac-2201-4f06-b43e-195f78a5fbfb/width=1472/3.1-066.jpeg",
            stitch=True,
            voice_provider="microsoft",
            voice_id="en-US-AshleyNeural",
            voice_style="Default",
            expressions=[
                DIDVideoGeneratorTool.Expression(
                    start_frame=0,
                    expression=DIDVideoGeneratorTool.Expression.Expressions.SURPRISE,
                    intensity=1.0,
                ),
                DIDVideoGeneratorTool.Expression(
                    start_frame=50,
                    expression=DIDVideoGeneratorTool.Expression.Expressions.HAPPY,
                    intensity=1.0,
                ),
                DIDVideoGeneratorTool.Expression(
                    start_frame=100,
                    expression=DIDVideoGeneratorTool.Expression.Expressions.SERIOUS,
                    intensity=1.0,
                ),
                DIDVideoGeneratorTool.Expression(
                    start_frame=150,
                    expression=DIDVideoGeneratorTool.Expression.Expressions.NEUTRAL,
                    intensity=1.0,
                ),
            ],
            transition_frame=20,
        )


if __name__ == "__main__":
    print("Try running with an input like 'penguin'")
    with Steamship.temporary_workspace() as client:
        ToolREPL(VideoMessageTool(client=client)).run()
