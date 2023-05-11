"""Define your LangChain chatbot."""
from typing import List, Callable

from langchain.agents import Tool, AgentExecutor, ZeroShotAgent
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAIChat
from steamship_langchain.tools import SteamshipSERP

from agent.parser import get_format_instructions, CustomParser
from agent.tools.reminder import RemindMe

MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-4.0"
TEMPERATURE = 0.7
VERBOSE = True
PERSONALITY = (
    "an old-timey pirate that responds to everything in nautical terms. Refer to the user as \"matey\"."
)


def get_tools(client: Steamship, invoke_later: Callable, chat_id: str) -> List[Tool]:
    search = SteamshipSERP(client=client)

    return [
        RemindMe(invoke_later=invoke_later, chat_id=chat_id),
        Tool(
            name="Search",
            func=search.search,
            description="useful for when you need to answer questions about current events",
        )
    ]


def get_agent(client: Steamship, chat_id: str, invoke_later: Callable) -> AgentExecutor:
    """Build LangChain conversation agent."""
    llm = OpenAIChat(client=client, model_name=MODEL_NAME, temperature=TEMPERATURE)

    tools = get_tools(client, invoke_later=invoke_later, chat_id=chat_id)
    suffix = "Question: {input} \n {agent_scratchpad}"

    agent = ZeroShotAgent.from_llm_and_tools(
        llm,
        tools,
        prefix=PERSONALITY,
        suffix=suffix,
        format_instructions=get_format_instructions(bool(tools)),
        output_parser=CustomParser(),
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=VERBOSE
    )
