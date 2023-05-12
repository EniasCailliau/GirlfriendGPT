"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
from typing import List, Optional

from steamship import Steamship, Block
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import post

from agent.get_agent import get_agent
from agent.utils import is_valid_uuid, make_image_public


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
            return [
                ChatMessage(
                    text="New conversation started.",
                    chat_id=incoming_message.get_chat_id(),
                )
            ]

        conversation = get_agent(
            self.client,
            chat_id=incoming_message.get_chat_id(),
            invoke_later=self._invoke_later,
        )
        response = conversation.run(input=incoming_message.text)

        return self.agent_output_to_chat_messages(
            chat_id=incoming_message.get_chat_id(), agent_output=response
        )

    def agent_output_to_chat_messages(
        self, chat_id: str, agent_output: List[str]
    ) -> List[ChatMessage]:
        """Transform the output of the Multi-Modal Agent into a list of ChatMessage objects.

        The response of a ulti-Modal Agent contains one or more:
        - parseable UUIDs, representing a block containing binary data, or:
        - Text

        This method inspects each string and creates a ChatMessage of the appropriate type.
        """
        ret = []
        for part_response in agent_output:
            if is_valid_uuid(part_response):
                block = Block.get(self.client, _id=part_response)
                message = ChatMessage.from_block(
                    block,
                    chat_id=chat_id,
                )
                message.url = make_image_public(self.client, block)

            else:
                message = ChatMessage(
                    client=self.client,
                    chat_id=chat_id,
                    text=part_response,
                )

            ret.append(message)
        return ret


if __name__ == "__main__":
    client = Steamship()
    bot = LangChainTelegramChatbot(client=client, config={"bot_token": "test"})
    answer = bot.create_response(
        ChatMessage(text="Hi bro, generate me an image of a cat", chat_id="2")
    )
    print("answer", answer)
