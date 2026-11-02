import asyncio
from datetime import datetime, timezone
from pathlib import Path
from lexical_hub.server import lookup_word, get_daily_search_history

async def run_simulation():
    # 1. Simulate the agent querying words
    test_words = ["algorithm", "entropy", "parsimony", "ephemeral", "cybernetics"]
    agent_id = "autonomous-researcher-01"

    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting agent search run...")

    for word in test_words:
        print(f"Querying word: '{word}'...")
        res = await lookup_word(word=word, agent_id=agent_id)
        print(f"Result recorded for '{word}'.")

    # 2. Inspect created partitions on disk
    today_partition = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    partition_path = Path("data/history") / f"dt={today_partition}"

    print(f"\nChecking partition folder: {partition_path}")
    if partition_path.exists():
        files = list(partition_path.glob("*.parquet"))
        print(f"Total Parquet batch files written today: {len(files)}")
        for f in files:
            print(f" - File: {f.name} ({f.stat().st_size} bytes)")
    else:
        print("Warning: Partition folder was not created.")

    # 3. Query the analytics tool
    print("\nReading daily search analytics:")
    analytics_json = await get_daily_search_history(today_partition)
    print(analytics_json)

if __name__ == "__main__":
    asyncio.run(run_simulation())
