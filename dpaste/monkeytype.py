from contextlib import contextmanager
from typing import Iterator

from monkeytype.config import DefaultConfig


class MyConfig(DefaultConfig):
    @contextmanager
    def cli_context(self, command: str) -> Iterator[None]:
        import django  # isort: skip

        django.setup()
        yield


config = MyConfig()
