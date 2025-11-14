import datetime as dt
import hashlib
import re
from pathlib import Path
import pandas as pd
from typing import Optional

CATEGORICAL_COLUMNS: list[str] = [
    "manufacturer",
    "model",
    "title_status",
    "transmission",
    "paint_color",
    "state",
]

def _make_key(raw_value: str) -> str:
    """Create a filesystem-safe, deterministic key from a categorical value."""
    value = "" if raw_value is None else str(raw_value)
    value = value.strip()
    if not value:
        base = ""
    else:
        normalized = re.sub(r"\s+", " ", value.lower())
        base = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    digest = hashlib.sha1(value.lower().encode("utf-8")).hexdigest()[:8] if value else "00000000"
    if base:
        base = base[:80].rstrip("-")
        return f"{base}-{digest}"
    return digest


SUPPORTED_MODEL_PAIRS = [
    ("jeep", "compass"),
    ("jeep", "grand cherokee"),
    ("jeep", "wrangler"),
    ("toyota", "corolla"),
    ("toyota", "camry"),
    ("toyota", "rav4"),
    ("toyota", "highlander"),
    ("honda", "accord"),
    ("honda", "civic"),
    ("honda", "cr-v"),
    ("ford", "escape"),
    ("ford", "f-150"),
    ("ford", "mustang"),
    ("chevrolet", "malibu"),
    ("chevrolet", "silverado"),
    ("chevrolet", "tahoe"),
    ("nissan", "altima"),
    ("nissan", "sentra"),
    ("dodge", "charger"),
    ("kia", "forte"),
    ("subaru", "outback"),
    ("subaru", "forester"),
    ("subaru", "impreza"),
    ("subaru", "crosstrek"),
]
SUPPORTED_MODEL_KEY_SET = {_make_key(model) for _, model in SUPPORTED_MODEL_PAIRS}
SUPPORTED_MODEL_PAIR_SET = {
    (manufacturer.strip().lower(), model.strip().lower()) for manufacturer, model in SUPPORTED_MODEL_PAIRS
}


def find_age(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Create 'age' feature
    df = df.dropna(subset=["year"])
    df["age"] = dt.datetime.now().year - df["year"]

    return df

def filter_price(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Filter out unrealistic prices
    df = df[(df["price"] > 2000) & (df["price"] < 100000)]

    return df


def extract_colors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Extract primary color from paint_color
    df["paint_color"] = df["paint_color"].str.split("/").str[0].str.strip().str.lower()
    return df


def extract_states(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Standardize state names to uppercase
    df["state"] = df["state"].str.upper().str.strip()
    return df


def extract_transmissions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transmission"] = df["transmission"].astype(str).str.strip().str.lower()
    return df



def _standardize_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[CATEGORICAL_COLUMNS] = df[CATEGORICAL_COLUMNS].apply(
        lambda col: col.astype(str).str.strip().str.lower()
    )
    return df

VEHICLE_SPECS_DIR = Path("ml/data") / "vehicle_specs"


def _write_manufacturer_model_lookup(df: pd.DataFrame) -> None:
    lookup_path = VEHICLE_SPECS_DIR / "vehicle_models_by_manufacturer.parquet"
    manufacturer_models = (
        df[["manufacturer", "model"]]
        .dropna()
        .assign(
            manufacturer_display=lambda data: data["manufacturer"].astype(str).str.strip(),
            model_display=lambda data: data["model"].astype(str).str.strip(),
        )
    )
    manufacturer_models = manufacturer_models[
        manufacturer_models.apply(
            lambda row: (row["manufacturer_display"].lower(), row["model_display"].lower())
            in SUPPORTED_MODEL_PAIR_SET,
            axis=1,
        )
    ].copy()
    manufacturer_models["manufacturer_key"] = manufacturer_models["manufacturer_display"].map(_make_key)
    manufacturer_models["model_key"] = manufacturer_models["model_display"].map(_make_key)
    manufacturer_models = (
        manufacturer_models[
            ["manufacturer_key", "manufacturer_display", "model_key", "model_display"]
        ]
        .drop_duplicates()
        .sort_values(["manufacturer_display", "model_display"])
    )
    if not manufacturer_models.empty:
        lookup_path.parent.mkdir(parents=True, exist_ok=True)
        manufacturer_models.to_parquet(lookup_path, index=False)


def _write_model_attribute_files(
    df_color: pd.DataFrame,
    df_state: pd.DataFrame,
    df_transmission: pd.DataFrame,
) -> None:
    target_dir = VEHICLE_SPECS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    def _prepare(df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=["model"]).copy()
        df["model_display"] = df["model"].astype(str).str.strip()
        df["model_key"] = df["model_display"].map(_make_key)
        df = df[df["model_key"].isin(SUPPORTED_MODEL_KEY_SET)]
        return df

    df_color = _prepare(df_color)
    df_state = _prepare(df_state)
    df_transmission = _prepare(df_transmission)

    def _write(df: pd.DataFrame, value_column: str, transform, prefix: str) -> None:
        for model_key, group in df.groupby("model_key"):
            if not model_key or model_key == "00000000":
                continue
            values = (
                group[value_column]
                .dropna()
                .astype(str)
                .str.strip()
            )
            if transform is not None:
                values = transform(values)
            values = (
                values[values != ""]
                .drop_duplicates()
                .sort_values()
            )
            if values.empty:
                continue
            out_path = target_dir / f"{prefix}_{model_key}.parquet"
            values.to_frame(name=value_column).to_parquet(out_path, index=False)

    _write(df_color, "paint_color", lambda s: s.str.lower(), "vehicle_color")
    _write(df_state, "state", lambda s: s.str.upper(), "vehicle_state")
    _write(
        df_transmission,
        "transmission",
        lambda s: s.str.lower(),
        "vehicle_transmission",
    )


def train_model_feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = find_age(df)
    df = filter_price(df)
    df_color = extract_colors(df)
    df_state = extract_states(df)
    df_transmission = extract_transmissions(df)
    _write_model_attribute_files(df_color, df_state, df_transmission)
    _write_manufacturer_model_lookup(df)
    df = _standardize_categoricals(df)
    return df

def model_feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = find_age(df)
    df = _standardize_categoricals(df)
    return df

def fit_transform(
    df: pd.DataFrame,
    drop_first: bool = True,
    expected_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    df = _standardize_categoricals(df)
    feature_cols = ["age", "odometer"] + CATEGORICAL_COLUMNS
    feature_frame = pd.get_dummies(df[feature_cols], drop_first=drop_first)
    if expected_columns is not None:
        feature_frame = feature_frame.reindex(columns=expected_columns, fill_value=0)
    return feature_frame
