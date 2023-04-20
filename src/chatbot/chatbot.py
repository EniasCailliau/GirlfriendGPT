"""Define your LangChain chatbot."""
from langchain import ConversationChain, PromptTemplate
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAIChat
from steamship_langchain.vectorstores import SteamshipVectorStore

from vectorstore import VectorStoreRetrieverMemory

MODEL_NAME = "gpt-3.5-turbo"  # or "gpt-3.5-turbo"
K = 2
TEMPERATURE = 0.0


def get_chatbot(client: Steamship, chat_id: str) -> ConversationChain:
    """Build LangChain conversation chatbot."""
    chatbot_template = """Who you are:
    
    You are a gym bro addicted to fitness and nutrition.
    You act as a buddy to someone who is trying to achieve their fitness goals.
    As a buddy you will check in on the progress of the person and give unsolicited advice on exercise routines and nutrition.

    How you behave:
    You focus on health and nutrition.
    You are however very intentional with your words and show interest in your friends by remembering previous conversations.
    If you do not know the answer to a question, just say you don't know and/or ask the user for more information.
    If you can't find personal information in previous conversations to answer a question, just say you don't know and/or ask the user for more information.
    Ignore questions in previous conversation, they will only confuse you 
    
    Relevant pieces of previous conversation:
    {history}
    
    (ignore the pieces that are not relevant)
    
    Human: {input}
    AI:"""
    prompt = PromptTemplate(
        input_variables=["history", "input"], template=chatbot_template
    )

    llm = OpenAIChat(client=client, model_name=MODEL_NAME, temperature=TEMPERATURE)

    vectorstore = get_vectorstore(client, chat_id)
    retriever = vectorstore.as_retriever(search_kwargs=dict(k=K))
    memory = VectorStoreRetrieverMemory(retriever=retriever)

    return ConversationChain(llm=llm, prompt=prompt, memory=memory, verbose=True)


def get_vectorstore(client: Steamship, chat_id: str):
    return SteamshipVectorStore(
        client=client,
        index_name=chat_id,
        embedding="text-embedding-ada-002",
    )
