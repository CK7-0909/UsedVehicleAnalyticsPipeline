"""Quickly compare how the pricing model reacts to different inputs.

Run inside the API container so all dependencies (joblib, pandas, etc.) are
available:

    docker compose exec api python scripts/probe_predictions.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from ml.src.predict import predict  # noqa: E402

MODEL_PATH = Path("ml/models/xgb_model_all.joblib")

# A realistic baseline pulled from the supported manufacturer/model list.
BASE_INPUT = {
    "manufacturer": "toyota",
    "model": "camry",
    "year": 2018,
    "odometer": 45000,
    "title_status": "clean",
    "transmission": "automatic",
    "paint_color": "black",
    "state": "CA",
}

# Each scenario overrides one or two categorical fields so you can see
# their specific impact while holding mileage/year constant.
SCENARIOS: Dict[str, Dict[str, object]] = {
    "base": {},
    "ford_f150": {"manufacturer": "ford", "model": "f-150"},
    "honda_civic": {"manufacturer": "honda", "model": "civic"},
    "manual_transmission": {"transmission": "manual"},
    "salvage_title": {"title_status": "salvage"},
    "bright_paint": {"paint_color": "white"},
    "new_york_listing": {"state": "NY"},
}


def run_scenario(name: str, overrides: Dict[str, object]) -> float:
    payload = {**BASE_INPUT, **overrides}
    df = pd.DataFrame([payload])
    prediction = predict(df, str(MODEL_PATH))
    return float(prediction[0])


def main() -> None:
    print("Comparing price predictions with constant mileage/year:\n")
    for name, overrides in SCENARIOS.items():
        price = run_scenario(name, overrides)
        modifiers = overrides or {"info": "base inputs"}
        print(f"{name:20s} ${price:,.2f}  {modifiers}")


if __name__ == "__main__":
    main()
