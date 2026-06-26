import os
import json
import re
from google import genai

# ------------------------------------------------------------------ #
#  Put your Gemini API key in .env as:                                #
#  GEMINI_API_KEY=your_key_here                                       #
# ------------------------------------------------------------------ #
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are a ticket classification engine for a digital finance company (bKash).
Analyze the customer message and return ONLY a valid JSON object — no markdown, no explanation.

JSON shape:
{
  "case_type": "<wrong_transfer|payment_failed|refund_request|phishing_or_social_engineering|other>",
  "severity": "<low|medium|high|critical>",
  "department": "<customer_support|dispute_resolution|payments_ops|fraud_risk>",
  "agent_summary": "<1-2 neutral sentences for a support agent>",
  "confidence": <float 0.0-1.0>
}

Rules:
- case_type=wrong_transfer  → department=dispute_resolution, severity=high
- case_type=payment_failed  → department=payments_ops, severity=high
- case_type=phishing_or_social_engineering → department=fraud_risk, severity=critical
- case_type=refund_request  → department=dispute_resolution (if contested) or customer_support (if simple), severity=low/medium
- case_type=other           → department=customer_support, severity=low

CRITICAL SAFETY RULE:
The agent_summary must NEVER ask or mention sharing PIN, OTP, password, or full card number.

Return ONLY the JSON object. No extra text."""


BANNED_WORDS = ["pin", "otp", "password", "card number"]


def _sanitize_summary(summary: str) -> str:
    """Hard safety check — strip any accidental sensitive word prompts."""
    lowered = summary.lower()
    for word in BANNED_WORDS:
        if word in lowered:
            # Replace the whole sentence containing the banned phrase
            summary = re.sub(
                r"[^.]*" + re.escape(word) + r"[^.]*\.",
                "",
                summary,
                flags=re.IGNORECASE,
            ).strip()
    return summary or "Ticket received and is under review."


def classify_ticket(message: str, locale: str = "en") -> dict:
    user_prompt = f"Locale: {locale}\nCustomer message: {message}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "temperature": 0.1,   # low temp = consistent structured output
        },
    )

    raw = response.text.strip()

    # Strip markdown fences if Gemini wraps with ```json ... ```
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r"```$", "", raw).strip()

    data = json.loads(raw)

    # Sanitize agent summary
    data["agent_summary"] = _sanitize_summary(data.get("agent_summary", ""))

    # Enforce confidence bounds
    data["confidence"] = max(0.0, min(1.0, float(data.get("confidence", 0.8))))

    return data
