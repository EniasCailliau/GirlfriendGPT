import time

import pandas as pd
import streamlit as st
from pytube import YouTube
from steamship import File

from utils.data import index_youtube_video
from utils.ux import sidebar, get_instance

st.title("Manage your chatbot")

sidebar()


def _get_video_info(youtube_url: str):
    yt = YouTube(youtube_url)
    return {
        "title": yt.title or "Unknown",
        "description": yt.description or "Unknown",
        "view_count": yt.views or 0,
        "thumbnail_url": yt.thumbnail_url or "Unknown",
        "publish_date": yt.publish_date.strftime("%Y-%m-%d %H:%M:%S")
        if yt.publish_date
        else "Unknown",
        "length": yt.length or 0,
        "author": yt.author or "Unknown",
    }


def load_and_show_videos(instance):
    files = File.query(instance.client, tag_filter_query='kind is "_type"').files
    documents = []
    for document in files:
        for block in document.blocks:
            video_info = _get_video_info(document.metadata["source"])
            documents.append(
                {
                    "Title": video_info.get("title"),
                    "source": document.metadata["source"],
                    "thumbnail_url": video_info.get("thumbnail_url"),
                    "Status": document.metadata["status"],
                }
            )
    df = pd.DataFrame(documents)
    table.dataframe(
        df,
        column_config={
            "Title": st.column_config.LinkColumn("source"),
            "thumbnail_url": st.column_config.ImageColumn(label="Thumbnail"),
        },
        column_order=["thumbnail_url", "Title", "Status"],
    )

    return documents


instance = get_instance()
refresh_bar = st.progress(0, text="Time till refresh")

table = st.empty()
documents = []
i = 0

youtube_url = st.text_input("Youtube video url")
if st.button("Add video"):
    index_youtube_video(youtube_url)
    print("done")

while True:
    refresh_bar.progress(i % 20 / 20, text="Time till refresh")

    if i % 20 == 0:
        table.text("Loading videos...")
        load_and_show_videos(instance)
    i += 1
    time.sleep(1)
