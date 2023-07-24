import re


def clean_text(text: str) -> str:
    return re.sub(r'^\W+', '', text.strip())
