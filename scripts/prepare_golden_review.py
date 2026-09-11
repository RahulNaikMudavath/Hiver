import json
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

INPUT_FILE = Path(
    "data/golden/golden_candidates_v2.jsonl"
)

OUTPUT_FILE = Path(
    "data/golden/golden_review.md"
)


# ============================================================
# LOAD
# ============================================================

def load_jsonl(path):

    records = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("PREPARING GOLDEN SET HUMAN REVIEW")
    print("=" * 70)

    records = load_jsonl(
        INPUT_FILE
    )

    print(
        f"\nCandidates loaded: {len(records)}"
    )

    # --------------------------------------------------------
    # Create Markdown review document
    # --------------------------------------------------------

    lines = []

    lines.append(
        "# AmazonHelp Golden Set Review\n"
    )

    lines.append(
        "## Instructions\n\n"
        "Review each candidate using the FULL conversation context.\n\n"
        "For every candidate, decide:\n\n"
        "- **KEEP** — example is suitable for the golden set\n"
        "- **CHANGE** — example is suitable, but suggested intent is wrong\n"
        "- **REJECT** — example is too ambiguous, poor quality, duplicate-like, "
        "or otherwise unsuitable\n\n"
        "If keeping the example, record the verified intent.\n\n"
        "Valid intents:\n\n"
    )

    intents = [
        "delivery_status_delay",
        "delivery_not_received",
        "delivery_carrier_issue",
        "order_cancellation",
        "return_issue",
        "refund_issue",
        "product_issue",
        "payment_or_cashback",
        "pricing_or_promotion",
        "account_access_security",
        "prime_or_subscription",
        "product_service_information",
        "customer_support_experience",
        "seller_support_issue",
        "technical_or_system_issue",
        "other_support",
        "non_support_social",
    ]

    for intent in intents:

        lines.append(
            f"- `{intent}`\n"
        )

    lines.append(
        "\n---\n\n"
    )

    # --------------------------------------------------------
    # Candidates
    # --------------------------------------------------------

    for record in records:

        candidate_id = record.get(
            "candidate_id"
        )

        conversation_id = record.get(
            "conversation_id"
        )

        tweet_id = record.get(
            "target_tweet_id"
        )

        target_text = record.get(
            "target_text",
            ""
        )

        suggested = record.get(
            "suggested_intent"
        )

        context = record.get(
            "conversation_context",
            ""
        )

        lines.append(
            f"# Candidate {candidate_id}\n\n"
        )

        lines.append(
            f"**Conversation ID:** `{conversation_id}`  \n"
        )

        lines.append(
            f"**Target Tweet ID:** `{tweet_id}`  \n\n"
        )

        lines.append(
            "## Target Customer Message\n\n"
        )

        lines.append(
            f"> {target_text}\n\n"
        )

        lines.append(
            "## Suggested Intent\n\n"
        )

        lines.append(
            f"`{suggested}`\n\n"
        )

        lines.append(
            "## Full Conversation Context\n\n"
        )

        lines.append(
            "```text\n"
        )

        lines.append(
            context
        )

        lines.append(
            "\n```\n\n"
        )

        lines.append(
            "## Human Verification\n\n"
        )

        lines.append(
            "**Decision:** `KEEP` / `CHANGE` / `REJECT`\n\n"
        )

        lines.append(
            "**Verified Intent:**\n\n"
        )

        lines.append(
            "`__________________________________`\n\n"
        )

        lines.append(
            "**Annotation Notes:**\n\n"
        )

        lines.append(
            "__________________________________________________\n\n"
        )

        lines.append(
            "---\n\n"
        )

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "".join(lines)
        )

    print("\n" + "=" * 70)
    print("REVIEW FILE CREATED")
    print("=" * 70)

    print(
        f"\nCandidates: {len(records)}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )

    print(
        "\nOpen the Markdown file and review the candidates."
    )

    print(
        "\nTarget:"
    )

    print(
        "250 candidates → at least 200 strong verified examples"
    )


if __name__ == "__main__":
    main()