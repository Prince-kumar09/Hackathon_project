# Hackathon_project
# Drowsy Driver Alert System

A real-time AI system that watches the driver's face, detects **eye closing, blinking and
yawning**, and raises a **buzzer + voice alert** when the driver looks sleepy.

**Goal:** detect driver drowsiness in time and reduce the risk of road accidents.

Technologies: Python, OpenCV, MediaPipe (or dlib), NumPy, Jupyter.

## How it works

```
Input (video/camera frame)
   -> face_detection.py   find face + eye/mouth landmarks
   -> eye_detection.py    EAR (eye aspect ratio), eye-closed time, blink count
   -> yawn_detection.py   MAR (mouth aspect ratio), yawn count
   -> drowsiness.py       decision engine -> driver state
   -> alert_system.py     beep + voice message + log file
```

| Signal | How it is measured | Alert rule (default) |
|---|---|---|
| Eyes closing | EAR below a per-driver threshold (auto-calibrated) | closed for >= 1.5 s -> `DROWSY` |
| Blinking | short closure (0.05 - 0.5 s) | >= 30 blinks/min -> `FATIGUE_BLINK` |
| Yawning | MAR > 0.6 for >= 1.2 s | >= 3 yawns in 60 s -> `FATIGUE_YAWN` |
| Driver not visible | no face detected | >= 3 s -> `DRIVER_NOT_VISIBLE` |

All thresholds live in `DrowsinessConfig` (`drowsiness.py`).
The first ~60 frames with a visible face are used to **calibrate** the driver's normal
open-eye EAR (keep your eyes open at the start of the video).

## Project structure

```
drowsy-driver-alert/
├── main.py               pipeline + CLI + run() for Jupyter
├── face_detection.py     MediaPipe / dlib landmark backends
├── eye_detection.py      EAR, blink monitor
├── drowsiness.py         DrowsinessDetector, DriverState, config
├── yawn_detection.py     MAR, yawn monitor
├── alert_system.py       beep, voice, cooldown, logging
├── test_cases.py         unit tests (no camera needed)
├── requirements.txt
├── README.md
└── run_in_jupyter.ipynb  ready-made notebook (extra)
```

## IBM LinuxONE (s390x) notes — please read

1. **There is no camera on a LinuxONE server.** Run the system on a **recorded video file**
   (e.g. a short `.mp4` of a face) uploaded to the Jupyter file browser. The code uses video
   time (`frame / fps`), so results are the same on every run.
2. **Package availability on s390x.** Many pip packages publish no s390x wheels, so install may
   try to build from source. As far as I know, official `mediapipe` wheels are not provided for
   s390x — check with `pip install mediapipe` on your machine. Plan B is the **dlib backend**:
   ```bash
   sudo apt-get install -y build-essential cmake python3-dev python3-opencv   # or dnf/yum
   pip install dlib
   wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
   bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
   ```
   `backend="auto"` tries MediaPipe first and automatically falls back to dlib.
   (If `pip install opencv-python-headless` fails, the distro package `python3-opencv` works too.)
3. **Sound.** The server has no speakers. In Jupyter the beep is played by your **browser**
   (IPython `Audio`) and the voice message by the browser's speech synthesis. Browsers may block
   autoplay until you click on the page once. Alerts are always printed and saved to `alerts.log`.
4. The **logic and tests are pure NumPy/Python**, so they run on s390x with no extra libraries.

## Run in Jupyter Notebook

1. Copy the whole `drowsy-driver-alert/` folder to your LinuxONE Jupyter environment.
2. Open `run_in_jupyter.ipynb` (or create cells yourself):

```python
!pip install -r requirements.txt          # or install packages as described above
!python -m unittest test_cases -v         # 16 tests, should all pass

from main import run
summary = run("driver_video.mp4",         # your uploaded video
              output_path="annotated.avi",
              display_every=10)           # show every 10th frame inside the notebook
summary
```

## Run from terminal

```bash
python main.py --source driver_video.mp4 --output annotated.avi
python main.py --source 0                 # local webcam (not available on a server)
```

## Tuning

| Problem | Change |
|---|---|
| Too many false "eyes closed" alerts | raise `eye_closed_secs` (e.g. 2.0) |
| Missed yawns | lower `mar_threshold` (e.g. 0.5) |
| Wrong threshold for a driver with narrow eyes | calibration adapts it; clamp range is `ear_threshold_min/max` |
| Alerts repeat too often | raise `cooldown_secs` / `fatigue_cooldown_secs` in `AlertSystem` |

## Limitations

- Needs a clear, front-facing view of the face with decent lighting; sunglasses hide the eyes.
- Thresholds are heuristics; test on your own videos before relying on them.
- This is a learning/demo project, **not a certified safety device**.
