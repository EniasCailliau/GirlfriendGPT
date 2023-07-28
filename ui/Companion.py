import sys
from pathlib import Path

import streamlit as st
from steamship.cli.create_instance import load_manifest

sys.path.append(str((Path(__file__) / "..").resolve()))
st.set_page_config(page_title="🎥->🤗 Youtube to Companion")
from utils.data import get_companions, get_companion_attributes, add_resource
from utils.utils import get_instance, to_snake
from utils.ux import sidebar, get_api_key, show_response

# Start page
st.title("🎥->🤗 Youtube to Companion")
st.write("Create your AI companion and chat about your favorite youtube video's")

sidebar()

manifest = load_manifest()

if not st.session_state.get("instance"):

    # TODO: Add dropdown with examples
    col1, col2 = st.columns(2)

    col1.subheader("Attributes")
    companion_template = col2.selectbox(
        "Templates (Optional)", options=["<none>", *get_companions()]
    )
    if companion_template != "<none>":
        companion = get_companion_attributes(companion_template.lower())
    else:
        companion = {}

    personality = st.text_input(
        "Name",
        value=companion.get("name", ""),
        placeholder="The name of your companion",
    )
    byline = st.text_input(
        "Byline",
        value=companion.get("byline", ""),
        placeholder="The byline of your companion",
    )
    identity = st.text_input(
        "Identity",
        value=companion.get("identity", ""),
        placeholder="The identity of your companion",
    )
    behavior = st.text_input(
        "Behavior",
        value=companion.get("behavior", ""),
        placeholder="The behavior of your companion",
    )
    st.session_state.companion_profile_img = st.text_input(
        "Profile picture",
        value=companion.get("profile_image", ""),
        placeholder="The profile picture of your companion",
    )

    st.session_state.companion_first_message = st.text_input(
        label="First message",
        placeholder="The first message your companion sends when a new conversation starts.",
    )

    st.subheader("Long term memory")
    youtube_video_url = st.text_input("Youtube Video URL")

    if st.button("🤗 Spin up your companion"):

        st.session_state.instance = instance = get_instance(
            to_snake(personality),
            config={
                "name": personality,
                "byline": byline,
                "identity": identity,
                "behavior": behavior,
            },
        )

        if youtube_video_url:
            with st.spinner("Companion is watching the video 👀..."):
                add_resource(
                    instance.invocation_url,
                    str(instance.client.config.api_key),
                    youtube_video_url,
                )

        st.balloons()
        st.experimental_rerun()

else:
    instance = st.session_state.instance
    companion_name = instance.config["name"]

    if st.button("+ New bot"):
        st.session_state.instance = None
        st.experimental_rerun()

    st.header(f"Start chatting with {companion_name}")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": st.session_state.companion_first_message or "Hi ☺️"}
        ]

    companion_img = st.session_state.get("companion_profile_img")
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message(msg["role"], avatar=companion_img):
                for response in [msg["content"]] if isinstance(msg["content"], str) else msg["content"]:
                    show_response(response)
        else:
            st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input():
        get_api_key()
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                responses = instance.invoke("prompt", prompt=prompt)
            for response in responses:
                show_response(response)
        st.session_state.messages.append({"role": "assistant", "content": responses})
