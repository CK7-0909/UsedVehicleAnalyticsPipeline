from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ml.data.snowflake.sf_connection import query_to_df
from ml.src.predict import predict

app = FastAPI(title="Used Vehicle Analytics API")
MODEL_PATH = Path("ml/models/xgb_model_all.joblib")
class VehicleInput(BaseModel):
    """Payload expected by the prediction endpoint."""

    manufacturer: str = Field(..., description="Vehicle manufacturer, e.g. Toyota")
    model: str = Field(..., description="Vehicle model, e.g. Camry")
    year: int = Field(..., ge=1980, le=2100, description="Vehicle model year")
    odometer: int = Field(..., ge=0, description="Odometer reading in miles")
    title_status: str = Field(..., description="Listing title status")
    transmission: str = Field(..., description="Transmission type")
    paint_color: str = Field(..., description="Primary exterior color")
    state: str = Field(..., description="Two-letter state abbreviation")

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([self.model_dump()])


@lru_cache(maxsize=1)
def _validated_model_path() -> str:
    """Ensure the configured model path exists before attempting predictions."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at '{MODEL_PATH}'. "
            "Run the training pipeline or update MODEL_PATH."
        )
    return str(MODEL_PATH)


# --- Health check ---
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API and dbt pipeline ready"}


# --- Snowflake query example ---
@app.get("/vehicles")
def get_vehicle_count():
    df = query_to_df()
    count = len(df)
    return {"total_vehicles": count}


# --- ML prediction endpoint ---
@app.post("/predict")
def predict_price(data: VehicleInput):
    try:
        df = data.to_frame()
        predictions = predict(df, model_path=_validated_model_path())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    price = float(predictions[0]) if len(predictions) else float("nan")
    return {"predicted_price": round(price, 2)}
