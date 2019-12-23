import os
from contextlib import contextmanager
from typing import Iterator

from monkeytype.config import DefaultConfig


class DpasteConfig(DefaultConfig):
    @contextmanager
    def cli_context(self, command: str) -> Iterator[None]:
        """
        Django Settings setup
        """
        try:
            import dpaste.settings.local  # isort: skip

            settings = "dpaste.settings.local"
        except ImportError:
            settings = "dpaste.settings.base"

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

        import django  # isort: skip

        django.setup()
        yield


CONFIG = DpasteConfig()
