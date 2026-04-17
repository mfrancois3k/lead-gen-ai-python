"""
ai_agent.py — GPT-4o lead scoring module.

Sends each lead's data + your Ideal Customer Profile (ICP) to GPT-4o
and receives a structured Hot / Warm / Cold classification with a
confidence score and a one-line reason.
"""

import json
from typing import Any
from openai import OpenAI, OpenAIError

SYSTEM_PROMPT = """\
You are an expert sales development representative (SDR) who specialises in
qualifying leads for local service business clients.

Your job is to evaluate a single business lead against the client's
Ideal Customer Profile (ICP) and return a structured JSON classification.

Classification rules:
  Hot  — Strong ICP match; high conversion probability. Pursue immediately.
  Warm — Moderate match; worth nurturing with follow-up.
  Cold — Poor match or missing critical info; deprioritise.

Always respond with ONLY a valid JSON object — no markdown, no extra text.
"""

USER_PROMPT_TEMPLATE = """\
## Ideal Customer Profile (ICP)
{icp}

## Lead Information
{lead_json}

Classify this lead. Respond with:
{{
  "score":      "Hot" | "Warm" | "Cold",
  "confidence": <float 0.0 - 1.0>,
  "reason":     "<one concise sentence explaining the classification>"
}}
"""


def score_lead(lead: dict[str, Any], icp_criteria: str, api_key: str) -> dict:
    """
    Score a single lead using GPT-4o.

    Returns dict with keys: score, confidence, reason.
    Falls back gracefully on API errors so the pipeline never crashes.
    """
    client = OpenAI(api_key=api_key)

    clean_lead = {
        k: v for k, v in lead.items()
        if k not in ("Domain_Status", "Email_MX_Error", "Email_MX_Valid",
                     "Domain_Live", "AI_Score", "Confidence", "Reason")
        and v not in (None, "", "N/A")
    }

    user_message = USER_PROMPT_TEMPLATE.format(
        icp=icp_criteria.strip(),
        lead_json=json.dumps(clean_lead, indent=2),
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=200,
        )
        result     = json.loads(response.choices[0].message.content)
        score      = result.get("score", "N/A")
        if score not in ("Hot", "Warm", "Cold"):
            score  = "N/A"
        confidence = max(0.0, min(1.0, float(result.get("confidence", 0.0))))
        reason     = str(result.get("reason", ""))[:300]
        return {"score": score, "confidence": confidence, "reason": reason}

    except (OpenAIError, json.JSONDecodeError, KeyError, ValueError) as exc:
        return {"score": "Error", "confidence": 0.0, "reason": f"API error: {exc}"}
