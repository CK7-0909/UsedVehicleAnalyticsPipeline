
from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import HTTPException, APIRouter
from pydantic import BaseModel, Field
import numpy as np
from ml.src.predict import predict

ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT_DIR / "ml" / "models" / "xgb_model_all.joblib"

router = APIRouter()

class VehicleInput(BaseModel):
    """Payload expected by the prediction endpoint."""

    manufacturer: str = Field(..., description="Vehicle manufacturer, e.g. Toyota")
    model: str = Field(..., description="Vehicle model, e.g. Camry")
    year: int = Field(..., ge=2000, le=2100, description="Vehicle model year")
    odometer: int = Field(..., ge=0, description="Odometer reading in miles")
    title_status: str = Field(..., description="Listing title status")
    transmission: str = Field(..., description="Transmission type")
    paint_color: str = Field(..., description="Primary exterior color")
    state: str = Field(..., description="Two-letter state abbreviation")

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame([self.model_dump()])
    

@router.post("/predict")
def predict_price(data: VehicleInput, model_path: Path = MODEL_PATH):
    try:
        df = data.to_frame()
        predictions = predict(df, str(model_path))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    price = float(predictions[0]) if len(predictions) else float("nan")
    return {"predicted_price": round(price, 2)}
