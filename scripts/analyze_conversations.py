import json
from pathlib import Path
from collections import defaultdict
import statistics

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "conversations.jsonl"
)

stats = defaultdict(lambda: {
    "conversations": 0,
    "resolved": 0,
    "total_turns": 0,
    "multi_turn": 0,
    "customer_messages": 0,
    "support_messages": 0,
    "unique_customers": set(),
})

print("=" * 80)
print("ANALYZING RECONSTRUCTED CONVERSATIONS")
print("=" * 80)

with open(INPUT_FILE, "r", encoding="utf-8") as f:

    for line in f:

        conversation = json.loads(line)

        brands = conversation.get("brands", [])
        messages = conversation.get("messages", [])

        if not brands:
            continue

        # Normally one support account per thread.
        # If multiple exist, count the conversation for each.
        for brand in brands:

            s = stats[brand]

            s["conversations"] += 1

            num_turns = len(messages)
            s["total_turns"] += num_turns

            if num_turns >= 3:
                s["multi_turn"] += 1

            if messages and messages[-1]["inbound"] is False:
                s["resolved"] += 1

            for message in messages:

                if message["inbound"] is True:
                    s["customer_messages"] += 1

                    customer_id = message.get("author_id")

                    if customer_id:
                        s["unique_customers"].add(customer_id)

                else:
                    s["support_messages"] += 1


print("\n" + "=" * 80)
print("BRAND LEADERBOARD")
print("=" * 80)

header = (
    f"{'Brand':25}"
    f"{'Conversations':>15}"
    f"{'Resolved':>12}"
    f"{'Multi-turn %':>14}"
    f"{'Avg turns':>12}"
    f"{'Customers':>12}"
)

print(header)
print("-" * len(header))

results = []

for brand, s in stats.items():

    conversations = s["conversations"]

    resolved_rate = (
        s["resolved"] / conversations
        if conversations
        else 0
    )

    multi_turn_rate = (
        s["multi_turn"] / conversations
        if conversations
        else 0
    )

    avg_turns = (
        s["total_turns"] / conversations
        if conversations
        else 0
    )

    result = {
        "brand": brand,
        "conversations": conversations,
        "resolved": s["resolved"],
        "resolved_rate": resolved_rate,
        "multi_turn_rate": multi_turn_rate,
        "avg_turns": avg_turns,
        "customers": len(s["unique_customers"]),
        "customer_messages": s["customer_messages"],
        "support_messages": s["support_messages"],
    }

    results.append(result)


# Rank primarily by conversation volume,
# while showing the other statistics.
results.sort(
    key=lambda x: x["conversations"],
    reverse=True
)


for r in results:

    print(
        f"{r['brand']:25}"
        f"{r['conversations']:>15,}"
        f"{r['resolved']:>12,}"
        f"{r['multi_turn_rate'] * 100:>13.1f}%"
        f"{r['avg_turns']:>12.2f}"
        f"{r['customers']:>12,}"
    )


print("\n" + "=" * 80)
print("TOP 30")
print("=" * 80)

for i, r in enumerate(results[:30], start=1):

    print(
        f"{i:2}. "
        f"{r['brand']:25} "
        f"{r['conversations']:>10,} conversations | "
        f"{r['resolved_rate'] * 100:5.1f}% response-ending | "
        f"{r['multi_turn_rate'] * 100:5.1f}% multi-turn | "
        f"{r['avg_turns']:.2f} avg turns"
    )