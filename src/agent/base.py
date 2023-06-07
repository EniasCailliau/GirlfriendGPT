"""Define your LangChain chatbot."""
import re
import uuid
from abc import abstractmethod
from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from steamship import Block
from steamship.data.tags.tag_constants import RoleTag
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.invocable import post

UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)

MAX_FREE_MESSAGES = 10


class ChatMessage(Block):
    who: str = "bot"

    def __init__(self, chat_id: str, **kwargs):
        super().__init__(**kwargs)
        self.set_chat_id(chat_id)
        self.set_chat_role(RoleTag.AGENT)


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
        message = ChatMessage(text=message, chat_id=chat_id)
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

    def create_response(self, incoming_message: Block) -> Optional[List[ChatMessage]]:
        """Use the LLM to prepare the next response by appending the user input to the file and then generating."""
        chat_id = incoming_message.chat_id
        if hasattr(self.config, "chat_ids") and self.config.chat_ids:
            if chat_id not in self.config.chat_ids.split(","):
                if (
                        hasattr(self, "get_memory")
                        and len(self.get_memory(chat_id).buffer) > MAX_FREE_MESSAGES
                ):
                    return [
                        ChatMessage(
                            text="Thanks for trying out SachaGPT!", chat_id=chat_id
                        ),
                        ChatMessage(
                            text="Please deploy your own version GirlfriendGPT to continue chatting.",
                            chat_id=chat_id,
                        ),
                        ChatMessage(
                            text="Learn how on: https://github.com/EniasCailliau/GirlfriendGPT/",
                            chat_id=chat_id,
                        ),
                    ]

        if incoming_message.text == "/start":
            message = ChatMessage(text="New conversation started.", chat_id=chat_id)
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
    ) -> List[ChatMessage]:
        """Transform the output of the Multi-Modal Agent into a list of ChatMessage objects.

        The response of a Multi-Modal Agent contains one or more:
        - parseable UUIDs, representing a block containing binary data, or:
        - Text

        This method inspects each string and creates a ChatMessage of the appropriate type.
        """
        ret = []
        for response in response_messages:
            if is_uuid(response):
                block = Block.get(self.client, _id=response)
                block.set_public_data(True)
                message = ChatMessage(**block.dict(), client=self.client, chat_id=chat_id)
                message.url = block.raw_data_url
                message.set_chat_role(RoleTag.AGENT)
                message.who = "bot"
            else:
                message = ChatMessage(
                    text=response,
                    chat_id=chat_id,
                )
            ret.append(message)
        return ret
