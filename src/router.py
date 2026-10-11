"""
Decision layer: given a ticket's classification, decide whether to
auto-respond or escalate to a human, and draft a suggested response
either way. Every decision carries an explicit, logged reason.
"""
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.classifier import TicketClassification

load_dotenv()

RESPONSE_DRAFT_PROMPT = """You are a helpful, concise support agent.

Draft a short (2-4 sentence) suggested response to the customer below.
If the ticket is billing-related or high urgency, acknowledge the issue
and reassure them a specialist will follow up shortly rather than
promising a resolution yourself.

Subject: {subject}
Body: {body}
"""


def decide_routing(classification: TicketClassification) -> tuple[str, str]:
    """
    Returns (decision, reason) where decision is 'auto_respond' or
    'escalate'.

    Simple, explainable policy:
    - high urgency -> escalate
    - billing category -> escalate (financial disputes need human review)
    - otherwise -> auto-respond
    """
    if classification.urgency == "high":
        return "escalate", "High urgency tickets are routed to a human for timely handling."
    if classification.category == "billing":
        return "escalate", "Billing/financial disputes default to human review."
    return "auto_respond", "Low/medium urgency, non-billing ticket — safe to auto-respond."


def draft_response(subject: str, body: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.4)
    prompt = RESPONSE_DRAFT_PROMPT.format(subject=subject, body=body)
    result = llm.invoke(prompt)
    return result.content
