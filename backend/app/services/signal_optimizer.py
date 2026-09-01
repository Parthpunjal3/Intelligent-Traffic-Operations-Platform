"""
Traffic-signal timing recommendation engine (Webster's formula baseline).
Copied into the backend package so it ships inside the Docker image
without needing an external path.
"""
from typing import List

LOST_TIME_PER_PHASE = 4.0
SATURATION_FLOW = 1800.0
MIN_GREEN = 10.0
MAX_CYCLE = 150.0
MIN_CYCLE = 40.0


def _webster_optimal_cycle(total_lost_time: float, sum_y: float) -> float:
    sum_y = min(sum_y, 0.95)
    return (1.5 * total_lost_time + 5) / max(0.05, (1 - sum_y))


def recommend_signal_timing(approach_volumes: List[float], num_lanes_per_approach: int = 1) -> dict:
    if not approach_volumes:
        approach_volumes = [10.0, 10.0]

    n_phases = len(approach_volumes)
    total_lost_time = LOST_TIME_PER_PHASE * n_phases

    saturation = SATURATION_FLOW * num_lanes_per_approach
    y_ratios = [max(0.01, v) / saturation for v in approach_volumes]
    sum_y = sum(y_ratios)

    cycle = _webster_optimal_cycle(total_lost_time, sum_y)
    cycle = max(MIN_CYCLE, min(MAX_CYCLE, cycle))

    effective_green_total = cycle - total_lost_time
    phases = []
    for idx, y in enumerate(y_ratios):
        share = y / sum_y if sum_y > 0 else 1 / n_phases
        green = max(MIN_GREEN, round(effective_green_total * share))
        phases.append({"name": f"phase_{idx + 1}", "green": green, "volume": approach_volumes[idx]})

    return {
        "cycle": round(cycle),
        "phases": phases,
        "lost_time": total_lost_time,
        "sum_critical_ratio": round(sum_y, 3),
    }