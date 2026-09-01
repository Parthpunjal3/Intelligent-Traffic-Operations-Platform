"""
Short-horizon (15-30 min) traffic volume forecasting.

Uses a Holt-Winters exponential smoothing model (statsmodels) per
camera as a strong, cheap baseline that captures trend + daily
seasonality from historical vehicle-count time series. Swap in an
LSTM/Temporal-Fusion-Transformer (see ml/training/) for higher
accuracy once you have enough historical data (weeks+).
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd

from app.core.config import settings


@dataclass
class ForecastPoint:
    target_timestamp: datetime
    predicted_count: float
    confidence: float


class TrafficForecaster:
    def __init__(self, interval_min: int | None = None, horizon_min: int | None = None):
        self.interval_min = interval_min or settings.FORECAST_INTERVAL_MIN
        self.horizon_min = horizon_min or settings.FORECAST_HORIZON_MIN

    def forecast(self, history: List[Tuple[datetime, float]]) -> List[ForecastPoint]:
        """
        history: list of (timestamp, count) sorted ascending, ideally at a
        regular cadence (resample first if raw/irregular).
        """
        n_steps = max(1, self.horizon_min // self.interval_min)

        if len(history) < 6:
            # Not enough data yet -- naive persistence forecast.
            last_val = history[-1][1] if history else 0.0
            last_ts = history[-1][0] if history else datetime.utcnow()
            return [
                ForecastPoint(
                    target_timestamp=last_ts + timedelta(minutes=self.interval_min * (i + 1)),
                    predicted_count=last_val,
                    confidence=0.3,
                )
                for i in range(n_steps)
            ]

        ts = pd.Series(
            [v for _, v in history],
            index=pd.DatetimeIndex([t for t, _ in history]),
        )
        ts = ts.asfreq(f"{self.interval_min}min").interpolate().fillna(method="bfill")

        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing

            seasonal_periods = min(len(ts) // 2, max(2, (24 * 60) // self.interval_min))
            use_seasonal = len(ts) >= seasonal_periods * 2

            model = ExponentialSmoothing(
                ts,
                trend="add",
                seasonal="add" if use_seasonal else None,
                seasonal_periods=seasonal_periods if use_seasonal else None,
                initialization_method="estimated",
            ).fit(optimized=True)

            forecast_vals = model.forecast(n_steps)
            resid_std = float(np.std(model.resid)) if len(model.resid) > 0 else 1.0
            confidence = max(0.4, 1.0 - min(0.5, resid_std / (ts.mean() + 1e-6)))
        except Exception:
            # Fallback: simple linear trend on last 12 points.
            recent = ts.values[-12:]
            x = np.arange(len(recent))
            coeffs = np.polyfit(x, recent, 1)
            forecast_vals = [
                max(0.0, np.polyval(coeffs, len(recent) + i)) for i in range(n_steps)
            ]
            confidence = 0.45

        last_ts = ts.index[-1]
        points = []
        for i in range(n_steps):
            val = float(forecast_vals[i]) if not isinstance(forecast_vals, list) else forecast_vals[i]
            points.append(
                ForecastPoint(
                    target_timestamp=last_ts + timedelta(minutes=self.interval_min * (i + 1)),
                    predicted_count=max(0.0, val),
                    confidence=round(float(confidence), 2),
                )
            )
        return points


def classify_congestion(count_per_min: float, moderate_th: int, heavy_th: int) -> str:
    if count_per_min >= heavy_th:
        return "heavy" if count_per_min < heavy_th * 1.6 else "gridlock"
    if count_per_min >= moderate_th:
        return "moderate"
    return "free_flow"
