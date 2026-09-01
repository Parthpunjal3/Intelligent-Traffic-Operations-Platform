#!/usr/bin/env python3
"""
Evaluate a trained forecaster (or the statsmodels baseline) against a
held-out time series using MAE / RMSE / MAPE.
"""
import argparse
import numpy as np
import pandas as pd


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true, y_pred):
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mape(y_true, y_pred):
    eps = 1e-6
    return float(np.mean(np.abs((y_true - y_pred) / (y_true + eps))) * 100)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV with columns: y_true, y_pred")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    y_true, y_pred = df["y_true"].values, df["y_pred"].values

    print(f"MAE:  {mae(y_true, y_pred):.3f}")
    print(f"RMSE: {rmse(y_true, y_pred):.3f}")
    print(f"MAPE: {mape(y_true, y_pred):.2f}%")


if __name__ == "__main__":
    main()
