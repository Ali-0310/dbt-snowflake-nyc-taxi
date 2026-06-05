import argparse
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


def _parse_args() -> MonthRange:
    parser = argparse.ArgumentParser(description="Ingestion NYC Taxi Parquet → Snowflake RAW")
    parser.add_argument("--start-year",  type=int, required=True, help="Année de début (ex: 2024)")
    parser.add_argument("--start-month", type=int, required=True, help="Mois de début (ex: 1)")
    parser.add_argument("--end-year",    type=int, required=True, help="Année de fin (ex: 2025)")
    parser.add_argument("--end-month",   type=int, required=True, help="Mois de fin (ex: 6)")
    args = parser.parse_args()
    return MonthRange(args.start_year, args.start_month, args.end_year, args.end_month)


def main() -> None:
    period = _parse_args()
    config = SnowflakeConfig.from_env()

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
