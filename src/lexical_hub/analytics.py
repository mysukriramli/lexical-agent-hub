from pathlib import Path
from typing import Dict, Any, List
import duckdb
from .config import get_settings


class HistoryAnalytics:
    def __init__(self, base_dir: Path | None = None):
        self.settings = get_settings()
        self.base_dir = base_dir or self.settings.history_base_dir

    def get_daily_summary(self, date_str: str) -> Dict[str, Any]:
        """Queries the daily partitioned Parquet files for query volume and latencies."""
        partition_path = self.base_dir / f"dt={date_str}" / "*.parquet"
        
        if not list(self.base_dir.glob(f"dt={date_str}/*.parquet")):
            return {
                "date": date_str,
                "total_searches": 0,
                "found_rate": 0.0,
                "avg_execution_ms": 0.0,
                "most_queried": [],
            }

        con = duckdb.connect(database=":memory:")
        try:
            rel = con.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(CAST(found AS INTEGER)) as hit_rate,
                    AVG(execution_ms) as avg_latency
                FROM read_parquet(?)
            """, [str(partition_path)]).fetchone()

            top_words_rel = con.execute("""
                SELECT searched_word, COUNT(*) as cnt
                FROM read_parquet(?)
                GROUP BY searched_word
                ORDER BY cnt DESC
                LIMIT 5
            """, [str(partition_path)]).fetchall()

            total = rel[0] if rel else 0
            hit_rate = round(rel[1], 4) if rel and rel[1] is not None else 0.0
            avg_lat = round(rel[2], 2) if rel and rel[2] is not None else 0.0

            return {
                "date": date_str,
                "total_searches": total,
                "found_rate": hit_rate,
                "avg_execution_ms": avg_lat,
                "most_queried": [{"word": r[0], "count": r[1]} for r in top_words_rel],
            }
        finally:
            con.close()

    def get_agent_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries recent search history for an agent across all partitions."""
        glob_path = self.base_dir / "dt=*/*.parquet"
        if not list(self.base_dir.glob("dt=*/*.parquet")):
            return []

        con = duckdb.connect(database=":memory:")
        try:
            rows = con.execute("""
                SELECT timestamp_utc, searched_word, found, execution_ms
                FROM read_parquet(?)
                WHERE agent_id = ?
                ORDER BY timestamp_utc DESC
                LIMIT ?
            """, [str(glob_path), agent_id, limit]).fetchall()

            return [
                {
                    "timestamp": str(r[0]),
                    "word": r[1],
                    "found": bool(r[2]),
                    "execution_ms": r[3],
                }
                for r in rows
            ]
        finally:
            con.close()
