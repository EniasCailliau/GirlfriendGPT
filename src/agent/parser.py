from __future__ import annotations

from typing import Union, Any

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish

from prompts import FORMAT_INSTRUCTIONS


class MultiModalOutputParser(AgentOutputParser):
    parser: AgentOutputParser

    def __init__(self, parser, **data: Any):
        super().__init__(**data, parser=parser)

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        cleaned_output = text.strip()

        if cleaned_output.startswith("AI: "):
            cleaned_output = cleaned_output[len("AI: ") :]

        return self.parser.parse(cleaned_output)

    @property
    def _type(self) -> str:
        return "conversational_chat"
