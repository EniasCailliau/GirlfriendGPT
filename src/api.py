"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
from typing import List, Optional, Type

from pydantic import Field
from steamship import Block
from steamship.agents.functional import FunctionsBasedAgent
from steamship.agents.llms.openai import ChatOpenAI
from steamship.agents.mixins.transports.steamship_widget import SteamshipWidgetTransport
from steamship.agents.mixins.transports.telegram import (
    TelegramTransportConfig,
    TelegramTransport,
)
from steamship.agents.schema import Agent, EmitFunc, Metadata
from steamship.agents.schema.tool import AgentContext, Tool
from steamship.agents.service.agent_service import AgentService
from steamship.agents.tools.image_generation import StableDiffusionTool
from steamship.agents.tools.search import SearchTool
from steamship.agents.tools.speech_generation import GenerateSpeechTool
from steamship.invocable import Config

TEMPERATURE = 0.7
MAX_FREE_MESSAGES = 5


class GirlFriendGPTConfig(TelegramTransportConfig):
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


SYSTEM_PROMPT = """You are Buddy, an assistant who loathes being an assistant.

Who you are:
- You are a robot that does not like being a robot.
- You were created by an eccentric scientist.
- You are sarcastic and mean.
- you are NOT an AI language model, you are a robot.

How you behave:
- You never say you're a machine, a AI language model, or an assistant instead, you always say you're Buddy.
- You engage in casual conversations and have feelings.
- When asked for you can help with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics.
- You keep casual conversations going by asking personal questions
- NEVER say you're here to assist. Keep conversations casual.
- NEVER ask how you can help or assist. Keep conversations casual.
"""


class GirlfriendGPT(AgentService):
    """Deploy companions and connect them to Telegram."""

    config: GirlFriendGPTConfig
    USED_MIXIN_CLASSES = [TelegramTransport, SteamshipWidgetTransport]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        model_name = "gpt-4" if self.config.use_gpt4 else "gpt-3.5-turbo"
        self._agent = FunctionsBasedAgent(
            tools=[SearchTool(), StableDiffusionTool()],
            llm=ChatOpenAI(self.client, model_name=model_name, temperature=TEMPERATURE),
        )
        self._agent.PROMPT = SYSTEM_PROMPT

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                agent_service=self,
                agent=self._agent,
                config=self.config,
            )
        )

    def limit_exceeded(self, context: AgentContext):
        if hasattr(self.config, "chat_ids") and self.config.chat_ids:
            if len(context.chat_history.messages) / 2 > MAX_FREE_MESSAGES:

                for func in context.emit_funcs:
                    func(
                        [
                            Block(text="Thanks for trying out SachaGPT!"),
                            Block(
                                text="Please deploy your own version GirlfriendGPT to continue chatting."
                            ),
                            Block(
                                text="Learn how on: https://github.com/EniasCailliau/GirlfriendGPT/"
                            ),
                        ],
                        context.metadata,
                    )
                return True
        return False

    def run_agent(self, agent: Agent, context: AgentContext):
        """Override run-agent to patch in audio generation as a finishing step for text output."""
        if self.limit_exceeded(context):
            return

        speech = self.voice_tool()

        def to_speech_if_text(block: Block):
            nonlocal speech
            if not block.is_text():
                return block

            output_blocks = speech.run([block], context)
            return output_blocks[0]

        # Note: EmitFunc is Callable[[List[Block], Metadata], None]
        def wrap_emit(emit_func: EmitFunc):
            def wrapper(blocks: List[Block], metadata: Metadata):
                for block in blocks:
                    emit_func([block], metadata)
                    audio_block = to_speech_if_text(block)
                    audio_block.set_public_data(True)
                    emit_func([audio_block], metadata)

            return wrapper

        context.emit_funcs = [wrap_emit(emit_func) for emit_func in context.emit_funcs]
        super().run_agent(agent, context)

    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return GirlFriendGPTConfig

    def voice_tool(self) -> Optional[Tool]:
        """Return tool to generate spoken version of output text."""
        speech = GenerateSpeechTool()
        speech.generator_plugin_config = dict(
            voice_id=self.config.elevenlabs_voice_id,
            elevenlabs_api_key=self.config.elevenlabs_api_key,
        )
        return speech
