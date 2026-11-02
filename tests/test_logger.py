import uuid
from datetime import datetime, timezone
from pathlib import Path
from lexical_hub.history_logger import HistoryLogger
from lexical_hub.analytics import HistoryAnalytics
from lexical_hub.models import SearchAuditLog, LexicalMetrics


def test_logger_partitioned_write_and_analytics(tmp_path: Path):
    logger = HistoryLogger(base_dir=tmp_path)
    analytics = HistoryAnalytics(base_dir=tmp_path)

    metrics = LexicalMetrics(
        length=4,
        shannon_entropy=1.5,
        scrabble_score=7,
        char_frequencies={"t": 1, "e": 1, "s": 1, "t": 1},
        vowel_count=1,
        consonant_count=3,
    )

    entry = SearchAuditLog(
        log_id=uuid.uuid4().hex,
        timestamp_utc=datetime.now(timezone.utc),
        agent_id="test-agent",
        searched_word="test",
        found=True,
        definitions_count=1,
        metrics_calculated=metrics,
        execution_ms=12.5,
    )

    logger.log_search(entry)
    logger.flush()

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    partition_folder = tmp_path / f"dt={today_str}"
    assert partition_folder.exists()
    assert len(list(partition_folder.glob("*.parquet"))) == 1

    summary = analytics.get_daily_summary(today_str)
    assert summary["total_searches"] == 1
    assert summary["found_rate"] == 1.0
    assert summary["avg_execution_ms"] == 12.5
    assert summary["most_queried"][0]["word"] == "test"

    history = analytics.get_agent_history("test-agent")
    assert len(history) == 1
    assert history[0]["word"] == "test"
