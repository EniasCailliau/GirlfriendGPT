import os
import uuid

from steamship import Steamship
from steamship.cli.cli import deploy
from steamship.data.manifest import Manifest

try:
    deploy()
except SystemExit as err:
    pass

manifest = Manifest.load_manifest()

client = Steamship(workspace=f"girlfriend-ai-{uuid.uuid1()}")


bot_token = os.environ.get("BOT_TOKEN")
bot = client.use(
    package_handle=manifest.handle,
    version=manifest.version,
    instance_handle=f"{manifest.handle}-{manifest.version.replace('.', '-')}",
    config={"bot_token": bot_token or input("bot_token: ")},
)

bot.wait_for_init()
print(client.config.workspace_handle)
print(bot.package_version_handle)
print(
    f"""Chat with your bot here: 

https://www.steamship.com/workspaces/{client.config.workspace_handle}/packages/{bot.handle}"""
)
