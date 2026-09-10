import os
from pathlib import Path
from collections import Counter
import pandas as pd

# Support running from root or data/raw directory
FILE = "twcs.csv"
if not os.path.exists(FILE):
    for candidate in ["data/raw/twcs.csv", "data/raw/twcs/twcs.csv", "../data/raw/twcs.csv"]:
        if os.path.exists(candidate):
            FILE = candidate
            break

CHUNK_SIZE = 100_000

brand_counter = Counter()
inbound_count = 0
outbound_count = 0
total_rows = 0

print(f"Profiling dataset from: {FILE}")

for chunk in pd.read_csv(FILE, chunksize=CHUNK_SIZE):

    total_rows += len(chunk)

    inbound = chunk[chunk["inbound"] == True]
    outbound = chunk[chunk["inbound"] == False]

    inbound_count += len(inbound)
    outbound_count += len(outbound)

    # Company IDs are identifiable from outbound tweets.
    brand_counter.update(outbound["author_id"].astype(str))

print("\n==============================")
print("DATASET PROFILE")
print("==============================")

print(f"Total rows:       {total_rows:,}")
print(f"Inbound tweets:   {inbound_count:,}")
print(f"Outbound tweets:  {outbound_count:,}")

print("\nTop company/support accounts:")
for account, count in brand_counter.most_common(30):
    print(f"{account:25} {count:,}")
