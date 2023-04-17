# Tutorial: Telegram chatbot with LangChain 

This project contains the necessary scaffolding to deploy LangChain conversation agents with memory and connect them to Telegram.

These 4 steps should get you online. If not, shoot me a message on [Discord](https://steamship.com/discord). Happy to help you out. 


Let's go: 

> Step 1: Just copy paste your LangChain conversation LLMChain into `src/chatbot/get_chatbot`


> Step 2: Add your telegram bot access token under `BOT_TOKEN` in `src/chatbot.py`. More info [here](docs/register-telegram-bot.md)


> Step 3: Pip install the latest `steamship_langchain`: `pip install --upgrade steamship_langchain`


> Step 4: Run `python deploy.py`


## Variations 

Examples of this package: 
* Gym Bro with long-term memory: https://github.com/steamship-packages/langchain-telegram-chatbot/tree/ec/gym-bro
