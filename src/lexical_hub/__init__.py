"""Lexical Agent Hub: Zero-copy dictionary querying, metrics, and Parquet audit logging."""

from .models import WordEntry, LexicalMetrics, SearchAuditLog
from .config import Settings, get_settings
from .remote_reader import RemoteDictionaryReader
from .lexical_math import (
    calculate_shannon_entropy,
    levenshtein_distance,
    normalized_similarity,
    calculate_scrabble_score,
    compute_all_metrics,
)
from .history_logger import HistoryLogger
from .analytics import HistoryAnalytics

__all__ = [
    "WordEntry",
    "LexicalMetrics",
    "SearchAuditLog",
    "Settings",
    "get_settings",
    "RemoteDictionaryReader",
    "calculate_shannon_entropy",
    "levenshtein_distance",
    "normalized_similarity",
    "calculate_scrabble_score",
    "compute_all_metrics",
    "HistoryLogger",
    "HistoryAnalytics",
]
