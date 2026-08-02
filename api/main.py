from __future__ import annotations
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from NL_to_SQL.filter_parser import parse_filters
from NL_to_SQL.query_engine import run_query
from api.routes.predict import router as predict_router
from api.routes.evaluation import router as eval_router
from api.routes.options import router as options_router

ROOT_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(title="Used Vehicle Analytics API")

@app.get("/")
def root():
    return {"message": "Used Vehicle Analytics API is running"}
# Allow the React dev server to call the API locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3200",
        "http://127.0.0.1:3200",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# --- Health check ---
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API and dbt pipeline ready"}


DATASET_PATH = ROOT_DIR / "ml" / "data" / "80K_Rows.csv"

@lru_cache(maxsize=1)
def _load_vehicle_data() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Dataset not found: {DATASET_PATH}")
    return pd.read_csv(DATASET_PATH)


@app.get("/vehicles")
def get_vehicle_count():
    df = _load_vehicle_data()
    return {"total_vehicles": len(df)}


FILE_PATH = ROOT_DIR / "ml_artifacts" / "evaluation_results.parquet"
MODEL_PATH = ROOT_DIR / "ml" / "models" / "xgb_model_all.joblib"

app.include_router(predict_router)
app.include_router(eval_router)
app.include_router(options_router)

 
class Question(BaseModel):
    question: str

@app.post("/vehicles/ask")
def vehicles_ask(q: Question):
    filters = parse_filters(q.question)
    results = run_query(filters)
    results_json = results.head(20).replace({np.nan: None}).to_dict(orient="records")
    return {
        "filters_used": filters,
        "count": len(results),
        "results": results_json,
    }