#!/usr/bin/env python3
"""
Standalone script: run vehicle detection on a video file or RTSP stream
and preview annotated output. Useful for testing camera placement /
model accuracy before wiring a camera into the live backend pipeline.

Usage:
    python run_detection.py --source path/to/video.mp4 --show
    python run_detection.py --source rtsp://camera-ip/stream
"""
import argparse
import cv2

from ultralytics import YOLO

VEHICLE_CLASSES = {"car", "truck", "bus", "motorcycle", "bicycle"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Video file path or RTSP/HTTP stream URL")
    parser.add_argument("--model", default="yolov8n.pt")
    parser.add_argument("--conf", type=float, default=0.4)
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    model = YOLO(args.model)
    cap = cv2.VideoCapture(args.source)

    if not cap.isOpened():
        raise SystemExit(f"Could not open source: {args.source}")

    frame_count = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_count += 1

        results = model.predict(frame, conf=args.conf, verbose=False)[0]
        names = results.names
        vehicle_count = 0
        for box in results.boxes:
            cls_name = names.get(int(box.cls[0]), "")
            if cls_name not in VEHICLE_CLASSES:
                continue
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, cls_name, (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.putText(frame, f"Vehicles: {vehicle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if args.show:
            cv2.imshow("detection", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Processed {frame_count} frames.")


if __name__ == "__main__":
    main()
