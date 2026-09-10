"""Few-shot or zero-shot LLM-based intent classifier with structured JSON output."""

import os
import json
from typing import Dict, Any, Optional, List
from src.taxonomy.discover_intents import load_taxonomy


INTENT_PROMPT_TEMPLATE = """You are an expert customer support intent classifier.
Analyze the following customer message and classify it into exactly one of the allowed intents.

Allowed Intents:
{intents_description}

Customer Message:
"{message}"

Respond strictly in valid JSON format:
{{
  "intent": "<EXACT_INTENT_NAME>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<concise explanation>"
}}
"""


class LLMClassifier:
    """Classifies customer message intents using an LLM."""

    def __init__(
        self,
        taxonomy: Optional[Dict[str, Dict[str, Any]]] = None,
        model_name: str = "gpt-4o-mini",
    ):
        self.taxonomy = taxonomy or load_taxonomy()
        self.model_name = model_name

    def _format_intents_desc(self) -> str:
        lines = []
        for name, meta in self.taxonomy.items():
            lines.append(f"- {name}: {meta.get('description', '')}")
        return "\n".join(lines)

    def classify(self, message: str) -> Dict[str, Any]:
        """Classify message intent.

        Args:
            message: Customer support message text.

        Returns:
            Dict containing intent, confidence, reasoning.
        """
        # Placeholder / heuristic fallback if API key is not configured
        intents_desc = self._format_intents_desc()
        prompt = INTENT_PROMPT_TEMPLATE.format(
            intents_description=intents_desc, message=message
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0.0,
                )
                content = response.choices[0].message.content
                return json.loads(content)
            except Exception as e:
                print(f"Warning: LLM classification API call failed ({e}). Using rule-based fallback.")

        # Keyword matching fallback
        lower_msg = message.lower()
        for intent, meta in self.taxonomy.items():
            keywords = meta.get("keywords", [])
            if any(kw in lower_msg for kw in keywords):
                return {
                    "intent": intent,
                    "confidence": 0.85,
                    "reasoning": "Matched intent keywords in message.",
                }

        first_intent = list(self.taxonomy.keys())[0] if self.taxonomy else "UNKNOWN"
        return {
            "intent": first_intent,
            "confidence": 0.4,
            "reasoning": "Default fallback classification.",
        }
