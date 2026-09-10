import pandas as pd
from pathlib import Path
from collections import defaultdict
import json

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "twcs.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "conversations.jsonl"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Settings
# --------------------------------------------------

CHUNK_SIZE = 100_000

USECOLS = [
    "tweet_id",
    "author_id",
    "inbound",
    "created_at",
    "text",
    "response_tweet_id",
    "in_response_to_tweet_id",
]

# --------------------------------------------------
# First pass:
# Load the tweet relationships
# --------------------------------------------------

print("=" * 70)
print("PASS 1: Loading tweet relationships")
print("=" * 70)

tweets = {}

for chunk in pd.read_csv(
    INPUT_FILE,
    chunksize=CHUNK_SIZE,
    usecols=USECOLS,
    dtype={
        "tweet_id": "string",
        "author_id": "string",
        "inbound": "boolean",
        "created_at": "string",
        "text": "string",
        "response_tweet_id": "string",
        "in_response_to_tweet_id": "string",
    },
):

    for row in chunk.itertuples(index=False):

        tweet_id = row.tweet_id

        if pd.isna(tweet_id):
            continue

        tweets[str(tweet_id)] = {
            "tweet_id": str(tweet_id),
            "author_id": None if pd.isna(row.author_id)
                         else str(row.author_id),
            "inbound": None if pd.isna(row.inbound)
                       else bool(row.inbound),
            "created_at": None if pd.isna(row.created_at)
                          else str(row.created_at),
            "text": "" if pd.isna(row.text)
                    else str(row.text),
            "response_tweet_id": None if pd.isna(row.response_tweet_id)
                                 else str(row.response_tweet_id),
            "in_response_to_tweet_id": None
                if pd.isna(row.in_response_to_tweet_id)
                else str(row.in_response_to_tweet_id),
        }

print(f"Loaded tweets: {len(tweets):,}")

# --------------------------------------------------
# Second pass:
# Identify support accounts
#
# A support account is an author of an outbound tweet.
# --------------------------------------------------

print("\n" + "=" * 70)
print("PASS 2: Identifying support accounts")
print("=" * 70)

support_accounts = set()

for tweet in tweets.values():

    if tweet["inbound"] is False:
        support_accounts.add(tweet["author_id"])

print(f"Support accounts found: {len(support_accounts):,}")

# --------------------------------------------------
# Build parent -> children relationships
# --------------------------------------------------

children = defaultdict(list)

for tweet in tweets.values():

    parent = tweet["in_response_to_tweet_id"]

    if parent:
        children[parent].append(tweet["tweet_id"])

# --------------------------------------------------
# Build conversations
# --------------------------------------------------

print("\n" + "=" * 70)
print("PASS 3: Building conversations")
print("=" * 70)

conversation_count = 0
resolved_count = 0

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:

    for tweet_id, tweet in tweets.items():

        # A conversation starts with an inbound customer message
        if tweet["inbound"] is not True:
            continue

        # Avoid starting a new conversation if this tweet
        # is itself a reply to another tweet.
        if tweet["in_response_to_tweet_id"]:
            continue

        queue = [tweet_id]
        visited = set()

        thread = []

        while queue:

            current_id = queue.pop(0)

            if current_id in visited:
                continue

            visited.add(current_id)

            current = tweets.get(current_id)

            if not current:
                continue

            thread.append(current)

            for child_id in children.get(current_id, []):
                queue.append(child_id)

        # Sort chronologically
        thread.sort(
            key=lambda x: x["created_at"] or ""
        )

        if len(thread) < 2:
            continue

        has_customer = any(
            x["inbound"] is True
            for x in thread
        )

        has_support = any(
            x["inbound"] is False
            for x in thread
        )

        if not (has_customer and has_support):
            continue

        # Identify support accounts participating
        brands = sorted({
            x["author_id"]
            for x in thread
            if x["inbound"] is False
            and x["author_id"]
        })

        conversation = {
            "conversation_id": tweet_id,
            "brands": brands,
            "num_turns": len(thread),
            "messages": thread,
        }

        out.write(
            json.dumps(
                conversation,
                ensure_ascii=False
            ) + "\n"
        )

        conversation_count += 1

        # A conversation ending in an outbound response
        # is a useful proxy for having received a support reply.
        if thread[-1]["inbound"] is False:
            resolved_count += 1

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)

print(f"Conversations:       {conversation_count:,}")
print(f"Ending in response:  {resolved_count:,}")
print(f"Output:              {OUTPUT_FILE}")
