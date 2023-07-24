from steamship import Steamship
from steamship.invocable.mixins.file_importer_mixin import FileImporterMixin, FileType

from api import GirlfriendGPT, GirlFriendGPTConfig

if __name__ == '__main__':
    with Steamship.temporary_workspace() as client:
        test = GirlfriendGPT(client=client, config=GirlFriendGPTConfig(
            bot_token="TEST",
            personality="sacha",
        ).dict())

        file_importer_mixin = [mixin for mixin in test.mixins if isinstance(mixin, FileImporterMixin)][0]

        # Change 1: Make mime_type optional
        f = file_importer_mixin.import_text(text="test")

        print(f)

        f = file_importer_mixin.index_content(content_or_url="test",
                                              file_type=FileType.TEXT,
                                              )
        print(f)

        f = file_importer_mixin.index_content(content_or_url="https://www.youtube.com/watch?v=LXDZ6aBjv_I",
                                              file_type=FileType.YOUTUBE,
                                              )
        print(f)
