"""
Layer 1: Natural language question -> structured filter dict.

If an Anthropic API key and library are available, this uses Anthropic.
Otherwise it falls back to a local mock parser so the API can run.
"""

import importlib.util
import json
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_AVAILABLE = importlib.util.find_spec("anthropic") is not None

if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
    from anthropic import Anthropic
    client = Anthropic()
else:
    client = None

SYSTEM = """Extract search filters from a car-shopping question.
Return ONLY valid JSON, no other text, no markdown code fences, no ```json``` blocks -- just the raw JSON object starting with {.
With these keys:
- price_min: number or null
- price_max: number or null
- year_min: number or null
- year_max: number or null
- body_type: string or null (lowercase, e.g. "sedan", "suv", "truck")
- reference_model: string or null (a specific car model mentioned as a comparison point, e.g. "Accord")
- limit: number or null (null means "all matches")

Notes:
- "26k" or "26 grand" means 26000. Always expand shorthand to a full number.
- If the question says "all" or doesn't mention a count, limit should be null.
- Year boundary convention (be precise about strict vs inclusive):
  - "older than 2021"   -> year_max = 2020 (strictly before 2021)
  - "2021 or older"     -> year_max = 2021 (inclusive)
  - "newer than 2021"   -> year_min = 2022 (strictly after 2021)
  - "2021 or newer"     -> year_min = 2021 (inclusive)

Examples:
Q: "cars under 26k, sedan, similar to an Accord"
A: {"price_min": null, "price_max": 26000, "year_min": null, "year_max": null, "body_type": "sedan", "reference_model": "Accord", "limit": null}

Q: "car under 26k and older than 2021"
A: {"price_min": null, "price_max": 26000, "year_min": null, "year_max": 2020, "body_type": null, "reference_model": null, "limit": null}
"""


def _fallback_parse_filters(question: str) -> dict:
    from .mock_parser import parse_filters as _mock_parse_filters
    return _mock_parse_filters(question)


def parse_filters(question: str, max_retries: int = 2) -> dict:
    if client is None:
        return _fallback_parse_filters(question)

    last_error = None
    for attempt in range(max_retries + 1):
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=200,
            system=SYSTEM,
            messages=[{"role": "user", "content": question}],
        )
        text = resp.content[0].text.strip()
        # Defensive: strip markdown code fences even though the prompt says
        # not to include them -- models sometimes add them out of habit anyway.
        if text.startswith("```"):
            text = text[3:]
            if text.lower().startswith("json"):
                text = text[4:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_error = e
            continue
    raise ValueError(
        f"Could not parse filters after {max_retries + 1} attempts. "
        f"Last raw response: {text!r}"
    ) from last_error