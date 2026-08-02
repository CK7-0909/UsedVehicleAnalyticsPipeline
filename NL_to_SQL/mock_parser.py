"""
Drop-in replacement for filter_parser.parse_filters() -- no API key, no
network call, no cost. Use this to test query_engine + FastAPI + React
wiring while your Anthropic key isn't set up yet, or just for fast iteration.

IMPORTANT: this does NOT test whether an LLM can correctly interpret
arbitrary phrasing -- it's a fixed lookup table for known questions. Treat
"parsing works" as unverified until you've also run the real parse_filters
(via Anthropic or a local model) at least once.
"""

_CANNED = {
    "cars under 26k, sedan, similar to an accord": {
        "price_min": None, "price_max": 26000, "year_min": None, "year_max": None,
        "body_type": "sedan", "reference_model": "Accord", "limit": None,
    },
    "show me suvs between 20000 and 35000": {
        "price_min": 20000, "price_max": 35000, "year_min": None, "year_max": None,
        "body_type": "suv", "reference_model": None, "limit": None,
    },
    "what trucks do you have under 40k": {
        "price_min": None, "price_max": 40000, "year_min": None, "year_max": None,
        "body_type": "truck", "reference_model": None, "limit": None,
    },
    "give me all sedans like a camry": {
        "price_min": None, "price_max": None, "year_min": None, "year_max": None,
        "body_type": "sedan", "reference_model": "Camry", "limit": None,
    },
    "car under 26k and older than 2021": {
        "price_min": None, "price_max": 26000, "year_min": None, "year_max": 2020,
        "body_type": None, "reference_model": None, "limit": None,
    },
}

_DEFAULT = {
    "price_min": None, "price_max": None, "year_min": None, "year_max": None,
    "body_type": None, "reference_model": None, "limit": None,
}


def parse_filters(question: str) -> dict:
    return _CANNED.get(question.strip().lower(), _DEFAULT)