"""
Run with: python -m rag_pipeline.test_integration   (from the project root)

Runs the REAL parser (costs a few cents) against the REAL CSV -- no
assertions here, unlike the other two test files. You don't know the exact
right answer on 80K real rows, so this is for eyeballing: does each result
set actually look correct for what was asked?

Sanity-check per question:
  - Do the filters look right for what was typed?
  - Does every row in the results actually satisfy those filters?
  - For "similar to X" questions, is the top result plausibly similar
    (comparable price/year/odometer), not just first-in-file-order?
"""

from .filter_parser import parse_filters
from .query_engine import run_query

QUESTIONS = [
    "cars under 26k, sedan, similar to an Accord",
    "show me suvs between 20000 and 35000",
    "car under 26k and older than 2021",
    "trucks newer than 2019 under 35k",
    "suvs from 2020 or newer",
]

for q in QUESTIONS:
    filters = parse_filters(q)
    results = run_query(filters)
    print(f"Q: {q}")
    print(f"  filters: {filters}")
    print(f"  {len(results)} matches, top 5:")
    cols = [c for c in ("model", "price", "year", "type", "odometer") if c in results.columns]
    print(results.head(5)[cols].to_string(index=False))
    print()