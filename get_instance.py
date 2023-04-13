from steamship import Steamship
from steamship.cli.cli import deploy

try:
    deploy()
except SystemExit as err:
    pass

client = Steamship(workspace="gymbro-new")

bot = client.use(
    "gym-bro-ai",
)

bot.wait_for_init()

print(bot.package_version_handle)
