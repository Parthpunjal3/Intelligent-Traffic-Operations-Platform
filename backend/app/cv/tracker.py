"""
Lightweight centroid tracker (Euclidean-distance based) used to assign
persistent IDs to vehicles across frames -- required for accurate
counting (avoiding double-counting) and speed estimation.

For production, swap this for ByteTrack/DeepSORT (both work well with
ultralytics' built-in `model.track()`), but this dependency-free version
is enough to demonstrate the pipeline end-to-end.
"""
from collections import OrderedDict
from typing import Dict, List, Tuple
import numpy as np


class CentroidTracker:
    def __init__(self, max_disappeared: int = 15, max_distance: float = 80.0):
        self.next_object_id = 0
        self.objects: "OrderedDict[int, Tuple[float, float]]" = OrderedDict()
        self.disappeared: "OrderedDict[int, int]" = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def _register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def _deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, bboxes: List[Tuple[float, float, float, float]]) -> Dict[int, Tuple[float, float]]:
        if len(bboxes) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            return self.objects

        input_centroids = np.array(
            [((x1 + x2) / 2.0, (y1 + y2) / 2.0) for (x1, y1, x2, y2) in bboxes]
        )

        if len(self.objects) == 0:
            for c in input_centroids:
                self._register(tuple(c))
        else:
            object_ids = list(self.objects.keys())
            object_centroids = np.array(list(self.objects.values()))

            D = np.linalg.norm(object_centroids[:, None] - input_centroids[None, :], axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows, used_cols = set(), set()
            for row, col in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > self.max_distance:
                    continue
                object_id = object_ids[row]
                self.objects[object_id] = tuple(input_centroids[col])
                self.disappeared[object_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(D.shape[0])) - used_rows
            unused_cols = set(range(D.shape[1])) - used_cols

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)

            for col in unused_cols:
                self._register(tuple(input_centroids[col]))

        return self.objects
