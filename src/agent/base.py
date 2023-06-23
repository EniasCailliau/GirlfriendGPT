"""Define your LangChain chatbot."""
import logging
import re
import uuid
from abc import abstractmethod
from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.memory.chat_memory import BaseChatMemory
from langchain.tools import Tool
from steamship import Block, Steamship
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransportConfig,
    TelegramTransport,
)
from steamship.agents.schema import Agent, AgentContext, Metadata
from steamship.agents.service.agent_service import AgentService

UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)

MAX_FREE_MESSAGES = 10


def is_uuid(uuid_to_test: str, version: int = 4) -> bool:
    """Check a string to see if it is actually a UUID."""
    lowered = uuid_to_test.lower()
    try:
        return str(uuid.UUID(lowered, version=version)) == lowered
    except ValueError:
        return False


class LangChainTelegramBot(AgentService):
    config: TelegramTransportConfig

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_mixin(
            SteamshipWidgetTransport(client=self.client, agent_service=self, agent=None)
        )

        self.add_mixin(
            TelegramTransport(
                client=self.client, config=self.config, agent_service=self, agent=None
            )
        )

    @abstractmethod
    def get_agent(self, chat_id: str) -> AgentExecutor:
        raise NotImplementedError()

    @abstractmethod
    def get_memory(self, client: Steamship, chat_id: str) -> BaseChatMemory:
        raise NotImplementedError()

    @abstractmethod
    def get_tools(self, chat_id: str) -> List[Tool]:
        raise NotImplementedError()

    def voice_tool(self) -> Optional[Tool]:
        return None

    def is_verbose_logging_enabled(self):
        return True

    def limit_usage(self, chat_id: str):
        if hasattr(self.config, "chat_ids") and self.config.chat_ids:
            if chat_id not in self.config.chat_ids.split(","):
                if (
                    hasattr(self, "get_memory")
                    and len(self.get_memory(client=self.client, chat_id=chat_id).buffer)
                    > MAX_FREE_MESSAGES
                ):
                    return [
                        Block(text="Thanks for trying out SachaGPT!"),
                        Block(
                            text="Please deploy your own version GirlfriendGPT to continue chatting."
                        ),
                        Block(
                            text="Learn how on: https://github.com/EniasCailliau/GirlfriendGPT/"
                        ),
                    ]

    def respond(
        self, incoming_message: Block, chat_id: str, client: Steamship
    ) -> List[Block]:

        # self.limit_usage(chat_id)

        if incoming_message.text == "/start":
            return [Block(text="New conversation started.")]

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

        return [
            Block.get(self.client, _id=response)
            if is_uuid(response)
            else Block(text=response)
            for response in response_messages
        ]

    def run_agent(self, agent: Agent, context: AgentContext):
        chat_id = context.metadata.get("chat_id")

        incoming_message = context.chat_history.last_user_message
        output_messages = self.respond(incoming_message, chat_id, context.client)
        for func in context.emit_funcs:
            logging.info(f"Emitting via function: {func.__name__}")
            func(output_messages, context.metadata)

    def prompt(self, prompt: str) -> str:
        """Run an agent with the provided text as the input."""

        context = AgentContext.get_or_create(self.client, {"id": str(uuid.uuid4())})
        context.chat_history.append_user_message(prompt)

        output = ""

        def sync_emit(blocks: List[Block], meta: Metadata):
            nonlocal output
            for block in blocks:
                if not block.is_text():
                    block.set_public_data(True)
                    output += f"({block.mime_type}: {block.raw_data_url})\n"
                else:
                    output += f"{block.text}\n"

        context.emit_funcs.append(sync_emit)
        self.run_agent(None, context)  # Maybe I override this
        return output
