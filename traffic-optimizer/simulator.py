"""
Very small discrete-event-ish simulator to sanity-check signal plans
before applying them: given arrival rates and a phase plan, estimates
average vehicle delay per approach using Webster's delay formula.
Useful for A/B testing candidate plans offline (see traffic-optimizer/policies/).
"""
from typing import List, Dict


def estimate_delay(phase_plan: dict, approach_volumes: List[float], saturation_flow: float = 1800.0) -> Dict:
    cycle = phase_plan["cycle"]
    results = []
    for phase in phase_plan["phases"]:
        g = phase["green"]
        v = phase["volume"]
        capacity = saturation_flow * (g / cycle)
        x = min(0.98, v / capacity) if capacity > 0 else 0.98  # degree of saturation

        # Webster's average delay per vehicle (simplified, uniform + random delay terms)
        uniform_delay = (cycle * (1 - g / cycle) ** 2) / (2 * (1 - x * (g / cycle))) if x < 1 else 60
        random_delay = (x ** 2) / (2 * v * (1 - x)) if v > 0 and x < 1 else 30
        avg_delay = uniform_delay + random_delay

        results.append({
            "phase": phase["name"],
            "degree_of_saturation": round(x, 2),
            "avg_delay_sec": round(avg_delay, 1),
        })
    return {"cycle": cycle, "per_phase": results}
