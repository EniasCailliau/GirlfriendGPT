"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""

import requests
from steamship.invocable import PackageService, post

from chatbot import BOT_TOKEN, get_chatbot


class LangChainTelegramChatbot(PackageService):
    """Deploy LangChain chatbots and connect them to Telegram."""

    def instance_init(self) -> None:
        """Connect the instance to telegram."""
        # Unlink the previous instance
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        # Reset the bot
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates")
        # Connect the new instance
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={
                "url": f"{self.context.invocable_url}respond",
                "allowed_updates": ["message"],
            },
        )

    @post("respond", public=True)
    def respond(self, update_id: int, message: dict) -> str:
        """Telegram webhook contract."""
        message_text = message["text"]
        chat_id = message["chat"]["id"]
        try:
            conversation = get_chatbot(self.client, chat_id)
            response = conversation.predict(input=message_text)
        except Exception as e:
            response = f"Sorry, I failed: {e}"

        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": response},
        )
        return "ok"
