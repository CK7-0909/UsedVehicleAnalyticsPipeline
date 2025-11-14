from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable, Optional

import pandas as pd
import plotly.express as px
import streamlit as st

DEFAULT_MANUFACTURER_MODELS = {
    "jeep": {
        "display": "Jeep",
        "models": [{"key": "compass", "display": "Compass"}],
    },
    "toyota": {
        "display": "Toyota",
        "models": [{"key": "corolla", "display": "Corolla"}],
    },
    "honda": {
        "display": "Honda",
        "models": [{"key": "civic", "display": "Civic"}],
    },
}

DEFAULT_COLORS: list[str] = ["black", "white", "silver", "blue", "red"]
DEFAULT_STATES: list[str] = ["CA", "TX", "NY", "FL", "WA"]
DEFAULT_TRANSMISSIONS: list[str] = ["automatic", "manual"]
VEHICLE_SPECS_DIR = Path("data") / "vehicle_specs"


@lru_cache(maxsize=1)
def _load_manufacturer_models():
    lookup_path = VEHICLE_SPECS_DIR / "vehicle_models_by_manufacturer.parquet"
    required_cols = [
        "manufacturer_key",
        "manufacturer_display",
        "model_key",
        "model_display",
    ]

    if not lookup_path.exists():
        return DEFAULT_MANUFACTURER_MODELS

    try:
        df = pd.read_parquet(lookup_path)
    except Exception:
        return DEFAULT_MANUFACTURER_MODELS

    if not set(required_cols).issubset(df.columns):
        return DEFAULT_MANUFACTURER_MODELS

    df = (
        df[required_cols]
        .dropna()
        .drop_duplicates()
        .sort_values(["manufacturer_display", "model_display"])
    )

    if df.empty:
        return DEFAULT_MANUFACTURER_MODELS

    manufacturer_models = {}
    for manufacturer_key, group in df.groupby("manufacturer_key"):
        models = [
            {"key": row.model_key, "display": row.model_display}
            for row in group.itertuples()
        ]
        if models:
            manufacturer_models[manufacturer_key] = {
                "display": group["manufacturer_display"].iloc[0],
                "models": models,
            }

    return manufacturer_models or DEFAULT_MANUFACTURER_MODELS


def _load_category_values(
    file_path: Path,
    column: str,
    transform: Optional[Callable[[pd.Series], pd.Series]] = None,
    fallback: Optional[Iterable[str]] = None,
) -> list[str]:
    try:
        if file_path.exists():
            series = pd.read_parquet(file_path)[column].dropna().astype(str).str.strip()
            if transform is not None:
                series = transform(series)
            values = sorted(series.unique())
            if values:
                return values
    except Exception:
        pass
    return list(fallback or [])


def plot_actual_vs_predicted(y_test, y_pred):
    st.subheader("Time to get a car!")

    fig = px.scatter(
        x=y_test,
        y=y_pred,
        labels={"x": "Actual Price", "y": "Predicted Price"},
        title="Actual vs Predicted Prices",
    )
    fig.add_shape(
        type="line",
        line=dict(dash="dash"),
        x0=y_test.min(),
        y0=y_test.min(),
        x1=y_test.max(),
        y1=y_test.max(),
    )
    st.plotly_chart(fig)


def inputData():
    st.subheader("Input Car Features for Price Prediction")
    st.write("Adjust the features to see how they affect the predicted price.")
    # Create layout columns
    col1, col2, col3, col4 = st.columns(4)
    col5, col6, col7, col8 = st.columns(4)

    manufacturer_models = _load_manufacturer_models()
    manufacturer_options = sorted(
        manufacturer_models.keys(),
        key=lambda key: manufacturer_models[key]["display"],
    )

    with col1:
        manufacturer_key = st.selectbox(
            "Manufacturer",
            manufacturer_options,
            format_func=lambda key: manufacturer_models[key]["display"],
        )

    manufacturer_entry = manufacturer_models[manufacturer_key]
    manufacturer_display = manufacturer_entry.get("display", manufacturer_key.title())

    selected_models = manufacturer_entry.get("models") or []
    if not selected_models:
        first_default = next(iter(DEFAULT_MANUFACTURER_MODELS.values()))
        selected_models = first_default["models"]

    model_keys = [entry["key"] for entry in selected_models]
    model_display_map = {entry["key"]: entry["display"] for entry in selected_models}

    with col2:
        model_key = st.selectbox(
            "Model",
            model_keys,
            format_func=lambda key: model_display_map.get(key, key.title()),
        )
    model_entry = next(
        (entry for entry in selected_models if entry["key"] == model_key), None
    )
    model_display = (
        model_entry["display"]
        if model_entry is not None
        else model_display_map.get(model_key, model_key.title())
    )

    with col3:
        year = st.number_input("Year", min_value=2000, max_value=2025, step=1)
    with col4:
        odometer = st.number_input("Odometer (miles)", min_value=0, step=1000)

    with col5:
        title_status = st.selectbox("Title Status", ["clean", "salvage", "rebuilt"])
    transmission_path = VEHICLE_SPECS_DIR / f"vehicle_transmission_{model_key}.parquet"
    transmission_options = _load_category_values(
        transmission_path,
        "transmission",
        transform=lambda s: s.str.lower(),
        fallback=DEFAULT_TRANSMISSIONS,
    )
    with col6:
        transmission = st.selectbox(
            "Transmission",
            transmission_options,
            format_func=lambda value: value.title(),
        )

    color_path = VEHICLE_SPECS_DIR / f"vehicle_color_{model_key}.parquet"
    color_options = _load_category_values(
        color_path,
        "paint_color",
        transform=lambda s: s.str.lower(),
        fallback=DEFAULT_COLORS,
    )
    with col7:
        paint_color = st.selectbox(
            "Paint Color", color_options, format_func=lambda value: value.title()
        )

    state_path = VEHICLE_SPECS_DIR / f"vehicle_state_{model_key}.parquet"
    state_options = _load_category_values(
        state_path,
        "state",
        transform=lambda s: s.str.upper(),
        fallback=DEFAULT_STATES,
    )
    with col8:
        state = st.selectbox("State", state_options)

    df = pd.DataFrame(
        [
            {
                "manufacturer": manufacturer_display,
                "model": model_display,
                "year": year,
                "odometer": odometer,
                "title_status": title_status,
                "transmission": transmission,
                "paint_color": paint_color,
                "state": state,
            }
        ]
    )

    categorical_cols = ["title_status", "transmission", "paint_color", "state"]
    df[categorical_cols] = df[categorical_cols].apply(lambda s: s.str.lower().str.strip())

    return df
