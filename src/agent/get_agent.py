"""Define your LangChain chatbot."""
from typing import List, Callable
from uuid import uuid1

from langchain.agents import Tool, AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAIChat
from steamship_langchain.memory import ChatMessageHistory
from steamship_langchain.tools import SteamshipSERP
from steamship_langchain.vectorstores import SteamshipVectorStore

from agent.parser import ConvoOutputParser
from agent.tools.reminder import RemindMe

MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-3.5-turbo"
K = 2
TEMPERATURE = 0.0
VERBOSE = True


def get_agent(client: Steamship, chat_id: str, invoke_later: Callable) -> AgentExecutor:
    """Build LangChain conversation agent."""
    llm = OpenAIChat(client=client, model_name=MODEL_NAME, temperature=TEMPERATURE)

    chat_memory = ChatMessageHistory(client=client, key=chat_id)
    memory = ConversationBufferMemory(
        chat_memory=chat_memory, memory_key="chat_history", return_messages=True
    )

    tools = get_tools(client, invoke_later, chat_id)
    agent = initialize_agent(
        tools,
        llm,
        output_parser=ConvoOutputParser,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=VERBOSE,
        memory=memory,
    )

    return agent


def get_tools(client: Steamship, invoke_later: Callable, chat_id: str) -> List[Tool]:
    search = SteamshipSERP(client=client)
    search_tool = Tool(
        name="Search",
        func=search.search,
        description="useful for when you need to answer questions about current events",
    )

    return [
        RemindMe(invoke_later=invoke_later, chat_id=chat_id),
        search_tool,
    ]


def get_vectorstore(client: Steamship, chat_id: str):
    return SteamshipVectorStore(
        client=client,
        index_name=chat_id,
        embedding="text-embedding-ada-002",
    )


if __name__ == "__main__":
    client = Steamship(workspace="agent-convo")


    def dummy_invoke_later(delay_ms: int, message: str, chat_id: str):
        print("Just called invoke later", delay_ms, message, chat_id)
        return "This is a test"


    chat_id = str(uuid1())
    agent = get_agent(client, chat_id, dummy_invoke_later)
    output = agent.run(input="Search the web and find me information on Andrew Tate.")
    print(output)
    output = agent.run(input="What did I just ask you?")
    print(output)

