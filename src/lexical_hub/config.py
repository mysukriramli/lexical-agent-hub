from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    dictionary_parquet_url: str = (
        "https://huggingface.co/datasets/npvinHnivqn/EnglishDictionary/resolve/"
        "refs%2Fconvert%2Fparquet/default/train/0000.parquet"
    )
    history_base_dir: Path = Path("data/history")
    duckdb_threads: int = 4
    duckdb_memory_limit: str = "2GB"
    enable_external_file_cache: bool = True
    batch_flush_size: int = 100
    flush_interval_seconds: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
