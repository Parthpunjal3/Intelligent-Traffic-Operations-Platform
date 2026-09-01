# Counting

Line-crossing vehicle counting logic lives in `backend/app/cv/counter.py`
(shared module, imported by both the live backend pipeline and any
offline batch-processing scripts here). See `LineCounter` for usage.

To batch-count vehicles in a saved video file:

```bash
python ../tracking/run_tracking.py --source path/to/video.mp4 --show
```

then wire a `LineCounter` in after the tracker update call, using a
`line_y` calibrated to the video's counting line.
