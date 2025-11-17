from fastapi import APIRouter
import pandas as pd
import os

router = APIRouter()

@router.get("/metrics/actual-vs-predicted")
def graph(file_path: str = "ml/artifacts/evaluation_all.parquet"):

    if not os.path.exists(file_path):
        return {"error": "Evaluation file not found"}

    df = pd.read_parquet(file_path)

    # The parquet may use either legacy y_* names or descriptive ones.
    actual_key = "y_test" if "y_test" in df.columns else (
        "y_true" if "y_true" in df.columns else "actual_price"
    )
    pred_key = "y_pred" if "y_pred" in df.columns else "predicted_price"

    missing = [key for key in (actual_key, pred_key) if key not in df.columns]
    if missing:
        return {"error": f"Evaluation file missing columns: {missing}"}

    return {
        "y_test": df[actual_key].tolist(),
        "y_pred": df[pred_key].tolist()
    }
