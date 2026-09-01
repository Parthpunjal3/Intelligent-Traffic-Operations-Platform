#!/usr/bin/env python3
"""
Build a clean, regularly-sampled time series of vehicle counts per
camera from raw ingestion records, ready for model training.

Usage:
    python build_timeseries.py --db-url postgresql://... --camera-id <id> --out data/sample/cam_ts.csv
"""
import argparse
import pandas as pd
from sqlalchemy import create_engine, text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db-url", required=True)
    parser.add_argument("--camera-id", required=True)
    parser.add_argument("--interval-min", type=int, default=5)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    engine = create_engine(args.db_url)
    query = text(
        """
        SELECT timestamp, SUM(count) as count
        FROM vehicle_counts
        WHERE camera_id = :camera_id
        GROUP BY timestamp
        ORDER BY timestamp
        """
    )
    df = pd.read_sql(query, engine, params={"camera_id": args.camera_id}, parse_dates=["timestamp"])
    df = df.set_index("timestamp").resample(f"{args.interval_min}min").sum().interpolate()
    df.to_csv(args.out)
    print(f"Wrote {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
