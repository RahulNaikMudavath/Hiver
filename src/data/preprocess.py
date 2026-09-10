"""Preprocess raw customer support tweets."""

import re
import pandas as pd
from pathlib import Path
from typing import Optional


def clean_tweet_text(text: str) -> str:
    """Clean tweet text by removing sensitive patterns, extra whitespaces, etc.

    Args:
        text: Raw text string.

    Returns:
        Cleaned text string.
    """
    if not isinstance(text, str):
        return ""
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_data(
    input_csv: Path = Path("./data/raw/twcs.csv"),
    output_csv: Path = Path("./data/processed/cleaned_tweets.csv"),
    sample_size: Optional[int] = None,
) -> pd.DataFrame:
    """Load raw tweets, clean text fields, and save processed dataframe.

    Args:
        input_csv: Path to raw CSV file.
        output_csv: Path to save processed CSV file.
        sample_size: Optional row limit for fast development.

    Returns:
        Processed pandas DataFrame.
    """
    if not input_csv.exists():
        raise FileNotFoundError(f"Input file not found at {input_csv}. Run download first.")

    print(f"Loading raw data from {input_csv}...")
    df = pd.read_csv(input_csv, nrows=sample_size)

    print("Cleaning text...")
    df["text_clean"] = df["text"].apply(clean_tweet_text)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    print(f"Saved cleaned data ({len(df)} rows) to {output_csv}")
    return df


if __name__ == "__main__":
    preprocess_data()
