from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.data.snowflake.sf_connection import query_to_df
from api.routes.predict import router as predict_router
from api.routes.evaluation import router as eval_router
from api.routes.options import router as options_router

app = FastAPI(title="Used Vehicle Analytics API")

# Allow the React dev server to call the API locally.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3200",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


FILE_PATH = Path("ml_artifacts/evaluation_results.parquet")
MODEL_PATH = Path("ml/models/xgb_model_all.joblib")

app.include_router(predict_router)
app.include_router(eval_router)
app.include_router(options_router)
