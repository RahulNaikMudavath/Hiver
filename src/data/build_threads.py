"""Reconstruct multi-turn customer support conversation threads."""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any


def build_conversation_threads(
    cleaned_csv: Path = Path("./data/processed/cleaned_tweets.csv"),
    output_jsonl: Path = Path("./data/processed/threads.jsonl"),
) -> pd.DataFrame:
    """Group inbound customer inquiries and brand responses into full threads.

    Args:
        cleaned_csv: Path to cleaned tweets CSV.
        output_jsonl: Path to save thread objects.

    Returns:
        DataFrame or list of conversation threads.
    """
    if not cleaned_csv.exists():
        raise FileNotFoundError(f"Cleaned CSV not found at {cleaned_csv}.")

    print(f"Building conversation threads from {cleaned_csv}...")
    df = pd.read_csv(cleaned_csv)

    # Filter for first inbound customer query and subsequent company replies
    # Grouping logic linking response_tweet_id / in_response_to_tweet_id
    threads: List[Dict[str, Any]] = []

    # Example placeholder structure for thread extraction
    # Standardizing columns: thread_id, customer_query, agent_response, author_id, created_at
    print(f"Total records parsed: {len(df)}")
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    # Save placeholder or extracted threads
    df_threads = pd.DataFrame(threads)
    df_threads.to_json(output_jsonl, orient="records", lines=True)
    print(f"Saved threads to {output_jsonl}")
    return df_threads


if __name__ == "__main__":
    build_conversation_threads()
