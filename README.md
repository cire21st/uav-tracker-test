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
- Confidence threshold: 0.50
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

Send the target angle error to an Arduino over serial (every frame):

```powershell
.\.venv\Scripts\python.exe main.py --serial auto    # find the Arduino automatically
.\.venv\Scripts\python.exe main.py --serial COM5    # or name the port
```

`auto` picks the one connected Arduino (official boards and CH340/FTDI/CP210x clones). If none or more than one is found, the app stops before opening the camera and lists the available ports; then pass the port name instead.

The message is `<valid,ax,ay>\n` at 115200 baud. `ax` and `ay` are the angle errors from the frame center in 0.1° units (right/down positive), computed with `atan` from the camera's diagonal field of view (`--dfov`, default 95.8). When nothing is detected, `<0,0,0>` is still sent as a heartbeat. Keep the camera's native aspect ratio (e.g. 16:9 at 1280×720); a cropped mode changes the real field of view.

Show all options:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The included UAV model is a community model. Its published metrics do not guarantee accuracy with your camera or environment. Model attribution, license, and checksum are documented in [`models/README.md`](models/README.md).
