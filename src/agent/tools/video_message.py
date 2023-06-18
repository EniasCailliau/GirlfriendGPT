"""Tool for generating images."""
import logging

from langchain.agents import Tool
from steamship import Steamship, Block, SteamshipError

NAME = "VideoMessage"

DESCRIPTION = """
Useful for when you want to send a video message. 
Input: The message you want to say in a video.  
Output: the UUID of the generated video. 
"""

PLUGIN_HANDLE = "did-video-generator"


class VideoMessageTool(Tool):
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
        """Generate a video."""
        video_generator = self.client.use_plugin(PLUGIN_HANDLE)
        print("Video generator")
        task = video_generator.generate(
            text=prompt,
            append_output_to_file=True,
            options={
                "source_url": "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/617d79ac-2201-4f06-b43e-195f78a5fbfb/width=1472/3.1-066.jpeg",
                "stitch": True,
                "provider": {
                    "type": "microsoft",
                    "voice_id": "en-US-AshleyNeural",
                    "voice_config": {"style": "Default"},
                    "expressions": [
                        {"start_frame": 0, "expression": "surprise", "intensity": 1.0},
                        {"start_frame": 50, "expression": "happy", "intensity": 1.0},
                        {"start_frame": 100, "expression": "serious", "intensity": 0.6},
                        {"start_frame": 150, "expression": "neutral", "intensity": 1.0},
                    ],
                },
                "transition_frames": 20,
            },
        )
        task.wait(retry_delay_s=3)
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")


if __name__ == "__main__":
    with Steamship.temporary_workspace() as client:
        tool = VideoMessageTool(client=client)
        id = tool.run("Unlike anything you experienced before")
        b = Block.get(client=client, _id=id)
        b.set_public_data(True)
        print(b.raw_data_url)
