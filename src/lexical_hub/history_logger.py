import json
import uuid
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import List
import pyarrow as pa
import pyarrow.parquet as pq

from .config import get_settings
from .models import SearchAuditLog


class HistoryLogger:
    _schema = pa.schema([
        ("log_id", pa.string()),
        ("timestamp_utc", pa.timestamp("us", tz="UTC")),
        ("agent_id", pa.string()),
        ("searched_word", pa.string()),
        ("found", pa.bool_()),
        ("definitions_count", pa.int32()),
        ("metrics_json", pa.string()),
        ("execution_ms", pa.float64()),
    ])

    def __init__(self, base_dir: Path | None = None):
        self.settings = get_settings()
        self.base_dir = base_dir or self.settings.history_base_dir
        self.buffer: List[SearchAuditLog] = []
        self._lock = threading.Lock()

    def log_search(self, audit_entry: SearchAuditLog) -> None:
        """Appends audit event to memory buffer and flushes if capacity is reached."""
        with self._lock:
            self.buffer.append(audit_entry)
            if len(self.buffer) >= self.settings.batch_flush_size:
                self._flush_locked()

    def flush(self) -> None:
        """Explicitly flushes remaining buffered records to partitioned Parquet file."""
        with self._lock:
            self._flush_locked()

    def _flush_locked(self) -> None:
        if not self.buffer:
            return

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        partition_dir = self.base_dir / f"dt={date_str}"
        partition_dir.mkdir(parents=True, exist_ok=True)

        batch_id = uuid.uuid4().hex[:8]
        file_path = partition_dir / f"batch_{batch_id}.parquet"

        data = {
            "log_id": [e.log_id for e in self.buffer],
            "timestamp_utc": [e.timestamp_utc for e in self.buffer],
            "agent_id": [e.agent_id for e in self.buffer],
            "searched_word": [e.searched_word for e in self.buffer],
            "found": [e.found for e in self.buffer],
            "definitions_count": [e.definitions_count for e in self.buffer],
            "metrics_json": [
                json.dumps(e.metrics_calculated.model_dump()) if e.metrics_calculated else None
                for e in self.buffer
            ],
            "execution_ms": [e.execution_ms for e in self.buffer],
        }

        table = pa.Table.from_pydict(data, schema=self._schema)
        pq.write_table(table, file_path, compression="SNAPPY")
        self.buffer.clear()
