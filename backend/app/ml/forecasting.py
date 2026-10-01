"""Predictive analytics layer: a generic XGBoost model for classification
(e.g. churn, incident-risk) or regression (e.g. demand forecasting), plus
a lightweight time-series forecaster for the /forecast endpoint's charting
use case (confidence-banded future periods).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error, roc_auc_score
from sklearn.model_selection import train_test_split

from app.config import get_settings

settings = get_settings()
os.makedirs(settings.model_registry_dir, exist_ok=True)


@dataclass
class TrainResult:
    model_path: str
    metrics: dict[str, float]
    feature_names: list[str]


def train_tabular_model(df: pd.DataFrame, target: str, model_name: str) -> TrainResult:
    """Train an XGBoost model on a tabular dataset. Automatically detects
    classification (binary target) vs. regression."""
    y = df[target]
    X = df.drop(columns=[target]).select_dtypes(include=[np.number])
    feature_names = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    is_classification = y.nunique() <= 2
    if is_classification:
        model = xgb.XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, eval_metric="auc",
        )
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_test)[:, 1]
        metrics = {"auc": float(roc_auc_score(y_test, preds))}
    else:
        model = xgb.XGBRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = {"rmse": float(mean_squared_error(y_test, preds) ** 0.5)}

    model_path = os.path.join(settings.model_registry_dir, f"{model_name}.json")
    model.save_model(model_path)
    with open(model_path + ".meta.json", "w") as f:
        json.dump({"feature_names": feature_names, "is_classification": is_classification}, f)

    return TrainResult(model_path=model_path, metrics=metrics, feature_names=feature_names)


def load_model(model_name: str):
    model_path = os.path.join(settings.model_registry_dir, f"{model_name}.json")
    meta_path = model_path + ".meta.json"
    with open(meta_path) as f:
        meta = json.load(f)
    model_cls = xgb.XGBClassifier if meta["is_classification"] else xgb.XGBRegressor
    model = model_cls()
    model.load_model(model_path)
    return model, meta


def predict(model_name: str, X: pd.DataFrame) -> np.ndarray:
    model, meta = load_model(model_name)
    X = X[meta["feature_names"]]
    if meta["is_classification"]:
        return model.predict_proba(X)[:, 1]
    return model.predict(X)


def time_series_forecast(history: pd.Series, horizon: int = 30) -> list[dict]:
    """Lightweight forecaster for operational time series (incident counts,
    churned-customer counts, etc.) using Holt's linear trend method with a
    bootstrap-based confidence band. Kept dependency-free (no statsmodels)
    for portability; swap for Prophet/ARIMA in a production iteration."""
    values = history.values.astype(float)
    n = len(values)
    if n < 4:
        raise ValueError("Need at least 4 historical periods to forecast")

    alpha, beta = 0.5, 0.3
    level, trend = values[0], values[1] - values[0]
    for v in values[1:]:
        last_level = level
        level = alpha * v + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend

    residuals = []
    l2, t2 = values[0], values[1] - values[0]
    for v in values[1:]:
        pred = l2 + t2
        residuals.append(v - pred)
        last_level = l2
        l2 = alpha * v + (1 - alpha) * (l2 + t2)
        t2 = beta * (l2 - last_level) + (1 - beta) * t2
    resid_std = float(np.std(residuals)) if residuals else float(np.std(values)) * 0.1

    out = []
    for h in range(1, horizon + 1):
        point = level + h * trend
        band = 1.96 * resid_std * (h ** 0.5)
        out.append({
            "step": h,
            "predicted": round(max(point, 0), 2),
            "lower": round(max(point - band, 0), 2),
            "upper": round(max(point + band, 0), 2),
        })
    return out
