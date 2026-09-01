"""
Reference LSTM forecasting model definition (PyTorch) for traffic
volume prediction, as a higher-accuracy alternative to the
statsmodels baseline used in `backend/app/ml/forecasting.py`.

Train with `ml/training/train_forecaster.py`, then export weights to
`ml/models/` and point the backend's TrafficForecaster subclass at them.
"""
import torch
import torch.nn as nn


class TrafficLSTM(nn.Module):
    def __init__(self, input_size: int = 1, hidden_size: int = 64, num_layers: int = 2, horizon: int = 6):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, horizon)

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)
        last_hidden = out[:, -1, :]
        return self.fc(last_hidden)  # (batch, horizon)


def make_sequences(series, seq_len: int, horizon: int):
    """Sliding-window dataset builder: returns (X, y) numpy arrays."""
    import numpy as np
    X, y = [], []
    for i in range(len(series) - seq_len - horizon + 1):
        X.append(series[i:i + seq_len])
        y.append(series[i + seq_len:i + seq_len + horizon])
    return np.array(X), np.array(y)
