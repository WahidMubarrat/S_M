# QueueStorm Ticket Sorter
bKash SUST CSE Carnival 2026 — Codex Community Hackathon | Mock Preliminary

Classifies customer support tickets using **FastAPI** + **Gemini 2.5 Flash**.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| POST | `/sort-ticket` | Classify a CRM ticket |

### POST /sort-ticket — Sample Request
```json
{
  "ticket_id": "T-001",
  "channel": "app",
  "locale": "en",
  "message": "I sent 5000 taka to a wrong number this morning, please help me get it back"
}
```

### Sample Response
```json
{
  "ticket_id": "T-001",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "Customer reports sending 5000 BDT to an incorrect recipient and is requesting a refund.",
  "human_review_required": true,
  "confidence": 0.95
}
```

---

## Local Setup

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd ticket-sorter

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run the server
uvicorn main:app --reload --port 8000
```

Server runs at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs

---

## Deploy on Render

1. Push this repo to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Set these in Render dashboard:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variable:** `GEMINI_API_KEY` = your key
5. Deploy — Render gives you a free HTTPS URL

---

## LLM Used
**Yes** — Google Gemini 2.5 Flash via `google-genai` SDK.
