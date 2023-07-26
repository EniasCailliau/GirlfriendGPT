import time

import pandas as pd
import streamlit as st
from steamship import File

from utils.ux import sidebar, get_instance

st.title("Manage your chatbot")

sidebar()


def load_and_show_videos(instance):
    files = File.query(instance.client, tag_filter_query='kind is "_type"').files
    videos = []
    for file in files:
        for block in file.blocks:
            tag_key_to_value = {tag.kind: tag.name for tag in block.tags}
            videos.append(
                {
                    "Title": tag_key_to_value.get("title"),
                    "source": "https://www.youtube.com/watch?v="
                    + tag_key_to_value.get("source"),
                    "thumbnail_url": tag_key_to_value.get("thumbnail_url"),
                    "Status": [tag.name for tag in file.tags if tag.kind == "status"][
                        0
                    ],
                }
            )
    df = pd.DataFrame(videos)
    table.dataframe(
        df,
        column_config={
            "Title": st.column_config.LinkColumn("source"),
            "thumbnail_url": st.column_config.ImageColumn(label="Thumbnail"),
        },
        column_order=["thumbnail_url", "Title", "Status"],
    )

    return videos


instance = get_instance()
refresh_bar = st.progress(0, text="Time till refresh")

table = st.empty()
videos = []
i = 0
#
# if st.button("Add 10 more video's", type="primary"):
#     videos = load_and_show_videos(instance)
#     index_youtube_channel(st.session_state.channel_url, len(videos), 10)
#     i = 0

while True:
    refresh_bar.progress(i % 20 / 20, text="Time till refresh")

    if i % 20 == 0:
        table.text("Loading videos...")
        load_and_show_videos(instance)
    i += 1
    time.sleep(1)
