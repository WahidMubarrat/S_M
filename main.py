from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# Loads GEMINI_API_KEY from .env automatically during local development
# On Render/Railway, set the env var in the dashboard instead
load_dotenv()

from models import TicketRequest, TicketResponse
from classifier import classify_ticket

app = FastAPI(title="QueueStorm Ticket Sorter", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ticket-sorter"}


@app.post("/sort-ticket", response_model=TicketResponse)
def sort_ticket(body: TicketRequest):
    try:
        result = classify_ticket(
            message=body.message,
            locale=body.locale or "en",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

    # Derive human_review_required from result
    human_review = (
        result["severity"] == "critical"
        or result["case_type"] == "phishing_or_social_engineering"
    )

    return TicketResponse(
        ticket_id=body.ticket_id,
        case_type=result["case_type"],
        severity=result["severity"],
        department=result["department"],
        agent_summary=result["agent_summary"],
        human_review_required=human_review,
        confidence=result["confidence"],
    )
