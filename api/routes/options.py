from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import APIRouter, HTTPException, Query


ROOT_DIR = Path(__file__).resolve().parents[2]
SPEC_DIR = ROOT_DIR / "ml" / "data" / "vehicle_specs"
MODELS_FILE = SPEC_DIR / "vehicle_models_by_manufacturer.parquet"

router = APIRouter(prefix="/options", tags=["options"])


def _normalize(value: str) -> str:
    return value.strip().lower()


@lru_cache(maxsize=1)
def _load_models_df() -> pd.DataFrame:
    if not MODELS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="Vehicle metadata not found. Train the model or provide the parquet artifacts.",
        )
    return pd.read_parquet(MODELS_FILE)


def _read_attribute_list(prefix: str, model_key: str, column: str) -> List[str]:
    path = SPEC_DIR / f"{prefix}_{model_key}.parquet"
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    values = (
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .drop_duplicates()
    )
    return sorted(values.tolist())


def _get_model_row(manufacturer: str, model: str) -> pd.Series:
    df = _load_models_df()
    mask = (
        df["manufacturer_display"].str.lower().eq(_normalize(manufacturer))
        & df["model_display"].str.lower().eq(_normalize(model))
    )
    if not mask.any():
        raise HTTPException(
            status_code=404,
            detail=f"No metadata found for {manufacturer} {model}",
        )
    return df[mask].iloc[0]


@router.get("/manufacturers")
def list_manufacturers():
    df = _load_models_df()
    manufacturers = sorted(df["manufacturer_display"].drop_duplicates().tolist())
    return {"manufacturers": manufacturers}


@router.get("/models")
def list_models(manufacturer: str = Query(..., description="Manufacturer name, e.g. Toyota")):
    df = _load_models_df()
    target = _normalize(manufacturer)
    subset = df[df["manufacturer_display"].str.lower() == target]
    if subset.empty:
        raise HTTPException(status_code=404, detail=f"Manufacturer '{manufacturer}' not found")
    models = sorted(subset["model_display"].drop_duplicates().tolist())
    return {"manufacturer": subset.iloc[0]["manufacturer_display"], "models": models}


@router.get("/model-details")
def model_details(
    manufacturer: str = Query(..., description="Manufacturer name"),
    model: str = Query(..., description="Model name"),
):
    row = _get_model_row(manufacturer, model)
    model_key = row["model_key"]
    colors = _read_attribute_list("vehicle_color", model_key, "paint_color")
    transmissions = _read_attribute_list("vehicle_transmission", model_key, "transmission")
    states = _read_attribute_list("vehicle_state", model_key, "state")
    return {
        "manufacturer": row["manufacturer_display"],
        "model": row["model_display"],
        "colors": colors,
        "transmissions": transmissions,
        "states": states,
    }
