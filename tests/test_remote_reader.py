from pathlib import Path
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from lexical_hub.remote_reader import RemoteDictionaryReader


def test_reader_local_parquet_mock(tmp_path: Path):
    mock_file = tmp_path / "mock_dict.parquet"
    table = pa.Table.from_pydict({
        "word": ["parsimony", "ephemeral"],
        "definition": ["Extreme unwillingness to spend money", "Lasting for a very short time"],
        "pos": ["noun", "adjective"],
    })
    pq.write_table(table, mock_file)

    reader = RemoteDictionaryReader(custom_url=str(mock_file))
    entries, elapsed = reader.lookup("parsimony")

    assert len(entries) == 1
    assert entries[0].word == "parsimony"
    assert "unwillingness" in entries[0].definition
    assert entries[0].pos == "noun"
    assert elapsed >= 0.0

    not_found, _ = reader.lookup("nonexistentword123")
    assert len(not_found) == 0
    reader.close()
