import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.rag_agent import run_agent

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

TEST_CASES = [
    {
        "test_id": 1,
        "name": "DELIVERY TEST",
        "expected_intent": "delivery_status_delay",
        "customer_message": "My package was supposed to arrive yesterday but hasn't arrived.",
        "context": ""
    },
    {
        "test_id": 2,
        "name": "PRICING TEST",
        "expected_intent": "pricing_or_promotion",
        "customer_message": "Why was I charged more than the advertised price?",
        "context": ""
    },
    {
        "test_id": 3,
        "name": "SUPPORT COMPLAINT TEST",
        "expected_intent": "customer_support_experience",
        "customer_message": "I've contacted customer service several times and nobody has resolved my issue.",
        "context": ""
    }
]

print("\n" + "=" * 80)
print("RUNNING 3-CASE TEST SUITE ON RAG AGENT")
print("=" * 80)

for test in TEST_CASES:
    print(f"\n>>> TEST {test['test_id']}: {test['name']}")
    print(f"Customer Message : {test['customer_message']}")
    print(f"Expected Intent  : {test['expected_intent']}")
    print("-" * 60)

    result = run_agent(
        test["customer_message"],
        test["context"]
    )

    pred = result.get("predicted_intent")
    reply = result.get("reply")
    escalate = result.get("escalate")
    reason = result.get("escalation_reason")
    retrieved = result.get("retrieved_cases", [])

    print(f"Predicted Intent : {pred} {'✅' if pred == test['expected_intent'] else '❌'}")
    print(f"Escalate         : {escalate}")
    print(f"Escalation Reason: {reason}")
    print(f"Generated Reply  :\n{reply}")
    print("\nTop Retrieved Cases:")
    for i, c in enumerate(retrieved[:3], 1):
        print(f"  [{i}] Case: {c.get('case_id')} | Score: {c.get('retrieval_score')} | Intent: {c.get('intent')}")
        print(f"      Customer: {c.get('customer_message')[:80]}...")
        print(f"      Response: {c.get('historical_response')[:80]}...")
    print("=" * 80)
