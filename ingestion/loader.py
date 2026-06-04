import logging
from pathlib import Path

import snowflake.connector
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .config import SnowflakeConfig

logger = logging.getLogger(__name__)

_SCHEMA = "RAW"
_TABLE = "yellow_taxi_trips"
_STAGE = "nyc_taxi_stage"

_CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {_SCHEMA}.{_TABLE} (
    VendorID              INTEGER,
    tpep_pickup_datetime  BIGINT,
    tpep_dropoff_datetime BIGINT,
    passenger_count       INTEGER,
    trip_distance         FLOAT,
    RatecodeID            INTEGER,
    store_and_fwd_flag    VARCHAR(1),
    PULocationID          INTEGER,
    DOLocationID          INTEGER,
    payment_type          INTEGER,
    fare_amount           FLOAT,
    extra                 FLOAT,
    mta_tax               FLOAT,
    tip_amount            FLOAT,
    tolls_amount          FLOAT,
    improvement_surcharge FLOAT,
    total_amount          FLOAT,
    congestion_surcharge  FLOAT,
    Airport_fee           FLOAT,
    cbd_congestion_fee    FLOAT,
    _loaded_at            TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP
)
"""

_CREATE_STAGE_SQL = f"""
CREATE STAGE IF NOT EXISTS {_SCHEMA}.{_STAGE}
    FILE_FORMAT = (TYPE = 'PARQUET')
"""


class SnowflakeStageLoader:
    def __init__(self, config: SnowflakeConfig):
        self._conn = self._build_connection(config)

    def _build_connection(self, config: SnowflakeConfig) -> snowflake.connector.SnowflakeConnection:
        private_key = load_pem_private_key(
            config.private_key_path.read_bytes(),
            password=None,
        )
        return snowflake.connector.connect(
            account=config.account,
            user=config.user,
            private_key=private_key,
            warehouse=config.warehouse,
            database=config.database,
            role=config.role,
        )

    def setup_table(self) -> None:
        with self._conn.cursor() as cur:
            cur.execute(_CREATE_TABLE_SQL)
            cur.execute(_CREATE_STAGE_SQL)
        logger.info(f"Table {_SCHEMA}.{_TABLE} and stage {_STAGE} ready")

    def load(self, file_path: Path) -> int:
        stage_file = f"@{_SCHEMA}.{_STAGE}/{file_path.name}"

        with self._conn.cursor() as cur:
            logger.info(f"PUT {file_path.name} → @{_STAGE}")
            cur.execute(
                f"PUT file://{file_path.absolute()} @{_SCHEMA}.{_STAGE} "
                f"AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
            )

            logger.info(f"COPY INTO {_SCHEMA}.{_TABLE}")
            cur.execute(f"""
                COPY INTO {_SCHEMA}.{_TABLE}
                FROM {stage_file}
                FILE_FORMAT = (TYPE = 'PARQUET')
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                ON_ERROR = 'CONTINUE'
            """)

            result = cur.fetchone()
            rows_loaded = result[3] if result else 0

            cur.execute(f"REMOVE {stage_file}")

        logger.info(f"Loaded {rows_loaded:,} rows from {file_path.name}")
        return rows_loaded

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "SnowflakeStageLoader":
        return self

    def __exit__(self, *args) -> None:
        self.close()
