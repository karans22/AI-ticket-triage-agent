"""
Orchestrates the full agent loop for a batch of tickets:
classify -> decide routing -> draft response -> log decision.

Run with:
    python -m src.agent
"""
from pathlib import Path

import pandas as pd

from src.classifier import classify_ticket
from src.router import decide_routing, draft_response

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_tickets.csv"
LOG_PATH = Path(__file__).resolve().parent.parent / "logs" / "decisions.csv"


def process_ticket(ticket_id: str, subject: str, body: str) -> dict:
    classification = classify_ticket(subject, body)
    decision, reason = decide_routing(classification)
    response = draft_response(subject, body)

    return {
        "ticket_id": ticket_id,
        "subject": subject,
        "category": classification.category,
        "urgency": classification.urgency,
        "classification_reasoning": classification.reasoning,
        "decision": decision,
        "decision_reason": reason,
        "suggested_response": response,
    }


def run_batch(csv_path: Path = DATA_PATH, log_path: Path = LOG_PATH) -> pd.DataFrame:
    tickets = pd.read_csv(csv_path)
    results = []

    for _, row in tickets.iterrows():
        print(f"Processing {row['ticket_id']}...")
        result = process_ticket(row["ticket_id"], row["subject"], row["body"])
        results.append(result)

    results_df = pd.DataFrame(results)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(log_path, index=False)
    print(f"\nProcessed {len(results_df)} tickets. Decisions logged to {log_path}")

    escalated = (results_df["decision"] == "escalate").sum()
    print(f"Escalated: {escalated} | Auto-responded: {len(results_df) - escalated}")

    return results_df


if __name__ == "__main__":
    run_batch()
