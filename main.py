import logging
import os
import sys

sys.path.insert(0, "src")
from functools import partial
from typing import List

from steamship.experimental.transports.chat import ChatMessage
from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from termcolor import colored
from api import LangChainTelegramChatbot


def show_results(response_messages: List[ChatMessage]):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    for message in response_messages:
        if message.mime_type:
            print(message.url, end="\n\n")
        else:
            print(message.text, end="\n\n")


class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def main():
    Steamship()

    with Steamship.temporary_workspace() as client:
        run = partial(
            run_agent,
            agent=LangChainTelegramChatbot(client=client,
                                           config={"bot_token": "test",
                                                   "elevenlabs_voice_id": os.environ.get(
                                                       "ELEVENLABS_VOICE_ID"),
                                                   "elevenlabs_api_key": os.environ.get(
                                                       "ELEVENLABS_API_KEY")}),
        )
        print(f"Starting Agent...")

        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )

        count = 1

        while True:
            print(f"----- Agent Run {count} -----")
            prompt = input(colored(f"Prompt: ", "blue"))
            run(
                # client,
                prompt=prompt,
            )
            count += 1


def run_agent(agent, prompt: str, as_api: bool = False) -> None:
    # For Debugging
    if not agent.is_verbose_logging_enabled():  # display progress when verbose is False
        print("Running: ", end="")
        with ship_spinner():
            response = agent.create_response(
                incoming_message=ChatMessage(text=prompt, chat_id="123")
            )
    else:
        response = agent.create_response(
            incoming_message=ChatMessage(text=prompt, chat_id="123")
        )

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
