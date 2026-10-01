"""CLI entry point for training a tabular XGBoost model from a CSV dataset.

Usage:
    python -m app.ml.train --dataset data/churn_sample.csv --target churn --name churn_xgb
"""

import argparse

import pandas as pd

from app.ml.forecasting import train_tabular_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to CSV file")
    parser.add_argument("--target", required=True, help="Target column name")
    parser.add_argument("--name", default="model", help="Registry name to save under")
    args = parser.parse_args()

    df = pd.read_csv(args.dataset)
    result = train_tabular_model(df, target=args.target, model_name=args.name)

    print(f"Model saved to: {result.model_path}")
    print(f"Metrics: {result.metrics}")
    print(f"Features used: {result.feature_names}")


if __name__ == "__main__":
    main()
