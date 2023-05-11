"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
from typing import List, Optional

from steamship import Steamship
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import post

from agent.get_agent import get_agent


class LangChainTelegramChatbot(TelegramBot):
    """Deploy LangChain chatbots and connect them to Telegram."""

    @post("send_message")
    def send_message(self, message: str, chat_id: str) -> str:
        self.telegram_transport.send([ChatMessage(text=message, chat_id=chat_id)])
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

    def create_response(
            self, incoming_message: ChatMessage
    ) -> Optional[List[ChatMessage]]:
        """Use the LLM to prepare the next response by appending the user input to the file and then generating."""
        if incoming_message.text == "/start":
            return [ChatMessage(text="New conversation started.",
                                chat_id=incoming_message.get_chat_id())]

        conversation = get_agent(self.client,
                                 chat_id=incoming_message.get_chat_id(),
                                 invoke_later=self._invoke_later)
        response = conversation.run(input=incoming_message.text)

        return [ChatMessage(text=response, chat_id=incoming_message.get_chat_id())]


if __name__ == '__main__':
    client = Steamship()
    bot = LangChainTelegramChatbot(client=client, config={"bot_token": "test"})
    answer = bot.create_response(ChatMessage(text="Hi bro", chat_id="2"))
    print("answer", answer)
