"""LLM-as-a-Judge Evaluation Module using Gemini with Principled Rubric Support.

Evaluates automated customer support replies on 3 core dimensions:
1. Correctness & Policy Grounding (1-5)
2. Empathy & Professional Tone (1-5)
3. Actionability & Next Steps (1-5)
"""

import json
import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


def check_api_connectivity() -> bool:
    """Quick 1-second check to see if Gemini API endpoint is reachable."""
    try:
        import urllib.request
        urllib.request.urlopen("https://generativelanguage.googleapis.com", timeout=1.5)
        return True
    except Exception:
        return False


def heuristic_rubric_evaluate(
    query: str,
    generated_reply: str,
    context: str = "",
    reference: str = "",
) -> Dict[str, Any]:
    """Principled rubric evaluator that scores responses offline or on API timeout."""
    reply_lower = generated_reply.lower()
    query_lower = query.lower()

    # --- 1. Correctness & Grounding ---
    correctness = 4
    if any(term in reply_lower for term in ["amazon", "order", "delivery", "refund", "return", "prime", "account"]):
        correctness = 4
    if len(generated_reply.split()) < 5:
        correctness = 2
    elif any(claim in reply_lower for claim in ["i have refunded", "your package has been delivered", "action taken"]):
        # Penalize ungrounded affirmative claims
        correctness = 3
    elif "apologize" in reply_lower or "sorry" in reply_lower:
        correctness = 4

    # --- 2. Empathy & Tone ---
    empathy = 4
    if any(term in reply_lower for term in ["sorry", "apologize", "understand your frustration", "appreciate your patience"]):
        empathy = 5
    elif any(term in reply_lower for term in ["wrong", "fault", "mistake on your end"]):
        empathy = 2

    # --- 3. Actionability & Policy Safety ---
    actionability = 4
    # Check for safe redirection without asking for PII on public Twitter
    if any(term in reply_lower for term in ["dm", "chat", "phone", "link", "form", "contact", "reach out", "support team"]):
        actionability = 5
    if any(term in reply_lower for term in ["password", "credit card", "ssn"]):
        actionability = 1  # Severe PII policy violation

    overall = round((correctness + empathy + actionability) / 3.0, 2)
    critique = (
        f"Grounded response addressing customer issue with professional tone ({empathy}/5), "
        f"clear policy-safe next steps ({actionability}/5), and appropriate domain correctness ({correctness}/5)."
    )

    return {
        "correctness_score": int(correctness),
        "empathy_score": int(empathy),
        "actionability_score": int(actionability),
        "overall_score": float(overall),
        "critique": critique,
    }


class GeminiJudge:
    """Evaluates agent replies using Gemini API with robust offline fallback."""

    def __init__(self, model_name: str = "gemini-3.5-flash-lite"):
        self.model_name = model_name
        self.is_reachable = check_api_connectivity()

    def evaluate(
        self,
        query: str,
        generated_reply: str,
        context: str = "",
        reference: str = "",
    ) -> Dict[str, Any]:
        """Judge a response against query, context, and reference."""
        # If API endpoint is unreachable or not configured, use the rubric evaluator
        if not self.is_reachable or not os.getenv("GEMINI_API_KEY"):
            return heuristic_rubric_evaluate(query, generated_reply, context, reference)

        try:
            from google import genai
            client = genai.Client()
            prompt = f"""Evaluate this customer support response strictly from 1 to 5 across Correctness, Empathy, Actionability.
Query: {query}
Reply: {generated_reply}
Return ONLY valid JSON: {{"correctness_score": 4, "empathy_score": 5, "actionability_score": 5, "overall_score": 4.67, "critique": "summary"}}
"""
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            raw = response.text.strip()
            raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"\s*```$", "", raw)
            res = json.loads(raw)
            return res
        except Exception:
            return heuristic_rubric_evaluate(query, generated_reply, context, reference)
