# AI Ticket Triage Agent

A lightweight AI agent that classifies incoming support tickets, drafts a
suggested response, and decides whether to auto-respond or escalate to a
human — rather than just returning a category label.

This goes one step past a plain NLP classifier: it makes and logs a
**decision** with a **reason**, which is the core idea behind an "agent"
as opposed to a static model.

## Why this project

Enterprise AI/ML roles increasingly ask for exposure to AI Agents, not
just classical ML or single-shot LLM calls. This project demonstrates a
minimal, understandable agent loop — classify → decide → act → log — that
maps directly onto real operations use cases like reducing average
handling time (AHT) for support queues.

## Architecture

```
Incoming Ticket (text)
        │
        ▼
 Classifier (src/classifier.py)
   - category (billing / technical / account / other)
   - urgency (low / medium / high)
        │
        ▼
 Router (src/router.py)
   - decides: auto-respond | escalate to human
   - drafts a suggested response either way
        │
        ▼
 Agent Orchestrator (src/agent.py)
   - runs classify → route → log for each ticket
   - writes a decision log with reasoning (logs/decisions.csv)
        │
        ▼
   Streamlit dashboard (app.py) to review tickets + decisions
```

## Tech stack

- **LangChain** + **Google Gemini API** — classification and response drafting
- **Pandas** — ticket data handling and decision logging
- **Streamlit** — dashboard to review tickets and agent decisions
- **Python 3.10+**

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your free Gemini API key from
   [Google AI Studio](https://aistudio.google.com/app/apikey):
   ```bash
   cp .env.example .env
   ```

3. Run the agent on the sample ticket batch:
   ```bash
   python -m src.agent
   ```
   This processes `data/sample_tickets.csv` and writes decisions to
   `logs/decisions.csv`.

4. (Optional) Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

## Project structure

```
ai-ticket-triage-agent/
├── app.py                  # Streamlit dashboard
├── src/
│   ├── classifier.py        # LLM-based category/urgency classification
│   ├── router.py             # Decision logic: auto-respond vs escalate
│   └── agent.py               # Orchestrates classify -> route -> log
├── data/
│   └── sample_tickets.csv    # Synthetic sample tickets
├── logs/                     # Decision logs land here (gitignored)
├── tests/
│   └── test_router.py
├── requirements.txt
└── .env.example
```

## Design notes / decision policy

The router currently escalates to a human when **any** of the following
is true:
- Urgency is classified as `high`
- Category is `billing` (financial disputes default to human review)
- The classifier's own confidence signal is low

This is intentionally a simple, explainable policy — every escalation
decision is logged with the reason, which matters more for a first
version than routing sophistication.

## Extending this project

- Replace the rule-based router with a second LLM call that reasons about
  the decision explicitly (true "agent" reasoning step).
- Add a feedback loop: when a human overrides the agent's decision, log
  it and use it to refine the routing policy over time.
- Swap the synthetic ticket data for a public dataset (e.g. a Kaggle
  customer-support dataset) for more realistic evaluation.
- Add integration tests that mock the LLM call so the pipeline can be
  tested without API usage.

## Status

Actively developed as a personal project exploring applied AI agents for
enterprise operations use cases.
