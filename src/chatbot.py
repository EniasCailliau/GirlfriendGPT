"""Define your LangChain chatbot."""
from langchain import ConversationChain, PromptTemplate
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAIChat
from steamship_langchain.vectorstores import SteamshipVectorStore

from vectorstore import VectorStoreRetrieverMemory

BOT_TOKEN = "YOUR_TOKEN"
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


if __name__ == '__main__':
    client = Steamship(workspace="banana")
    convo = get_chatbot(client, "test222222addddsddasdfddddasdfadsdd2sdadsfadsasdfad22fsdfasfadsfdasfdsa32")
    print("response", convo.predict(input="what's my favorite food?"), "\n----------------")
    print("response", convo.predict(input="My favorite food is frietjes met stoofvlees"), "\n----------------")
    print("response", convo.predict(input="what's my favorite food?"),
          "\n----------------")
#     print("response", convo.predict(input="What did we say about pizza?"), "\n----------------")
# print(convo.predict(input="What exercises do I dislike?"))
# print(convo.predict(input="My name is Enias, what's your name?"))
# print(convo.predict(input="Whats my favorite food"))
# print(convo.predict(input="I like pushups and deadlifts"))
# print(convo.predict(input="I hate jumping jacks and cycling"))
# print(convo.predict(input="What's my name?"))
# print(convo.predict(input="what's my favorite sport?"))
# print(convo.predict(input="What exercises do I dislike?"))
# print(convo.predict(input="what's my favorite sport?"))
# print(convo.predict(input="What do you keep in mind when building my the training schedule for next week?"))
