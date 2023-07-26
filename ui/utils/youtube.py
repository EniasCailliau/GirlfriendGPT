import re
import urllib.request


def download_html(url):
    with urllib.request.urlopen(url) as response:
        html = response.read().decode()
    return html


def extract_channel_id_and_name(html_content):
    id_pattern = r'<link rel="canonical" href="https://www.youtube.com/channel/(.*?)"'
    title_pattern = r"<title>(.*?) - YouTube</title>"

    id_match = re.findall(id_pattern, html_content)
    title_match = re.findall(title_pattern, html_content)

    channel_id = id_match[0] if id_match else None
    channel_name = title_match[0] if title_match else None
    return channel_id, channel_name


def get_channel_name(channel_url):
    try:
        html_content = download_html(channel_url)
        channel_id, channel_name = extract_channel_id_and_name(html_content)
        return channel_name
    except Exception as e:
        print(f"Error loading youtube data {e}")
