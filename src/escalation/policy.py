"""Escalation policy deciding whether a conversation requires human agent handoff."""

from typing import Dict, Any, List


class EscalationPolicy:
    """Evaluates rules, sentiment, and classifier confidence to determine escalation."""

    def __init__(
        self,
        confidence_threshold: float = 0.65,
        escalate_intents: List[str] = None,
    ):
        self.confidence_threshold = confidence_threshold
        self.escalate_intents = escalate_intents or [
            "COMPLAINT_ESCALATION",
            "BILLING_PAYMENT_ISSUE",
        ]
        self.escalation_keywords = [
            "lawyer",
            "sue",
            "fraud",
            "scam",
            "manager",
            "supervisor",
            "human",
            "terrible",
            "unacceptable",
        ]

    def evaluate(
        self,
        query: str,
        classification_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate whether to escalate the ticket.

        Args:
            query: Raw user message.
            classification_result: Output from intent classifier.

        Returns:
            Dict with should_escalate (bool), reason (str), and priority (str).
        """
        lower_query = query.lower()
        intent = classification_result.get("intent", "")
        confidence = float(classification_result.get("confidence", 1.0))

        # 1. Critical keyword rule
        matched_keywords = [kw for kw in self.escalation_keywords if kw in lower_query]
        if matched_keywords:
            return {
                "should_escalate": True,
                "reason": f"Escalation keywords detected: {', '.join(matched_keywords)}",
                "priority": "HIGH",
            }

        # 2. Specific escalation-required intents
        if intent in self.escalate_intents:
            return {
                "should_escalate": True,
                "reason": f"Intent '{intent}' mandates human specialist intervention.",
                "priority": "MEDIUM",
            }

        # 3. Low classification confidence
        if confidence < self.confidence_threshold:
            return {
                "should_escalate": True,
                "reason": f"Low classification confidence ({confidence:.2f} < {self.confidence_threshold:.2f}).",
                "priority": "LOW",
            }

        return {
            "should_escalate": False,
            "reason": "Standard automated response sufficient.",
            "priority": "NONE",
        }
