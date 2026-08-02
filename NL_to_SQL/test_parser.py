"""
Run with: python -m rag_pipeline.test_parser   (from the project root)

Each case is (question, check_fn). check_fn returns True/False given the
parsed filter dict. Read the raw output once before trusting these checks --
confirm the model actually returns the key names/formats assumed below.
"""

from .filter_parser import parse_filters

CASES = [
    (
        "cars under 26k, sedan, similar to an Accord",
        lambda f: f["price_max"] == 26000
        and f["body_type"] == "sedan"
        and f["reference_model"]
        and "accord" in f["reference_model"].lower(),
    ),
    (
        "show me suvs between 20000 and 35000",
        lambda f: f["price_min"] == 20000
        and f["price_max"] == 35000
        and f["body_type"] == "suv",
    ),
    (
        "what trucks do you have under 40k",
        lambda f: f["price_max"] == 40000 and f["body_type"] == "truck",
    ),
    (
        "give me all sedans like a Camry",
        lambda f: f["body_type"] == "sedan"
        and f["reference_model"]
        and "camry" in f["reference_model"].lower()
        and f["limit"] is None,
    ),
    (
        "anything around 15 grand",
        # Loose on purpose -- "around" is ambiguous. Just checking it's in the
        # ballpark and didn't do something wild like read "15" as $15.
        lambda f: f["price_max"] is not None and 13000 <= f["price_max"] <= 17000,
    ),
    (
        "car under 26k and older than 2021",
        # "older than 2021" should be STRICT -- year_max=2020, not 2021.
        # This is the case most likely to silently flip on you; check it explicitly.
        lambda f: f["price_max"] == 26000 and f["year_max"] == 2020,
    ),
    (
        "suvs from 2020 or newer",
        # "or newer" is INCLUSIVE -- year_min=2020, not 2021.
        lambda f: f["year_min"] == 2020 and f["body_type"] == "suv",
    ),
    (
        "trucks newer than 2019 under 35k",
        # "newer than" is STRICT -- year_min=2020, not 2019.
        lambda f: f["year_min"] == 2020 and f["price_max"] == 35000,
    ),
]


def run_tests():
    passed = 0
    for question, check in CASES:
        filters = parse_filters(question)
        ok = check(filters)
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {question}\n    -> {filters}\n")
        passed += ok
    print(f"{passed}/{len(CASES)} passed")


if __name__ == "__main__":
    run_tests()