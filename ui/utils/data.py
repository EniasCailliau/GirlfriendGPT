import concurrent
import itertools
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import requests
import scrapetube
import streamlit as st
from steamship import PackageInstance


def add_resource(invocation_url: str, api_key: str, url: str):

    response = requests.post(
        f"{invocation_url}index_url",
        json={"url": url},
        headers={"Authorization": f"bearer {api_key}"},
    )
    return response.text


def index_youtube_channel(
    channel_url: str, offset: Optional[int] = 0, count: Optional[int] = 10
):
    instance: PackageInstance = st.session_state.instance

    videos = scrapetube.get_channel(channel_url=channel_url)

    future_to_url = {}
    with ThreadPoolExecutor(max_workers=20) as executor:
        for video in itertools.islice(videos, offset, offset + count + 1):
            video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
            future_to_url[
                executor.submit(
                    add_resource,
                    instance.invocation_url,
                    instance.client.config.api_key,
                    video_url,
                )
            ] = video_url

    for ix, future in enumerate(concurrent.futures.as_completed(future_to_url)):
        url = future_to_url[future]
        try:
            data = future.result()
            if data.lower().contains("added"):
                st.write(f"Added {url}")
        except Exception as e:
            st.error(f"Loading {url} generated an exception: {e}")


def index_youtube_video(youtube_url: str):
    instance: PackageInstance = st.session_state.instance
    data = add_resource(
        instance.invocation_url, instance.client.config.api_key.get_secret_value(), youtube_url
    )

    if "added" in data.lower():
        st.write(f"Added {youtube_url}")
    else:
        print("error", data)


COMPANION_DIR = (
    Path(__file__) / ".." / ".." / ".." / "src" / "personalities"
).resolve()


def get_companions():
    return [
        companion.stem
        for companion in COMPANION_DIR.iterdir()
        if companion.suffix == ".json"
    ]


def get_companion_attributes(companion_name: str):
    companion = json.load((COMPANION_DIR / f"{companion_name}.json").open())
    return {
        "name": companion["name"],
        "byline": companion["byline"],
        "identity": "\n".join(companion["identity"]),
        "behavior": "\n".join(companion["behavior"]),
        "profile_image": companion["profile_image"],
    }
