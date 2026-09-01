"""
Traffic-signal timing recommendation engine.

Implements a Webster's-formula-based cycle/green-split optimizer, which
is the standard traffic-engineering baseline for minimizing average
vehicle delay at a signalized intersection given per-approach demand
(flow) and saturation flow rates.

recommend_signal_timing() takes a list of approach volumes (vehicles
observed per minute, one entry per approach/phase group) and returns a
phase plan: total cycle length + green time per phase.
"""
from typing import List


LOST_TIME_PER_PHASE = 4.0          # seconds lost to clearance/start-up per phase
SATURATION_FLOW = 1800.0           # vehicles/hour/lane -- typical urban default
MIN_GREEN = 10.0                   # seconds
MAX_CYCLE = 150.0                  # seconds
MIN_CYCLE = 40.0                   # seconds


def _webster_optimal_cycle(total_lost_time: float, sum_y: float) -> float:
    """Webster's formula: Co = (1.5*L + 5) / (1 - Y)"""
    sum_y = min(sum_y, 0.95)  # cap to avoid division blow-up / oversaturation
    return (1.5 * total_lost_time + 5) / max(0.05, (1 - sum_y))


def recommend_signal_timing(approach_volumes: List[float], num_lanes_per_approach: int = 1) -> dict:
    """
    approach_volumes: e.g. [northbound_vph, southbound_vph, eastbound_vph, westbound_vph]
                       (or already grouped per phase, e.g. [NS_volume, EW_volume])
    Returns a phase plan dict, e.g.:
        {"cycle": 65, "phases": [{"name": "phase_1", "green": 35}, {"name": "phase_2", "green": 25}], "lost_time": 8}
    """
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
