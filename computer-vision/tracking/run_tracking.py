#!/usr/bin/env python3
"""
Standalone script demonstrating detection + centroid tracking together.
Reuses the shared detector/tracker implementations from the backend app
so behavior stays identical between offline testing and production.
"""
import argparse
import sys
import os
import cv2

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))
from app.cv.detector import VehicleDetector
from app.cv.tracker import CentroidTracker


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    detector = VehicleDetector()
    tracker = CentroidTracker()

    cap = cv2.VideoCapture(args.source)
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        detections = detector.detect(frame)
        bboxes = [d.bbox for d in detections]
        tracked = tracker.update(bboxes)

        for object_id, (cx, cy) in tracked.items():
            cv2.circle(frame, (int(cx), int(cy)), 4, (255, 0, 0), -1)
            cv2.putText(frame, f"ID {object_id}", (int(cx) + 5, int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        if args.show:
            cv2.imshow("tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
