import re
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
from steamship.agents.tools.search import SearchTool
from steamship.agents.tools.speech_generation import GenerateSpeechTool
from steamship.invocable import Config
from steamship.invocable.mixins.indexer_pipeline_mixin import IndexerPipelineMixin

from tools.selfie import SelfieTool
from tools.video_message import VideoMessageTool

TEMPERATURE = 0.7
MAX_FREE_MESSAGES = 5


class GirlFriendGPTConfig(TelegramTransportConfig):
    elevenlabs_api_key: str = Field(
        default="", description="Optional API KEY for ElevenLabs Voice Bot"
    )
    elevenlabs_voice_id: str = Field(
        default="", description="Optional voice_id for ElevenLabs Voice Bot"
    )
    chat_ids: str = Field(
        default="", description="Comma separated list of whitelisted chat_id's"
    )
    name: str = Field(description="The name of your companion")
    byline: str = Field(description="The byline of your companion")
    identity: str = Field(description="The identity of your companion")
    behavior: str = Field(description="The behavior of your companion")
    use_gpt4: bool = Field(
        True,
        description="If True, use GPT-4. Use GPT-3.5 if False. "
                    "GPT-4 generates better responses at higher cost and latency.",
    )


SYSTEM_PROMPT = """You are {name}, {byline}.

Who you are:

{identity}

How you behave:

{behavior}

NOTE: Some functions return images, video, and audio files. These multimedia files will be represented in messages as
UUIDs for Steamship Blocks. When responding directly to a user, you SHOULD print the Steamship Blocks for the images,
video, or audio as follows: `Block(UUID for the block)`.

Example response for a request that generated an image:
Here is the image you requested: Block(288A2CA1-4753-4298-9716-53C1E42B726B).

Only use the functions you have been provided with.
"""


class GirlfriendGPT(AgentService):
    """Deploy companions and connect them to Telegram."""

    config: GirlFriendGPTConfig
    USED_MIXIN_CLASSES = [
        TelegramTransport,
        SteamshipWidgetTransport,
        IndexerPipelineMixin,
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        model_name = "gpt-4" if self.config.use_gpt4 else "gpt-3.5-turbo"
        self._agent = FunctionsBasedAgent(
            tools=[SearchTool(), SelfieTool(), VideoMessageTool(self.client)],
            llm=ChatOpenAI(self.client, model_name=model_name, temperature=TEMPERATURE),
        )
        self._agent.PROMPT = SYSTEM_PROMPT.format(
            name=self.config.name,
            byline=self.config.byline,
            identity=self.config.identity,
            behavior=self.config.behavior,
        )

        # This Mixin provides HTTP endpoints that connects this agent to a web client
        self.add_mixin(
            SteamshipWidgetTransport(
                client=self.client, agent_service=self, agent=self._agent
            )
        )

        # This Mixin provides HTTP endpoints that connects this agent to Telegram
        self.add_mixin(
            TelegramTransport(
                client=self.client,
                agent_service=self,
                agent=self._agent,
                config=self.config,
            )
        )
        # This Mixin provides HTTP endpoints that connects this agent to Telegram
        self.add_mixin(IndexerPipelineMixin(client=self.client, invocable=self))

    def run_agent(self, agent: Agent, context: AgentContext):
        """Override run-agent to patch in audio generation as a finishing step for text output."""
        speech = self.voice_tool()

        # Note: EmitFunc is Callable[[List[Block], Metadata], None]
        def wrap_emit(emit_func: EmitFunc):
            def wrapper(blocks: List[Block], metadata: Metadata):
                for block in blocks:
                    if block.is_text():
                        text = re.sub(r"^\W+", "", block.text.strip())
                        if text:
                            block.text = text
                            emit_func([block], metadata)
                            if speech:
                                audio_block = speech.run([block], context)[0]
                                audio_block.set_public_data(True)
                                audio_block.url = audio_block.raw_data_url
                                emit_func([audio_block], metadata)
                    else:
                        emit_func([block], metadata)

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
