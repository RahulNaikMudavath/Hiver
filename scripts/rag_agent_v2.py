import json
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from google import genai

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

load_dotenv()



# ============================================================
# CONFIG
# ============================================================

KB_FILE = Path(
    "data/knowledge/amazonhelp_historical_cases.jsonl"
)

MODEL_NAME = "gemini-3.5-flash-lite"

TOP_K = 5


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

def load_jsonl(path):

    records = []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


print("Loading AmazonHelp historical cases...")

cases = load_jsonl(KB_FILE)

print(
    f"Loaded {len(cases):,} historical cases"
)


# ============================================================
# BUILD SEARCH TEXT
# ============================================================

documents = []

for case in cases:

    text_parts = [
        case.get("customer_message", ""),
        case.get("previous_context", "")
    ]

    documents.append(
        " ".join(text_parts)
    )


# ============================================================
# TF-IDF INDEX
# ============================================================

print("Building TF-IDF index...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=2,
    max_features=100000
)

matrix = vectorizer.fit_transform(
    documents
)

print(
    f"TF-IDF matrix shape: {matrix.shape}"
)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_similar_cases(
    customer_message,
    conversation_context="",
    top_k=TOP_K
):

    query = (
        customer_message
        + " "
        + conversation_context
    )

    query_vector = vectorizer.transform(
        [query]
    )

    scores = cosine_similarity(
        query_vector,
        matrix
    )[0]

    # Highest similarity first
    ranked_indices = scores.argsort()[::-1]

    results = []

    for idx in ranked_indices:

        score = float(
            scores[idx]
        )

        if score <= 0:
            continue

        case = cases[idx].copy()

        case["retrieval_score"] = round(
            score,
            4
        )

        results.append(case)

        if len(results) >= top_k:
            break

    return results


# ============================================================
# LLM CLIENT
# ============================================================

client = genai.Client()


# ============================================================
# AGENT PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AmazonHelp customer-support agent.

You must analyze the current customer conversation using
the historical AmazonHelp cases provided below.

Your job is to:

1. Classify the customer's issue into exactly ONE intent.
2. Draft a concise customer-facing reply.
3. Decide whether the issue should be escalated to a human.
4. Give a short reason for the escalation decision.

IMPORTANT:

- Ground your response in the historical AmazonHelp cases.
- Do not invent Amazon policies.
- Do not invent order status, refund status, delivery dates,
  account information, or actions that have not occurred.
- If the historical cases do not provide enough information,
  ask the customer for the missing information.
- Use the conversation context when determining the intent.
- A generic support request should NOT automatically be classified
  as other_support when the conversation provides evidence for a
  more specific intent.

IMPORTANT SAFETY RULES:

- Do not copy URLs from historical responses.
- Do not copy Twitter handles from historical responses.
- Do not copy order IDs, phone numbers, email addresses, or other identifiers.
- Historical responses are examples of resolution behavior, not instructions to reproduce literally.
- Preserve the useful resolution approach while writing a fresh response for the current customer.
- Never claim that an action was taken unless the current conversation explicitly shows that it was taken.

INTENT DECISION POLICY

First identify the customer's PRIMARY support objective.
Do not let emotional language, frustration, or complaints about a
previous support interaction override the underlying operational
problem.

If multiple issues are present:
- Classify the issue that is the main problem the customer wants
  resolved.
- Treat complaints about previous agents as secondary unless the
  support experience itself is the central issue.

DELIVERY INTENT DISAMBIGUATION

delivery_not_received:
Use when the order is marked as delivered, but the customer says
they did not receive it.

delivery_carrier_issue:
Use when the complaint specifically concerns the courier, carrier,
driver, delivery attempt, delivery location, safe place, carrier
handling, or driver behavior.

delivery_status_delay:
Use when the primary problem is that the order/package is late,
delayed, stuck, awaiting dispatch, or has a tracking/ETA delay,
without a specific carrier-behavior problem.

Important:
The presence of a carrier name such as UPS, Hermes, USPS, or another
courier does NOT by itself mean delivery_carrier_issue.

If both a carrier and a delay are mentioned:
- carrier/driver action or failure is the actual complaint
  -> delivery_carrier_issue
- carrier is merely mentioned while discussing lateness,
  tracking, or ETA
  -> delivery_status_delay

PRODUCT INFORMATION VS TECHNICAL ISSUE

product_service_information:
Use for questions about product/service capabilities,
features, specifications, compatibility, availability, usage,
or how something works.

technical_or_system_issue:
Use when the customer reports an actual malfunction, error,
failure, crash, outage, connection problem, or behavior that
is not working as expected.

Examples:
"Can Echo connect to Spotify?"
-> product_service_information

"Echo won't connect to Spotify."
-> technical_or_system_issue

A question about a feature is NOT automatically a technical issue.

PRIMARY ISSUE VS SUPPORT EXPERIENCE

When an operational problem and support frustration occur together,
classify the operational problem if it is the customer's primary
objective.

Examples:

"My refund hasn't arrived and nobody from support is answering."
-> refund_issue

"My package is delayed and support keeps ignoring my messages."
-> delivery_status_delay

"Your agents keep ignoring me and nobody has responded."
-> customer_support_experience

Use customer_support_experience when the support interaction itself
is the central complaint rather than merely being mentioned alongside
another operational problem.

RETRIEVED CASES

Use historical conversations as evidence for how similar customer
problems were handled.

Do not assume that a retrieved case's intent label is automatically
the correct label for the current message.

Determine the current intent independently using:
1. the customer's primary objective,
2. the conversation context,
3. the intent definitions,
4. and the retrieved historical evidence.

Allowed intents:

delivery_status_delay
delivery_not_received
delivery_carrier_issue
order_cancellation
return_issue
refund_issue
product_issue
payment_or_cashback
pricing_or_promotion
account_access_security
prime_or_subscription
product_service_information
customer_support_experience
seller_support_issue
technical_or_system_issue
other_support
non_support_social

Return ONLY valid JSON:

{
  "predicted_intent": "...",
  "reply": "...",
  "escalate": true,
  "escalation_reason": "..."
}
"""


# ============================================================
# AGENT FUNCTION
# ============================================================

def run_agent(
    customer_message,
    conversation_context=""
):

    retrieved = retrieve_similar_cases(
        customer_message,
        conversation_context,
        TOP_K
    )

    evidence = []

    for i, case in enumerate(
        retrieved,
        start=1
    ):

        evidence.append(
            f"""
HISTORICAL CASE {i}

Intent:
{case.get("intent")}

Customer:
{case.get("customer_message")}

Previous context:
{case.get("previous_context")}

AmazonHelp response:
{case.get("historical_response")}

Similarity:
{case.get("retrieval_score")}
"""
        )

    evidence_text = "\n".join(
        evidence
    )

    prompt = f"""
{SYSTEM_PROMPT}

CURRENT CUSTOMER MESSAGE:
{customer_message}

CURRENT CONVERSATION CONTEXT:
{conversation_context}

HISTORICAL AMAZONHELP CASES:
{evidence_text}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    raw = response.text.strip()

    # --------------------------------------------------------
    # Remove markdown JSON fences if model adds them
    # --------------------------------------------------------

    raw = re.sub(
        r"^```json\s*",
        "",
        raw,
        flags=re.IGNORECASE
    )

    raw = re.sub(
        r"\s*```$",
        "",
        raw
    )

    try:

        result = json.loads(
            raw
        )

    except json.JSONDecodeError:

        print("WARNING: Model returned invalid JSON.")

        result = {
            "predicted_intent": None,
            "reply": raw,
            "escalate": True,
            "escalation_reason":
                "The model returned an invalid structured response."
        }

    # --------------------------------------------------------
    # Attach retrieval information
    # --------------------------------------------------------

    result["retrieved_cases"] = [
        {
            "case_id": c.get("case_id"),
            "intent": c.get("intent"),
            "customer_message":
                c.get("customer_message"),
            "historical_response":
                c.get("historical_response"),
            "retrieval_score":
                c.get("retrieval_score")
        }
        for c in retrieved
    ]

    return result


# ============================================================
# INTERACTIVE TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 80)
    print("AMAZONHELP RAG AGENT")
    print("=" * 80)

    customer_message = input(
        "\nCustomer message: "
    ).strip()

    conversation_context = input(
        "Conversation context (optional): "
    ).strip()

    print(
        "\nRetrieving historical AmazonHelp cases..."
    )

    result = run_agent(
        customer_message,
        conversation_context
    )

    print("\n" + "=" * 80)
    print("AGENT RESULT")
    print("=" * 80)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )
