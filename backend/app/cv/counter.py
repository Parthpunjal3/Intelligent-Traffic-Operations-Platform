"""
Line-crossing vehicle counter. Counts a tracked object once when its
centroid crosses a virtual counting line (defined as a y-coordinate,
or generalize to an arbitrary line for angled roads).
"""
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple


@dataclass
class LineCounter:
    line_y: float
    counted_ids: Set[int] = field(default_factory=set)
    last_positions: Dict[int, Tuple[float, float]] = field(default_factory=dict)
    total_count: int = 0

    def update(self, tracked_objects: Dict[int, Tuple[float, float]]) -> int:
        """Call once per frame with the current tracker output.
        Returns the number of NEW crossings this frame."""
        new_crossings = 0
        for object_id, centroid in tracked_objects.items():
            prev = self.last_positions.get(object_id)
            self.last_positions[object_id] = centroid
            if object_id in self.counted_ids or prev is None:
                continue
            prev_y, curr_y = prev[1], centroid[1]
            if prev_y < self.line_y <= curr_y or prev_y > self.line_y >= curr_y:
                self.counted_ids.add(object_id)
                self.total_count += 1
                new_crossings += 1
        return new_crossings

    def reset_window(self):
        """Call at the end of an aggregation window (e.g. every 60s)."""
        self.counted_ids.clear()
        self.total_count = 0
