import logging
import tempfile
from pathlib import Path

from .config import SnowflakeConfig
from .downloader import ParquetDownloader
from .loader import SnowflakeStageLoader
from .pipeline import IngestionPipeline, MonthRange

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    config = SnowflakeConfig.from_env()
    period = MonthRange(start_year=2025, start_month=1, end_year=2025, end_month=6)

    with tempfile.TemporaryDirectory() as tmp_dir:
        downloader = ParquetDownloader(Path(tmp_dir))

        with SnowflakeStageLoader(config) as loader:
            pipeline = IngestionPipeline(downloader, loader)
            results = pipeline.run(period)

    print("\n--- Résultats ingestion ---")
    total = 0
    for month, rows in results.items():
        if rows >= 0:
            print(f"  {month} : {rows:>12,} lignes  ✓")
            total += rows
        else:
            print(f"  {month} : ERREUR")
    print(f"  {'TOTAL':} : {total:>12,} lignes")


if __name__ == "__main__":
    main()
