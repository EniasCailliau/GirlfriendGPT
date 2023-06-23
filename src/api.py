"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
import logging
from typing import List, Optional, Type

import langchain
from langchain.agents import Tool, initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from pydantic import Field
from steamship import Steamship
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransportConfig,
    TelegramTransport,
)
from steamship.invocable import Config
from steamship.utils.repl import AgentREPL
from steamship_langchain.llms import OpenAIChat
from steamship_langchain.memory import ChatMessageHistory

from agent.base import LangChainTelegramBot
from agent.tools.search import SearchTool
from agent.tools.selfie import SelfieTool
from agent.tools.speech import GenerateSpeechTool
from agent.tools.video_message import VideoMessageTool
from personalities import get_personality
from prompts import SUFFIX, FORMAT_INSTRUCTIONS, PERSONALITY_PROMPT

TEMPERATURE = 0.7
VERBOSE = False
MEMORY_WINDOW_SIZE = 10

langchain.cache = None


class GirlFriendAIConfig(TelegramTransportConfig):
    bot_token: str = Field(
        description="Your telegram bot token.\nLearn how to create one here: "
        "https://github.com/EniasCailliau/GirlfriendGPT/blob/main/docs/register-telegram-bot.md"
    )
    elevenlabs_api_key: str = Field(
        default="", description="Optional API KEY for ElevenLabs Voice Bot"
    )
    elevenlabs_voice_id: str = Field(
        default="", description="Optional voice_id for ElevenLabs Voice Bot"
    )
    chat_ids: str = Field(
        default="", description="Comma separated list of whitelisted chat_id's"
    )
    personality: str = Field(
        description="The personality you want to deploy. Pick one of the personalities listed here: "
        "https://github.com/EniasCailliau/GirlfriendGPT/tree/main/src/personalities"
    )
    use_gpt4: bool = Field(
        False,
        description="If True, use GPT-4. Use GPT-3.5 if False. "
        "GPT-4 generates better responses at higher cost and latency.",
    )


class GirlfriendGPT(LangChainTelegramBot):
    """Deploy LangChain chatbots and connect them to Telegram."""

    config: GirlFriendAIConfig
    USED_MIXIN_CLASSES = [TelegramTransport, SteamshipWidgetTransport]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_name = "gpt-4" if self.config.use_gpt4 else "gpt-3.5-turbo"

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return GirlFriendAIConfig

    def get_agent(self, chat_id: str) -> AgentExecutor:
        llm = OpenAIChat(
            client=self.client,
            model_name=self.model_name,
            temperature=TEMPERATURE,
            verbose=VERBOSE,
        )

        tools = self.get_tools(chat_id=chat_id)

        memory = self.get_memory(client=self.client, chat_id=chat_id)

        return initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            agent_kwargs={
                "prefix": PERSONALITY_PROMPT.format(
                    personality=get_personality(self.config.personality)
                ),
                "suffix": SUFFIX,
                "format_instructions": FORMAT_INSTRUCTIONS,
            },
            verbose=VERBOSE,
            memory=memory,
        )

    def voice_tool(self) -> Optional[Tool]:
        """Return tool to generate spoken version of output text."""
        return GenerateSpeechTool(
            client=self.client,
            voice_id=self.config.elevenlabs_voice_id,
            elevenlabs_api_key=self.config.elevenlabs_api_key,
        )

    def get_memory(self, client: Steamship, chat_id: str) -> BaseChatMemory:
        return ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=ChatMessageHistory(
                client=client, key=f"history-{chat_id or 'default'}"
            ),
            return_messages=True,
        )

    def get_tools(self, chat_id: str) -> List[Tool]:
        return [
            SearchTool(self.client),
            # MyTool(self.client),
            # GenerateImageTool(self.client),
            # GenerateAlbumArtTool(self.client)
            # RemindMe(invoke_later=self.invoke_later, chat_id=chat_id),
            # VideoMessageTool(self.client),
            SelfieTool(self.client),
            VideoMessageTool(self.client),
        ]


if __name__ == "__main__":
    logging.disable(logging.ERROR)
    AgentREPL(
        GirlfriendGPT,
        method="prompt",
        agent_package_config={
            "botToken": "not-a-real-token-for-local-testing",
            "personality": "sacha",
        },
    ).run()
