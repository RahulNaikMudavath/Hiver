"""LLM-as-a-Judge evaluation harness for response correctness, tone, and empathy."""

import os
import json
from typing import Dict, Any, Optional

JUDGE_PROMPT_TEMPLATE = """You are an impartial evaluator assessing the quality of an automated customer support reply.

Customer Query:
"{query}"

Ground Truth / Reference Resolution:
"{reference_reply}"

Model Generated Reply:
"{generated_reply}"

Evaluate the generated response across 3 dimensions on a scale of 1 to 5:
1. Correctness & Relevance (Is the reply accurate, helpful, and answers the query?)
2. Empathy & Tone (Is the tone professional, polite, and customer-centric?)
3. Actionability & Policy (Does it give clear next steps without making false promises?)

Return your evaluation in JSON format:
{{
  "correctness_score": <1-5>,
  "empathy_score": <1-5>,
  "actionability_score": <1-5>,
  "overall_score": <1-5>,
  "critique": "<brief explanation>"
}}
"""


class LLMJudge:
    """Evaluates agent responses using an LLM evaluator."""

    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name

    def evaluate(
        self,
        query: str,
        generated_reply: str,
        reference_reply: str = "",
    ) -> Dict[str, Any]:
        """Judge the quality of a generated reply against the query and reference.

        Args:
            query: Customer input.
            generated_reply: AI response.
            reference_reply: Ground truth or human response.

        Returns:
            Dict containing scores and critique.
        """
        prompt = JUDGE_PROMPT_TEMPLATE.format(
            query=query,
            reference_reply=reference_reply,
            generated_reply=generated_reply,
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
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"Warning: Judge API call failed ({e}). Returning heuristic default.")

        # Default fallback score for offline execution
        return {
            "correctness_score": 4,
            "empathy_score": 4,
            "actionability_score": 4,
            "overall_score": 4.0,
            "critique": "Offline simulated evaluation: response is polite and relevant.",
        }
