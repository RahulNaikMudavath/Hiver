"""Discover intents through topic modeling / clustering or LLM summarization."""

import json
from pathlib import Path
from typing import Dict, List, Any


DEFAULT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "ORDER_STATUS_TRACKING": {
        "description": "Inquiries regarding delivery tracking, shipping updates, or ETA.",
        "keywords": ["where is my order", "track", "shipping", "delivery status", "package"],
    },
    "CANCELLATION_REFUND": {
        "description": "Requests to cancel an order or request a refund/chargeback.",
        "keywords": ["cancel", "refund", "money back", "return", "charge"],
    },
    "TECHNICAL_SUPPORT": {
        "description": "Troubleshooting app crashes, website glitches, login failures, or device errors.",
        "keywords": ["login", "error", "crash", "bug", "not working", "password reset"],
    },
    "BILLING_PAYMENT_ISSUE": {
        "description": "Discrepancies in invoices, payment method rejections, duplicate billing.",
        "keywords": ["charged twice", "overcharged", "payment failed", "credit card", "billing"],
    },
    "PRODUCT_INQUIRY_FEEDBACK": {
        "description": "General product features, availability, pricing, or customer suggestions.",
        "keywords": ["do you have", "feature request", "compatibility", "available in", "price"],
    },
    "COMPLAINT_ESCALATION": {
        "description": "Severe dissatisfaction, agent conduct complaints, demanding supervisor or manager.",
        "keywords": ["terrible service", "talk to human", "manager", "unacceptable", "supervisor"],
    },
}


def save_taxonomy(
    taxonomy: Dict[str, Dict[str, Any]] = DEFAULT_TAXONOMY,
    output_path: Path = Path("./data/processed/intent_taxonomy.json"),
) -> None:
    """Save intent taxonomy definitions to disk.

    Args:
        taxonomy: Dictionary of intent metadata.
        output_path: Destination JSON path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2)
    print(f"Taxonomy written to {output_path}")


def load_taxonomy(
    taxonomy_path: Path = Path("./data/processed/intent_taxonomy.json"),
) -> Dict[str, Dict[str, Any]]:
    """Load intent taxonomy from disk, falling back to DEFAULT_TAXONOMY.

    Args:
        taxonomy_path: Path to taxonomy JSON.

    Returns:
        Taxonomy dictionary.
    """
    if taxonomy_path.exists():
        with open(taxonomy_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_TAXONOMY


if __name__ == "__main__":
    save_taxonomy()
