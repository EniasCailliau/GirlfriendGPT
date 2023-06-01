"""Define your LangChain chatbot."""
import re
import uuid
from abc import abstractmethod
from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from steamship import Block
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.invocable import post

UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)


def is_uuid(uuid_to_test: str, version: int = 4) -> bool:
    """Check a string to see if it is actually a UUID."""
    lowered = uuid_to_test.lower()
    try:
        return str(uuid.UUID(lowered, version=version)) == lowered
    except ValueError:
        return False


class LangChainAgentBot(TelegramBot):
    @abstractmethod
    def get_agent(self, chat_id: str) -> AgentExecutor:
        raise NotImplementedError()

    def voice_tool(self) -> Optional[Tool]:
        return None

    def is_verbose_logging_enabled(self):
        return True

    @post("send_message")
    def send_message(self, message: str, chat_id: str) -> str:
        """Send a message to Telegram.

        Note: This is a private endpoint that requires authentication."""
        message = Block(text=message)
        message.set_chat_id(chat_id)  # TODO: chat_id part of __init__?
        self.telegram_transport.send([message], metadata={})
        return "ok"

    def _invoke_later(self, delay_ms: int, message: str, chat_id: str):
        self.invoke_later(
            "send_message",
            delay_ms=delay_ms,
            arguments={
                "message": message,
                "chat_id": chat_id,
            },
        )

    def create_response(self, incoming_message: Block) -> Optional[List[Block]]:
        """Use the LLM to prepare the next response by appending the user input to the file and then generating."""
        chat_id = incoming_message.chat_id
        if incoming_message.text == "/start":
            message = Block(
                text="New conversation started.",
            )
            message.set_chat_id(chat_id)
            return [message]

        conversation = self.get_agent(
            chat_id=chat_id,
        )
        response = conversation.run(input=incoming_message.text)
        response = UUID_PATTERN.split(response)
        response = [re.sub(r"^\W+", "", el) for el in response]
        if audio_tool := self.voice_tool():
            response_messages = []
            for message in response:
                response_messages.append(message)
                if not is_uuid(message):
                    audio_uuid = audio_tool.run(message)
                    response_messages.append(audio_uuid)
        else:
            response_messages = response

        return self.agent_output_to_chat_messages(
            chat_id=chat_id, response_messages=response_messages
        )

    def agent_output_to_chat_messages(
        self, chat_id: str, response_messages: List[str]
    ) -> List[Block]:
        """Transform the output of the Multi-Modal Agent into a list of ChatMessage objects.

        The response of a Multi-Modal Agent contains one or more:
        - parseable UUIDs, representing a block containing binary data, or:
        - Text

        This method inspects each string and creates a ChatMessage of the appropriate type.
        """
        ret = []
        for response in response_messages:
            if is_uuid(response):
                message = Block.get(self.client, _id=response)
                message.set_chat_id(chat_id)
                message = message.set_public_data(True)
                message.url = message.raw_data_url

            else:
                message = Block(
                    client=self.client,
                    text=response,
                )
                message.set_chat_id(
                    chat_id=chat_id,
                )

            ret.append(message)
        return ret
