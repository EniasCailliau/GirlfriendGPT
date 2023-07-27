import streamlit as st

from utils.ux import sidebar, get_instance

sidebar()
st.title("Share your chatbot")
instance = get_instance()

st.subheader("Public URL")

st.code(
    f"https://www.steamship.com/embed/chat?userHandle={instance.user_handle}&workspaceHandle={instance.handle}&instanceHandle={instance.handle}"
)

st.subheader("Embeddable iframe")
st.write(
    "To add the chatbot any where on your website, add this iframe to your html code"
)

st.code(
    """
<iframe src="https://www.steamship.com/embed/chat?userHandle={instance.user_handle}&workspaceHandle={instance.handle}&instanceHandle={instance.handle}"
width="100%"
height="700"
frameborder="0"
></iframe>
"""
)
st.subheader("Chat bubble")

st.write(
    "To add a chat bubble to the bottom right of your website add this script tag to your html"
)
st.code(
    """
<script
src="https://cdn.jsdelivr.net/gh/EniasCailliau/chatbot@main/index.js"
id="https://www.steamship.com/embed/chat?userHandle={instance.user_handle}&workspaceHandle={instance.handle}&instanceHandle={instance.handle}" >
</script>
"""
)

st.subheader("Connect to Telegram")
bot_token = st.text_input("Bot Token", type="password")
st.write(
    "Learn how to create one [here](https://github.com/steamship-packages/langchain-agent-production-starter/blob/main/docs/register-telegram-bot.md)"
)
if st.button("Connect"):
    response = instance.invoke("connect_telegram", bot_token=bot_token)
    if response == "OK":
        st.info("Chatbot successfully connected to Telegram ✅")
