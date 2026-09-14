import json
from collections import Counter
from pathlib import Path


INPUT = Path("data/golden/rag_predictions.jsonl")
OUTPUT = Path("data/golden/rag_failures_clean.txt")


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def main():

    records = load_jsonl(INPUT)

    valid = []
    failures = []
    correct = []

    for r in records:

        gold = r.get("gold_intent")
        pred = r.get("predicted_intent")

        if not gold or not pred:
            continue

        valid.append(r)

        if gold == pred:
            correct.append(r)
        else:
            failures.append(r)

    print("=" * 80)
    print("CLEAN RAG FAILURE ANALYSIS")
    print("=" * 80)

    print(f"Total valid records : {len(valid)}")
    print(f"Correct             : {len(correct)}")
    print(f"Failures            : {len(failures)}")

    accuracy = (
        len(correct) / len(valid)
        if valid else 0
    )

    print(f"Accuracy            : {accuracy:.2%}")

    # ---------------------------------------------------------------
    # CONFUSION PAIRS
    # ---------------------------------------------------------------

    pairs = Counter(
        (
            r["gold_intent"],
            r["predicted_intent"]
        )
        for r in failures
    )

    print("\n" + "=" * 80)
    print("CONFUSION PAIRS")
    print("=" * 80)

    for (gold, pred), count in pairs.most_common():

        print(
            f"{count:>3}  "
            f"{gold} -> {pred}"
        )

    # ---------------------------------------------------------------
    # FAILURE RATE BY INTENT
    # ---------------------------------------------------------------

    gold_counts = Counter(
        r["gold_intent"]
        for r in valid
    )

    failure_counts = Counter(
        r["gold_intent"]
        for r in failures
    )

    print("\n" + "=" * 80)
    print("FAILURE RATE BY GOLD INTENT")
    print("=" * 80)

    for intent, total in gold_counts.most_common():

        failed = failure_counts[intent]

        print(
            f"{intent:<35} "
            f"{failed:>3}/{total:<3} "
            f"({failed / total:.2%})"
        )

    # ---------------------------------------------------------------
    # WRITE ONLY ACTUAL FAILURES
    # ---------------------------------------------------------------

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("RAG FAILURE EXAMPLES\n")
        f.write("=" * 80 + "\n\n")

        for i, r in enumerate(failures, 1):

            gold = r["gold_intent"]
            pred = r["predicted_intent"]

            f.write(
                f"FAILURE {i}\n"
            )

            f.write(
                f"Gold      : {gold}\n"
            )

            f.write(
                f"Predicted : {pred}\n"
            )

            f.write(
                f"Candidate : {r.get('candidate_id')}\n"
            )

            f.write(
                "\nTARGET MESSAGE:\n"
            )

            f.write(
                r.get("target_text", "")
            )

            f.write(
                "\n\nCONVERSATION CONTEXT:\n"
            )

            f.write(
                r.get("conversation_context", "")
            )

            f.write(
                "\n\nRETRIEVED CASES:\n"
            )

            for j, case in enumerate(
                r.get("retrieved_cases", [])[:5],
                1
            ):

                f.write(
                    f"\n[{j}] score="
                    f"{case.get('retrieval_score', case.get('score'))}\n"
                )

                f.write(
                    "Customer: "
                    + case.get(
                        "customer_message",
                        ""
                    )
                    + "\n"
                )

                f.write(
                    "Historical response: "
                    + case.get(
                        "historical_response",
                        ""
                    )
                    + "\n"
                )

            f.write(
                "\n"
                + "-" * 80
                + "\n\n"
            )

    print("\nSaved:")
    print(OUTPUT)


if __name__ == "__main__":
    main()