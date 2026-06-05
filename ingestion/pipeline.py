import logging
from dataclasses import dataclass
from typing import Iterator

from .protocols import DataLoaderProtocol, FileDownloaderProtocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MonthRange:
    start_year: int
    start_month: int
    end_year: int
    end_month: int

    def __iter__(self) -> Iterator[tuple[int, int]]:
        year, month = self.start_year, self.start_month
        while (year, month) <= (self.end_year, self.end_month):
            yield year, month
            month += 1
            if month > 12:
                month = 1
                year += 1


class IngestionPipeline:
    def __init__(self, downloader: FileDownloaderProtocol, loader: DataLoaderProtocol):
        self._downloader = downloader
        self._loader = loader

    def run(self, period: MonthRange) -> dict[str, int]:
        self._loader.setup_table()
        results: dict[str, int] = {}

        for year, month in period:
            key = f"{year}-{month:02d}"
            logger.info(f"--- Processing {key} ---")
            try:
                file_path = self._downloader.download(year, month)
                rows = self._loader.load(file_path, year=year, month=month)
                results[key] = rows
            except Exception as e:
                logger.error(f"Failed {key}: {e}")
                results[key] = -1

        return results
