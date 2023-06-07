import logging
import os
import sys

sys.path.insert(0, "src")
from functools import partial
from typing import List
from agent.base import ChatMessage

from steamship import Steamship, SteamshipError, Block
from termcolor import colored
from api import GirlfriendGPT


class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def show_results(response_messages: List[Block]):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    for message in response_messages:
        print(message.url if message.mime_type else message.text, end="\n\n")


def main():
    Steamship()

    with Steamship.temporary_workspace() as client:
        run = partial(
            run_agent,
            agent=GirlfriendGPT(
                client=client,
                config={
                    "bot_token": "test",
                    "personality": "sacha",
                    "elevenlabs_voice_id": os.environ.get("ELEVENLABS_VOICE_ID"),
                    "elevenlabs_api_key": os.environ.get("ELEVENLABS_API_KEY"),
                    "did_api_key": os.environ.get("DID_API_KEY"),
                },
            ),
        )
        print(f"Starting Agent...")
        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )
        while True:
            prompt = input(colored(f"Prompt: ", "blue"))
            run(
                prompt=prompt,
            )


def run_agent(agent, prompt: str) -> None:
    message = ChatMessage(text=prompt, chat_id="123")
    response = agent.create_response(incoming_message=message)
    show_results(response)


if __name__ == "__main__":
    # when running locally, we can use print statements to capture logs / info.
    # as a result, we will disable python logging to run. this will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")
