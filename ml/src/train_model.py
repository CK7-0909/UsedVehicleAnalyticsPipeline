from pathlib import Path
from typing import Tuple

import joblib as jb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from ml.src.preprocessing import fit_transform


def train_model(
    df: pd.DataFrame,
    model_output: str = "ml/models/xgb_model_all.joblib",
    eval_output: str = "models/evaluation_all.parquet",
) -> Tuple[np.ndarray, np.ndarray]:
    df = df.copy()
    X = fit_transform(df, drop_first=True)
    y = np.log(df["price"])  # log transformation to reduce the impact of outliers

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )
    model.fit(X_train, y_train)

    y_pred_log = model.predict(X_test)
    y_true = np.exp(y_test)
    y_pred = np.exp(y_pred_log)

    # Persist the trained model
    model_path = Path(model_output)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    jb.dump(model, model_path)

    # Save predictions to reduce rerunning model training
    abs_error = np.abs(y_true - y_pred)
    pct_error = np.where(y_true != 0, abs_error / y_true * 100, np.nan)
    eval_df = pd.DataFrame(
        {
            "actual_price": y_true.values,
            "predicted_price": y_pred,
            "abs_error": abs_error,
            "pct_error": pct_error,
        }
    )
    eval_path = Path(eval_output)
    eval_path.parent.mkdir(parents=True, exist_ok=True)
    eval_df.to_parquet(eval_path, index=False)

    return y_pred, y_true
