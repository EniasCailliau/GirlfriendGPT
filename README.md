# Tutorial: Telegram chatbot with LangChain 

This project contains the necessary scaffolding to deploy LangChain conversation agents with memory and connect them to Telegram.


# Step 1: Add your chatbot agent 

- Step 1: Just copy paste your LangChain conversation LLMChain into `src/chatbot/get_chatbot`


- Step 2: Add your telegram bot access token under `BOT_TOKEN` in `src/api.py`. More info [here](docs/register-telegram-bot.md)


- Step 3: Pip install the latest `steamship_langchain`: `pip install --upgrade steamship_langchain`


- Step 4: Run `python get_instance.py`