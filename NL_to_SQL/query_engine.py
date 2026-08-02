"""
Layer 2: Structured filter dict -> actual matching rows, with optional
feature-normalized nearest-neighbor ranking for "similar to X" questions.
"""

import duckdb
import pandas as pd
from .config import DATA_PATH, PRICE_COL, YEAR_COL, BODY_TYPE_COL, MODEL_COL, SIMILARITY_COLS

df = pd.read_csv(DATA_PATH)
# Testing purposes for clean data
df = df[df[PRICE_COL] >= 2000]

con = duckdb.connect()
con.register("vehicles", df)


def run_query(filters: dict) -> pd.DataFrame:
    clauses = []
    if filters.get("price_min") is not None:
        clauses.append(f"{PRICE_COL} >= {filters['price_min']}")
    if filters.get("price_max") is not None:
        clauses.append(f"{PRICE_COL} <= {filters['price_max']}")
    if filters.get("year_min") is not None:
        clauses.append(f"{YEAR_COL} >= {filters['year_min']}")
    if filters.get("year_max") is not None:
        clauses.append(f"{YEAR_COL} <= {filters['year_max']}")
    if filters.get("body_type"):
        clauses.append(f"LOWER({BODY_TYPE_COL}) = '{filters['body_type'].lower()}'")

    where = " AND ".join(clauses) if clauses else "TRUE"
    results = con.execute(f"SELECT * FROM vehicles WHERE {where}").df()

    if filters.get("reference_model") and not results.empty:
        matches = df[df[MODEL_COL].str.contains(filters["reference_model"], case=False, na=False)]
        if not matches.empty:
            ref = matches.iloc[0]
            # Normalize each similarity column to 0-1 before computing distance,
            # so a column like price (thousands) doesn't drown out one like mpg (tens).
            norm = results.copy()
            for col in SIMILARITY_COLS:
                span = (df[col].max() - df[col].min()) or 1
                norm[col] = (results[col] - df[col].min()) / span
            ref_norm = {
                c: (ref[c] - df[c].min()) / ((df[c].max() - df[c].min()) or 1)
                for c in SIMILARITY_COLS
            }
            results["similarity_dist"] = sum(
                (norm[c] - ref_norm[c]) ** 2 for c in SIMILARITY_COLS
            ) ** 0.5
            results = results.sort_values("similarity_dist")

    if filters.get("limit"):
        results = results.head(int(filters["limit"]))
    return results