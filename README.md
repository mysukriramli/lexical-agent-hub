# lexical-agent-hub

An agentic gateway providing zero-copy remote dictionary lookups over Hugging Face Parquet datasets, deterministic lexical and information-theoretic calculations, and automated daily-partitioned Parquet telemetry logging.

## Core Features
- **Zero-Copy Remote HTTP Range Requests**: Uses DuckDB's `httpfs` extension with predicate pushdown to read only relevant row groups over the wire.
- **Deterministic Lexical Math**: Shannon entropy ($H(X) = -\sum P(x) \log_2 P(x)$), Levenshtein edit distance, normalized similarity scoring, and Scrabble point totals.
- **Audit Logging in Daily Parquet Partitions**: Stores queries under `data/history/dt=YYYY-MM-DD/batch_{id}.parquet` for non-blocking telemetry and frequency aggregation.
- **Model Context Protocol (MCP)**: Implements FastMCP tool handlers for autonomous agents.

## Quickstart

### Installation
```bash
git clone [https://github.com/your-org/lexical-agent-hub.git](https://github.com/your-org/lexical-agent-hub.git)
cd lexical-agent-hub
pip install -e .
