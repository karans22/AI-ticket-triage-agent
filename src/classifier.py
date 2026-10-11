"""
Classifies a support ticket's category and urgency using an LLM with a
structured (Pydantic) output schema, so downstream code gets reliable
fields instead of parsing free text.
"""
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
    reasoning: str = Field(
        description="One short sentence explaining the classification."
    )


CLASSIFICATION_PROMPT = """You are a support ticket triage classifier.

Classify the following ticket into:
- category: one of billing, technical, account, other
- urgency: one of low, medium, high (high = blocking work, financial risk,
  or security concern; medium = inconvenient but not blocking; low = minor
  or a feature request)

Subject: {subject}
Body: {body}
"""


def get_classifier_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    return llm.with_structured_output(TicketClassification)


def classify_ticket(subject: str, body: str) -> TicketClassification:
    classifier = get_classifier_llm()
    prompt = CLASSIFICATION_PROMPT.format(subject=subject, body=body)
    return classifier.invoke(prompt)
