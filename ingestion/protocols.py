from pathlib import Path
from typing import Protocol


class FileDownloaderProtocol(Protocol):
    def download(self, year: int, month: int) -> Path: ...


class DataLoaderProtocol(Protocol):
    def setup_table(self) -> None: ...
    def load(self, file_path: Path) -> int: ...
