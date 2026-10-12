"""
Unit tests for the routing/decision policy. These don't require any LLM
call since they test decide_routing() directly against constructed
classification objects.

Run with:
    pytest tests/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.classifier import TicketClassification  # noqa: E402
from src.router import decide_routing  # noqa: E402


def make_classification(category="technical", urgency="low", confidence="high"):
    return TicketClassification(
        category=category, urgency=urgency, confidence=confidence, reasoning="test"
    )


def test_high_urgency_always_escalates():
    classification = make_classification(category="technical", urgency="high")
    decision, _ = decide_routing(classification)
    assert decision == "escalate"


def test_billing_always_escalates_even_if_low_urgency():
    classification = make_classification(category="billing", urgency="low")
    decision, _ = decide_routing(classification)
    assert decision == "escalate"


def test_low_urgency_non_billing_auto_responds():
    classification = make_classification(category="technical", urgency="low")
    decision, _ = decide_routing(classification)
    assert decision == "auto_respond"


def test_medium_urgency_non_billing_auto_responds():
    classification = make_classification(category="account", urgency="medium")
    decision, _ = decide_routing(classification)
    assert decision == "auto_respond"


def test_decision_always_includes_a_reason():
    classification = make_classification(category="other", urgency="high")
    decision, reason = decide_routing(classification)
    assert isinstance(reason, str) and len(reason) > 0


def test_low_confidence_escalates_even_if_otherwise_safe():
    classification = make_classification(category="technical", urgency="low", confidence="low")
    decision, reason = decide_routing(classification)
    assert decision == "escalate"
    assert "confidence" in reason.lower()


def test_demo_classifier_not_urgent_beats_urgent():
    from src.demo import demo_classify

    c = demo_classify("Feature request: dark mode", "Not urgent, just a nice-to-have.")
    assert c.urgency == "low"
