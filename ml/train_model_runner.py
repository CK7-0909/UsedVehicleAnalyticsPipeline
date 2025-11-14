from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from ml.data.snowflake.sf_connection import query_to_df
from ml.src.evaluate import evaluate_model
from ml.src.preprocessing import train_model_feature_engineer
from ml.src.train_model import train_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train the vehicle price model using Snowflake data."
    )
    parser.add_argument(
        "--save-model-path",
        default="ml/models/xgb_model_all.joblib",
        help="Where the trained model will be stored (default: %(default)s).",
    )
    parser.add_argument(
        "--eval-output",
        default="models/evaluation_all.parquet",
        help="Path for detailed evaluation output (default: %(default)s).",
    )
    parser.add_argument(
        "--print-metrics",
        action="store_true",
        help="Print summary metrics to stdout once training completes.",
    )
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()

    raw_df = query_to_df()
    if raw_df.empty:
        raise RuntimeError("Snowflake query returned no rows; aborting training.")

    feature_df = train_model_feature_engineer(raw_df)
    y_pred, y_true = train_model(
        feature_df,
        model_output=args.save_model_path,
        eval_output=args.eval_output,
    )

    metrics, _ = evaluate_model(
        y_true,
        y_pred,
        save_path=None,
        return_details=False,
    )

    if args.print_metrics:
        print(json.dumps(metrics.to_dict(), indent=2))

    model_path = Path(args.save_model_path)
    if not model_path.exists():
        raise FileNotFoundError(
            f"Expected trained model at {model_path}, but the file was not created."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
