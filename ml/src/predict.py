# Take inputs from streamlit and run the model to preict the price
import joblib
import numpy as np
import pandas as pd
from ml.src.preprocessing import fit_transform, model_feature_engineer

def predict(prediction_df: pd.DataFrame, model_path: str = "ml/models/xgb_model_all.joblib") -> np.ndarray:

    df = model_feature_engineer(prediction_df)
    model = joblib.load(model_path)

    # Build the feature matrix using the same encoding as training
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None:
        feature_names = model.get_booster().feature_names or []
    expected_columns = list(feature_names) if feature_names else None
    feature_frame = fit_transform(
        df,
        drop_first=True,
        expected_columns=expected_columns,
    )
  
    predictions = model.predict(feature_frame)
    return np.exp(predictions) # reverse log transformation
