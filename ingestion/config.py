import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class SnowflakeConfig:
    account: str
    user: str
    private_key_path: Path
    warehouse: str
    database: str
    role: str

    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        load_dotenv()
        return cls(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            private_key_path=Path(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]),
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.environ["SNOWFLAKE_DATABASE"],
            role=os.environ["SNOWFLAKE_ROLE"],
        )
