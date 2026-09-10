"""Unit and integration tests for SupportAgent."""

import pytest
from src.agent import SupportAgent


def test_agent_process_message():
    agent = SupportAgent()
    res = agent.process_message("Where is my package? Tracking number 987654")

    assert "query" in res
    assert "intent" in res
    assert "confidence" in res
    assert "escalation" in res
    assert "reply" in res

    assert isinstance(res["escalation"], dict)
    assert "should_escalate" in res["escalation"]
    assert len(res["reply"]) > 0


def test_agent_escalation_trigger():
    agent = SupportAgent()
    res = agent.process_message("This service is unacceptable, I want to talk to your manager right now!")

    assert res["escalation"]["should_escalate"] is True
    assert res["escalation"]["priority"] in ["HIGH", "MEDIUM"]
