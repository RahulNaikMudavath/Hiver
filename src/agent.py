"""Unified AI Customer Support Agent Orchestration."""

from typing import Dict, Any, Optional
from src.retrieval.retrieve import Retriever
from src.classification.llm_classifier import LLMClassifier
from src.escalation.policy import EscalationPolicy
from src.generation.reply_generator import ReplyGenerator


class SupportAgent:
    """End-to-end customer support agent connecting retrieval, classification, escalation, and reply generation."""

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        classifier: Optional[LLMClassifier] = None,
        escalation_policy: Optional[EscalationPolicy] = None,
        reply_generator: Optional[ReplyGenerator] = None,
    ):
        self.retriever = retriever or Retriever()
        self.classifier = classifier or LLMClassifier()
        self.escalation_policy = escalation_policy or EscalationPolicy()
        self.reply_generator = reply_generator or ReplyGenerator()

    def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process an incoming customer query through the pipeline.

        Args:
            user_message: Incoming customer message text.

        Returns:
            Dict containing intent, confidence, retrieved context, escalation decision, and reply.
        """
        # Step 1: Intent Classification
        classification = self.classifier.classify(user_message)
        intent = classification.get("intent", "UNKNOWN")

        # Step 2: Context Retrieval
        retrieved_context = self.retriever.retrieve(user_message, top_k=3)

        # Step 3: Escalation Check
        escalation = self.escalation_policy.evaluate(
            query=user_message,
            classification_result=classification,
        )

        # Step 4: Response Generation
        reply = self.reply_generator.generate(
            query=user_message,
            intent=intent,
            context_items=retrieved_context,
        )

        return {
            "query": user_message,
            "intent": intent,
            "confidence": classification.get("confidence", 1.0),
            "reasoning": classification.get("reasoning", ""),
            "retrieved_context": retrieved_context,
            "escalation": escalation,
            "reply": reply,
        }


if __name__ == "__main__":
    agent = SupportAgent()
    sample_query = "Where is my package? It's been 5 days and tracking hasn't updated."
    result = agent.process_message(sample_query)
    print("Agent Pipeline Output:")
    print(result)
