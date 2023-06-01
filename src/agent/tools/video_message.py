"""Tool for generating images."""
import logging
import time

import requests
from langchain.agents import Tool
from steamship import Steamship, Block, MimeTypes, File

NAME = "VideoMessage"

DESCRIPTION = """
Useful for when you want to send a video message to answer a question. 
Input: The message you want to say in a video message.  
Output: the UUID of the generated video message. 
"""


class VideoMessageTool(Tool):
    """Tool used to generate images from a text-prompt."""

    client: Steamship
    api_key: str

    def __init__(self, client: Steamship, api_key: str):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client, api_key=api_key
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def run(self, prompt: str, **kwargs) -> str:
        """Generate a video."""
        headers = {
            'Authorization': f"Basic {self.api_key}"
        }
        response = requests.post("https://api.d-id.com/talks",
                                 json={
                                     "source_url": "https://raw.githubusercontent.com/EniasCailliau/GirlfriendGPT/main/docs/img/personalities/sneako.png",
                                     "script": {
                                         "type": "text",
                                         "input": prompt,
                                         "provider": {
                                             "type": "microsoft",
                                             "voice_id": "en-US-AriaNeural",
                                             "voice_config": {
                                                 "style": "Chat"
                                             }
                                         }
                                     },
                                     "config": {
                                         "driver_expressions": {
                                             "expressions": [
                                                 {
                                                     "start_frame": 0,
                                                     "expression": "happy",
                                                     "intensity": 1.0
                                                 }
                                             ]
                                         },
                                         "stitch": True
                                     }

                                 },
                                 headers=headers).json()

        talk_id = response["id"]
        status = response["status"]

        while status != "done":
            response = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers).json()
            status = response["status"]
            time.sleep(1)

        f = File.create(self.client, content="test")
        blocks = [Block.create(client=self.client,
                               file_id=f.id,
                               url=response["result_url"],
                               mime_type=MimeTypes.MP4_VIDEO)]
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
        return blocks[0].id
