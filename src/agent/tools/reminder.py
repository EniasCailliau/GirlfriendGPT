"""Tool for scheduling reminders."""
import logging
from typing import Callable

from langchain.agents import Tool
from pydantic import BaseModel, Field
from pytimeparse.timeparse import timeparse


class ToolRequest(BaseModel):
    @classmethod
    def get_json(cls):
        return {
            key: info["description"] for key, info in cls.schema()["properties"].items()
        }


class ReminderRequest(ToolRequest):
    """Provide structure for tool invocation for the LLM."""

    after: str = Field(description="time delta")
    reminder: str = Field(description="reminder message to send to the user")


EXAMPLES = [
    ReminderRequest(after="15s", reminder="turn off the lights"),
    ReminderRequest(after="60m", reminder="file your taxes"),
    ReminderRequest(after="2h5m", reminder="send a message to your wife about dinner"),
]

NAME: str = "REMIND"

EXAMPLES_STR = "\n".join([example.json() for example in EXAMPLES])
DESCRIPTION: str = f"""Used to schedule reminders for the user at a future point in time. Input: time time delata and the reminder. Please use the following JSON format as Input:  
{ReminderRequest.get_json()}.
            
Example(s):
{EXAMPLES_STR}""".replace(
    "{", "{{"
).replace(
    "}", "}}"
)


class RemindMe(Tool):
    """Tool used to schedule reminders via the Steamship Task system."""

    invoke_later: Callable
    chat_id: str

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def __init__(self, invoke_later: Callable, chat_id: str):
        super().__init__(
            name="REMIND",
            func=self.run,
            description=DESCRIPTION,
            invoke_later=invoke_later,
            chat_id=chat_id,
        )

    def run(self, prompt, **kwargs) -> str:
        """Respond to LLM prompts."""
        logging.info(f"[remind-me] prompt: {prompt}")
        if isinstance(prompt, dict):
            req = ReminderRequest.parse_obj(prompt)
        elif isinstance(prompt, str):
            prompt = prompt.replace("'", '"')
            req = ReminderRequest.parse_raw(prompt)
        else:
            return "Tool failure. Could not handle request. Sorry."

        self._schedule(req)
        return "This is the output"

    def _schedule(self, req: ReminderRequest) -> str:
        after_seconds = timeparse(req.after)
        logging.info(f"scheduling after {after_seconds}s, message {req.reminder}")

        self.invoke_later(
            delay_ms=after_seconds * 1_000,
            message=req.reminder,
            chat_id=self.chat_id,
        )

        logging.info(f"scheduling {after_seconds * 1_000}, message {req.reminder}")

        return "Your reminder has been scheduled."
