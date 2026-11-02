import duckdb
import time
from typing import List, Tuple
from .config import get_settings
from .models import WordEntry


class RemoteDictionaryReader:
    def __init__(self, custom_url: str | None = None):
        self.settings = get_settings()
        self.parquet_url = custom_url or self.settings.dictionary_parquet_url
        self.con = duckdb.connect(database=":memory:")
        self._init_duckdb()

    def _init_duckdb(self) -> None:
        self.con.execute("INSTALL httpfs;")
        self.con.execute("LOAD httpfs;")
        self.con.execute(f"SET threads = {self.settings.duckdb_threads};")
        self.con.execute(f"SET memory_limit = '{self.settings.duckdb_memory_limit}';")
        if self.settings.enable_external_file_cache:
            self.con.execute("SET enable_external_file_cache = true;")

    def lookup(self, word: str) -> Tuple[List[WordEntry], float]:
        """
        Executes an HTTP byte-range request against the remote Parquet file,
        fetching only required row groups using predicate pushdown.
        """
        target = word.strip().lower()
        start_time = time.perf_counter()

        query = f"""
            SELECT word, definition, pos
            FROM read_parquet(?)
            WHERE lower(word) = ?
        """
        
        try:
            rel = self.con.execute(query, [self.parquet_url, target])
            rows = rel.fetchall()
            entries = [
                WordEntry(
                    word=str(r[0]),
                    definition=str(r[1]),
                    pos=str(r[2]) if r[2] is not None else None,
                )
                for r in rows
            ]
        except Exception:
            entries = []

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return entries, elapsed_ms

    def close(self) -> None:
        self.con.close()
