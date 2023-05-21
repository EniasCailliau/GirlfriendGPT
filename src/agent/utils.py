import logging
import re
import uuid

from steamship.data.workspace import SignedUrl
from steamship.utils.signed_urls import upload_to_signed_url

UUID_PATTERN = re.compile(
    r"([0-9A-Za-z]{8}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{4}-[0-9A-Za-z]{12})"
)


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check a string to see if it is actually a UUID."""
    lowered = uuid_to_test.lower()
    try:
        uuid_obj = uuid.UUID(lowered, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == lowered


def make_block_public(client, block):
    extension = block.mime_type.split("/")[1]
    filepath = f"{uuid.uuid4()}.{extension}"
    signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.WRITE,
            )
        )
        .signed_url
    )
    logging.info(f"Got signed url for uploading block content: {signed_url}")
    read_signed_url = (
        client.get_workspace()
        .create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.READ,
            )
        )
        .signed_url
    )
    upload_to_signed_url(signed_url, block.raw())
    return read_signed_url
