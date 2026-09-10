"""Grounded customer support reply generation using retrieved context and classified intent."""

import os
from typing import List, Dict, Any, Optional

REPLY_PROMPT_TEMPLATE = """You are a helpful, professional, and empathetic customer support agent.
Generate a concise, direct, and empathetic response to the customer.

Customer Query:
"{query}"

Classified Intent:
{intent}

Retrieved Knowledge/Historical Context:
{context}

Guidelines:
- Keep the tone polite, clear, and action-oriented.
- If relevant details (like order ID, tracking number, email) are needed, politely request them.
- Do not make up facts or unverified policy commitments.
- Ensure the answer aligns with the classified intent.

Support Reply:
"""


class ReplyGenerator:
    """Generates customer support replies using context and LLMs."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name

    def _format_context(self, context_items: List[Dict[str, Any]]) -> str:
        if not context_items:
            return "No historical context found."
        formatted = []
        for i, item in enumerate(context_items, 1):
            text = item.get("text", item.get("agent_response", str(item)))
            formatted.append(f"[{i}] {text}")
        return "\n".join(formatted)

    def generate(
        self,
        query: str,
        intent: str,
        context_items: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Generate support reply.

        Args:
            query: Customer inquiry.
            intent: Classified intent name.
            context_items: Retrieved reference resolutions or documents.

        Returns:
            Generated response string.
        """
        context_str = self._format_context(context_items or [])
        prompt = REPLY_PROMPT_TEMPLATE.format(
            query=query,
            intent=intent,
            context=context_str,
        )

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Warning: Reply generation API call failed ({e}). Using template fallback.")

        # Template-based fallback
        fallbacks = {
            "ORDER_STATUS_TRACKING": "Hello! I would be happy to help you check your order status. Could you please provide your order or tracking number?",
            "CANCELLATION_REFUND": "We apologize for the inconvenience. To process your cancellation or refund request, please share your order details and account email.",
            "TECHNICAL_SUPPORT": "We are sorry you're experiencing technical difficulties. Could you please share more details about the error message or device you are using?",
            "BILLING_PAYMENT_ISSUE": "Thank you for reaching out. Please send us your invoice reference and billing email so we can inspect the charge right away.",
            "COMPLAINT_ESCALATION": "We are deeply sorry for your frustrating experience. I am escalating your case directly to a senior support specialist who will reach out shortly.",
        }
        return fallbacks.get(
            intent,
            "Hello! Thank you for contacting customer support. How may we assist you further today?"
        )
