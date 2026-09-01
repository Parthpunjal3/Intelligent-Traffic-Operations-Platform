#!/usr/bin/env python3
"""
Train the reference LSTM traffic forecaster on a per-camera time series
CSV (produced by ml/preprocessing/build_timeseries.py).

Usage:
    python train_forecaster.py --csv data/sample/cam_ts.csv --epochs 30 --out ml/models/lstm_cam1.pt
"""
import argparse
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from forecasting.lstm_model import TrafficLSTM, make_sequences


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--seq-len", type=int, default=24)
    parser.add_argument("--horizon", type=int, default=6)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    series = df["count"].values.astype(np.float32)
    series = (series - series.mean()) / (series.std() + 1e-6)

    X, y = make_sequences(series, args.seq_len, args.horizon)
    X = torch.tensor(X).unsqueeze(-1)
    y = torch.tensor(y)

    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = TrafficLSTM(horizon=args.horizon)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    loss_fn = nn.MSELoss()

    for epoch in range(args.epochs):
        total_loss = 0.0
        for xb, yb in loader:
            optimizer.zero_grad()
            pred = model(xb)
            loss = loss_fn(pred, yb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"epoch {epoch + 1}/{args.epochs} loss={total_loss / len(loader):.4f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    torch.save(model.state_dict(), args.out)
    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()
