import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


class ParquetDownloader:
    def __init__(self, download_dir: Path):
        self._dir = download_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def download(self, year: int, month: int) -> Path:
        filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
        dest = self._dir / filename

        if dest.exists():
            logger.info(f"{filename} already cached, skipping download")
            return dest

        url = f"{_BASE_URL}/{filename}"
        logger.info(f"Downloading {url}")

        with requests.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

        logger.info(f"Saved {filename} ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
