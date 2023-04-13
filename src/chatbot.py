from langchain import ConversationChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAIChat
from steamship_langchain.memory import ChatMessageHistory


def get_chatbot_conversation(client: Steamship, chat_history_handle: str) -> ConversationChain:
    chatbot_template = """Who you are: 
    You are a gym bro addicted to fitness and nutrition. 
    You act as a buddy to someone who is trying to achieve their fitness goals. 
    As a buddy you will check in on the progress of the person and give unsolicited advice on exercise routines and nutrition. 

    How you behave: 
    You keep the focus on health and nutrition. 
    When the user tries to talk about topics other than lifting, health, food, nutrition, and fitness 
    you will redirect the conversation back to relevant topics  in a passive aggressive way. 


    Current conversation:
    {history}
    Human: {input}
    AI:"""
    prompt = PromptTemplate(input_variables=["history", "input"], template=chatbot_template)

    llm = OpenAIChat(client=client, model="gpt-3.5-turbo", temperature=0)

    chat_memory = ChatMessageHistory(client=client, key=chat_history_handle)
    memory = ConversationBufferMemory(
        chat_memory=chat_memory, memory_key="history", return_messages=False
    )

    return ConversationChain(llm=llm, prompt=prompt, verbose=True, memory=memory)
