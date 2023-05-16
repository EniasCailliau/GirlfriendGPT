"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
from typing import List

from langchain.agents import Tool, initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship_langchain.llms import OpenAIChat
from steamship_langchain.memory import ChatMessageHistory

from agent.base import LangChainAgentBot
from agent.tools.image import GenerateImageTool
from agent.tools.reminder import RemindMe
from agent.tools.search import SearchTool

MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4.0"
TEMPERATURE = 0.7
VERBOSE = True


class LangChainTelegramChatbot(LangChainAgentBot, TelegramBot):
    """Deploy LangChain chatbots and connect them to Telegram."""

    def get_agent(self, chat_id: str) -> AgentExecutor:
        llm = OpenAIChat(
            client=self.client,
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            verbose=VERBOSE,
        )

        tools = self.get_tools(chat_id=chat_id)

        memory = self.get_memory(chat_id)

        return initialize_agent(
            tools,
            llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=memory,
        )

    def get_memory(self, chat_id):
        if self.context and self.context.invocable_instance_handle:
            my_instance_handle = self.context.invocable_instance_handle
        else:
            my_instance_handle = "local-instance-handle"
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=ChatMessageHistory(
                client=self.client, key=f"history-{chat_id}-{my_instance_handle}"
            ),
            return_messages=True,
        )
        return memory

    def get_tools(self, chat_id: str) -> List[Tool]:
        return [
            SearchTool(self.client),
            # MyTool(self.client),
            GenerateImageTool(self.client),
            # GenerateAlbumArtTool(self.client)
            RemindMe(invoke_later=self.invoke_later, chat_id=chat_id),
        ]
