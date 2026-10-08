# UAV Tracker Test

A small test project that detects UAVs from a webcam and tracks them with ByteTrack.

The application draws a bounding box and center point for each detection. It also prints `cx`, `cy`, `error_x`, and `error_y` relative to the center of the camera frame.

This repository is for testing and learning only. It is not a production or safety-critical tracking system.

## Requirements

- Windows
- Python 3.11 or 3.12
- A webcam or USB camera

## Install

```powershell
git clone https://github.com/cire21st/uav-tracker-test.git
cd uav-tracker-test

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe main.py
```

Default settings:

- Model: `models/best.pt`
- Tracker: ByteTrack
- Class 0: `quadcopter`
- Class 1: `fixed-wing`
- Camera: device 0
- Exit: `Q` or `Esc`

Use another camera:

```powershell
.\.venv\Scripts\python.exe main.py --camera 1
```

Track quadcopters only:

```powershell
.\.venv\Scripts\python.exe main.py --classes 0
```

Lower the detection confidence threshold:

```powershell
.\.venv\Scripts\python.exe main.py --conf 0.15
```

Show all options:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The included UAV model is a community model. Its published metrics do not guarantee accuracy with your camera or environment. Model attribution, license, and checksum are documented in [`models/README.md`](models/README.md).
