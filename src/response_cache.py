"""Simple caching system that checks if we already responded to a message."""
from steamship import Tag, Steamship, File


def already_responded(client: Steamship, chat_id: str, message_id: str) -> bool:
    return (
            len(
                Tag.query(
                    client,
                    tag_filter_query=f'kind "chat_message_id" and name "{chat_id}_{message_id}"',
                ).tags
            )
            > 0
    )


def get_file_for_chat(client: Steamship, chat_id: int) -> File:
    """Find the File associated with this chat id, or create it"""
    file_handle = str(chat_id)
    try:
        return File.get(client, handle=file_handle)
    except:
        return File.create(client, handle=file_handle, blocks=[])


def record_response(client: Steamship, chat_id: int, message_id: str):
    file = get_file_for_chat(client, chat_id)
    Tag.create(
        client, file_id=file.id, kind="chat_message_id", name=f"{chat_id}_{message_id}"
    )
