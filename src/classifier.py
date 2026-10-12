"""
Classifies a support ticket's category and urgency using an LLM with a
structured (Pydantic) output schema, so downstream code gets reliable
fields instead of parsing free text.
"""
import os
from typing import Literal

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()


class TicketClassification(BaseModel):
    category: Literal["billing", "technical", "account", "other"] = Field(
        description="The primary category of the support ticket."
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="How urgently this ticket needs a response."
    )
    confidence: Literal["low", "medium", "high"] = Field(
        default="high",
        description="How confident the classifier is in its category and urgency.",
    )
    reasoning: str = Field(
        description="One short sentence explaining the classification."
    )


CLASSIFICATION_PROMPT = """You are a support ticket triage classifier.

Classify the following ticket into:
- category: one of billing, technical, account, other
- confidence: one of low, medium, high (low = ticket is vague, mixed, or
  you are unsure of the category/urgency)
- urgency: one of low, medium, high (high = blocking work, financial risk,
  or security concern; medium = inconvenient but not blocking; low = minor
  or a feature request)

Subject: {subject}
Body: {body}
"""


# Override with the GEMINI_MODEL env var if Google retires/renames a model.
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def demo_mode() -> bool:
    """True when TRIAGE_DEMO=1: run offline with a keyword heuristic, no API key."""
    return os.getenv("TRIAGE_DEMO", "").lower() in ("1", "true", "yes")


def get_classifier_llm():
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0)
    return llm.with_structured_output(TicketClassification)


def classify_ticket(subject: str, body: str) -> TicketClassification:
    if demo_mode():
        from src.demo import demo_classify

        return demo_classify(subject, body)
    classifier = get_classifier_llm()
    prompt = CLASSIFICATION_PROMPT.format(subject=subject, body=body)
    return classifier.invoke(prompt)
