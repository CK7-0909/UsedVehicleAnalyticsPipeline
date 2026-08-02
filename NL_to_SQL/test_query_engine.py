"""
Run with: python -m rag_pipeline.test_query_engine   (from the project root)

Tests query_engine.run_query() against a tiny synthetic dataset where the
correct answer is known by construction. Column names are pulled from
config.py, so this test builds its synthetic dataframe using YOUR actual
schema (PRICE_COL, YEAR_COL, BODY_TYPE_COL, MODEL_COL, SIMILARITY_COLS)
rather than hardcoded placeholder names -- if you change config.py later,
this test stays in sync automatically instead of silently testing the wrong
columns. Covers price filtering, year filtering (year_min/year_max), body
type filtering, similarity ranking, and combinations of these.

No LLM calls here, no API cost, fully deterministic.
"""

import duckdb
import pandas as pd
from rag_pipeline import query_engine
from rag_pipeline.config import PRICE_COL, YEAR_COL, BODY_TYPE_COL, MODEL_COL, SIMILARITY_COLS


def make_test_df() -> pd.DataFrame:
    # (model, price, body_type, odometer, year) -- distinct values per column
    # so the test can actually tell them apart, rather than one number reused
    # across every extra similarity column.
    raw_rows = [
        ("Accord", 24000, "sedan", 20000, 2019),
        ("Camry",  23000, "sedan", 18000, 2020),
        ("Civic",  21000, "sedan", 12000, 2021),
        ("CR-V",   27000, "suv",   15000, 2020),
        ("F-150",  38000, "truck", 25000, 2018),
    ]
    rows = []
    for model, price, body_type, odometer, year in raw_rows:
        rows.append({
            MODEL_COL: model,
            PRICE_COL: price,
            BODY_TYPE_COL: body_type,
            "odometer": odometer,
            YEAR_COL: year,
        })
    return pd.DataFrame(rows)


def use_test_data():
    """Swap the module's real CSV-backed df/con for the synthetic test data."""
    test_df = make_test_df()
    query_engine.df = test_df
    query_engine.con = duckdb.connect()
    query_engine.con.register("vehicles", test_df)


CASES = [
    (
        "price_max only",
        {"price_min": None, "price_max": 24000, "body_type": None, "reference_model": None, "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry", "Civic"},
    ),
    (
        "body_type only",
        {"price_min": None, "price_max": None, "body_type": "sedan", "reference_model": None, "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry", "Civic"},
    ),
    (
        "combined price + body_type",
        {"price_min": 22000, "price_max": 25000, "body_type": "sedan", "reference_model": None, "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry"},
    ),
    (
        "year_max only (older than 2021 -> year_max=2020)",
        {"price_min": None, "price_max": None, "year_min": None, "year_max": 2020, "body_type": None, "reference_model": None, "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry", "CR-V", "F-150"},
    ),
    (
        "combined price + year_max",
        {"price_min": None, "price_max": 26000, "year_min": None, "year_max": 2020, "body_type": None, "reference_model": None, "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry"},
    ),
    (
        "similar-to ranking: Accord should rank above CR-V/F-150",
        {"price_min": None, "price_max": None, "body_type": None, "reference_model": "Accord", "limit": None},
        lambda r: list(r[MODEL_COL])[0] == "Accord",
    ),
    (
        "no matches",
        {"price_min": 100000, "price_max": None, "body_type": None, "reference_model": None, "limit": None},
        lambda r: len(r) == 0,
    ),
    (
        "reference_model not found in data -- should not crash, just skip ranking",
        {"price_min": None, "price_max": None, "body_type": "sedan", "reference_model": "Tesla Model S", "limit": None},
        lambda r: set(r[MODEL_COL]) == {"Accord", "Camry", "Civic"},
    ),
    (
        "limit truncates results",
        {"price_min": None, "price_max": None, "body_type": "sedan", "reference_model": None, "limit": 2},
        lambda r: len(r) == 2,
    ),
]


def run_tests():
    use_test_data()
    passed = 0
    for name, filters, check in CASES:
        result = query_engine.run_query(filters)
        ok = check(result)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}\n    filters={filters}\n    -> models={list(result[MODEL_COL])}\n")
        passed += ok
    print(f"{passed}/{len(CASES)} passed")


if __name__ == "__main__":
    run_tests()