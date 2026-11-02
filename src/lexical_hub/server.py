import uuid
import json
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

from .remote_reader import RemoteDictionaryReader
from .lexical_math import (
    compute_all_metrics,
    levenshtein_distance,
    normalized_similarity,
    calculate_shannon_entropy,
    calculate_scrabble_score,
)
from .history_logger import HistoryLogger
from .analytics import HistoryAnalytics
from .models import SearchAuditLog, DistanceResult

mcp = FastMCP("lexical-agent-hub")

_reader = RemoteDictionaryReader()
_logger = HistoryLogger()
_analytics = HistoryAnalytics()


@mcp.tool()
async def lookup_word(word: str, agent_id: str = "agent-1") -> str:
    """
    Looks up a word in the remote Parquet dictionary via zero-copy range request.
    Computes Shannon entropy and Scrabble scores, and commits an audit log.
    """
    clean_word = word.strip().lower()
    entries, elapsed_ms = _reader.lookup(clean_word)
    metrics = compute_all_metrics(clean_word)

    audit_entry = SearchAuditLog(
        log_id=uuid.uuid4().hex,
        timestamp_utc=datetime.now(timezone.utc),
        agent_id=agent_id,
        searched_word=clean_word,
        found=len(entries) > 0,
        definitions_count=len(entries),
        metrics_calculated=metrics,
        execution_ms=elapsed_ms,
    )
    _logger.log_search(audit_entry)
    _logger.flush()

    response = {
        "word": clean_word,
        "found": len(entries) > 0,
        "definitions": [e.model_dump() for e in entries],
        "metrics": metrics.model_dump(),
        "query_latency_ms": elapsed_ms,
    }
    return json.dumps(response, indent=2)


@mcp.tool()
async def compute_lexical_distance(word_a: str, word_b: str) -> str:
    """Computes Levenshtein distance, similarity ratio, entropy delta, and Scrabble point delta."""
    w_a = word_a.strip().lower()
    w_b = word_b.strip().lower()

    dist = levenshtein_distance(w_a, w_b)
    sim = normalized_similarity(w_a, w_b)
    ent_a = calculate_shannon_entropy(w_a)
    ent_b = calculate_shannon_entropy(w_b)
    scr_a = calculate_scrabble_score(w_a)
    scr_b = calculate_scrabble_score(w_b)

    result = DistanceResult(
        word_a=w_a,
        word_b=w_b,
        levenshtein_distance=dist,
        similarity_ratio=sim,
        entropy_delta=round(abs(ent_a - ent_b), 4),
        scrabble_delta=abs(scr_a - scr_b),
    )
    return json.dumps(result.model_dump(), indent=2)


@mcp.tool()
async def get_daily_search_history(date_str: str) -> str:
    """
    Inspects what words autonomous agents looked up on a specific date (YYYY-MM-DD).
    Returns query volume, hit rate, average latency, and top queried words.
    """
    summary = _analytics.get_daily_summary(date_str)
    return json.dumps(summary, indent=2)


@mcp.tool()
async def get_agent_recent_queries(agent_id: str, limit: int = 20) -> str:
    """Retrieves recent search queries logged for a specific agent ID."""
    history = _analytics.get_agent_history(agent_id, limit=limit)
    return json.dumps(history, indent=2)


if __name__ == "__main__":
    mcp.run()
