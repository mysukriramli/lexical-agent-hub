from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class WordEntry(BaseModel):
    word: str
    definition: str
    pos: Optional[str] = None


class LexicalMetrics(BaseModel):
    length: int
    shannon_entropy: float = Field(..., description="Bits per character")
    scrabble_score: int
    char_frequencies: Dict[str, int]
    vowel_count: int
    consonant_count: int


class SearchAuditLog(BaseModel):
    log_id: str
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_id: str
    searched_word: str
    found: bool
    definitions_count: int
    metrics_calculated: Optional[LexicalMetrics] = None
    execution_ms: float


class DistanceResult(BaseModel):
    word_a: str
    word_b: str
    levenshtein_distance: int
    similarity_ratio: float
    entropy_delta: float
    scrabble_delta: int
