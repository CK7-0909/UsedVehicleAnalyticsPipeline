from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

NumberArray = Union[Iterable[float], np.ndarray, pd.Series]


@dataclass(frozen=True)
class RegressionMetrics:
    """Simple container for the key regression metrics we care about."""

    mae: float
    rmse: float
    r2: float

    def to_dict(self) -> dict:
        return asdict(self)


def _to_numpy(values: NumberArray) -> np.ndarray:
    """Return a float numpy array regardless of the original container."""
    return np.asarray(values, dtype=float)


def evaluate_model(
    y_true: NumberArray,
    y_pred: NumberArray,
    save_path: Optional[str] = "ml/artifacts/evaluation_all.parquet",
    return_details: bool = False,
) -> Tuple[RegressionMetrics, Optional[pd.DataFrame]]:
    """
    Compute regression metrics and optionally persist row-level errors.

    Args:
        y_true: Ground-truth price values.
        y_pred: Predicted price values (already inverse-transformed).
        save_path: Where to write the evaluation parquet; pass None to skip saving.
        return_details: When True also return the per-record evaluation DataFrame.
    """

    y_true_arr = _to_numpy(y_true)
    y_pred_arr = _to_numpy(y_pred)

    metrics = RegressionMetrics(
        mae=float(mean_absolute_error(y_true_arr, y_pred_arr)),
        rmse=float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr))),
        r2=float(r2_score(y_true_arr, y_pred_arr)),
    )

    abs_error = np.abs(y_true_arr - y_pred_arr)
    pct_error = np.where(y_true_arr != 0, abs_error / y_true_arr * 100, np.nan)
    eval_df = pd.DataFrame(
        {
            "actual_price": y_true_arr,
            "predicted_price": y_pred_arr,
            "abs_error": abs_error,
            "pct_error": pct_error,
        }
    )

    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        eval_df.to_parquet(path, index=False)

    if return_details:
        return metrics, eval_df

    return metrics, None
