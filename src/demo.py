"""
Offline demo mode (TRIAGE_DEMO=1). Uses simple keyword rules instead of
Gemini so the full pipeline can be shown without an API key. This is NOT
the real classifier -- it only exists to demonstrate the agent loop.
"""
from src.classifier import TicketClassification

BILLING = ("charge", "refund", "invoice", "billing", "payment", "subscription")
ACCOUNT = ("log in", "login", "password", "account", "sign in", "locked")
TECHNICAL = ("crash", "error", "bug", "slow", "not working", "broken", "freez")
HIGH = ("urgent", "asap", "blocking", "immediately", "cannot work", "security", "hacked")
LOW = ("feature request", "nice-to-have", "nice to have", "not urgent", "would be great")


def demo_classify(subject: str, body: str) -> TicketClassification:
    text = f"{subject} {body}".lower()
    if any(k in text for k in BILLING):
        category = "billing"
    elif any(k in text for k in ACCOUNT):
        category = "account"
    elif any(k in text for k in TECHNICAL):
        category = "technical"
    else:
        category = "other"

    if any(k in text for k in LOW):  # "not urgent" must win over "urgent"
        urgency = "low"
    elif any(k in text for k in HIGH):
        urgency = "high"
    else:
        urgency = "medium"

    confidence = "low" if category == "other" and urgency == "medium" else "high"
    return TicketClassification(
        category=category,
        urgency=urgency,
        confidence=confidence,
        reasoning="[demo] keyword-rule classification, not an LLM.",
    )


def demo_response(subject: str, body: str) -> str:
    return (
        f"[demo reply] Thanks for contacting us about \"{subject}\". "
        "We've logged your ticket and will follow up shortly."
    )
