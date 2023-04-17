"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""

import requests
from steamship.invocable import PackageService, post

from chatbot import BOT_TOKEN, get_chatbot, get_vectorstore
from response_cache import already_responded, record_response


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

    def send_message(self, chat_id: str, message: str) -> None:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": chat_id, "text": message},
        )

    @post("respond", public=True)
    def respond(self, update_id: int, message: dict) -> str:
        """Telegram webhook contract."""
        chat_id = message["chat"]["id"]
        try:
            message_text = message["text"]
            message_id = message["message_id"]

            if message_text == "/start":
                self.send_message(chat_id, "New conversation started.")
                return "ok"

            if message_text == "/reset":
                get_vectorstore(self.client, chat_id).index.reset()
                self.send_message(chat_id, "Reset conversation.")
                return "ok"

            if already_responded(self.client, chat_id, message_id):
                return "ok"

            record_response(self.client, chat_id, message_id)

            try:
                conversation = get_chatbot(self.client, chat_id)
                response = conversation.predict(input=message_text)
            except Exception as e:
                response = f"Sorry, I failed: {e}"

            self.send_message(chat_id, response)
            return "ok"
        except Exception as e:
            self.send_message(chat_id, f"I failed {e}")
            return "nok"

