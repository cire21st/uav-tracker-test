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

Send the target to the pan-tilt controller (every frame):

```powershell
.\.venv\Scripts\python.exe main.py --udp                 # to control.py on this PC (127.0.0.1:5005), recommended
.\.venv\Scripts\python.exe main.py --serial auto         # or straight to the Arduino, without control.py
```

Values follow the team firmware (`uav-vision-tracker/firmware/motor_control`) AUTO mode:

- `dx`, `dy`: angle error from the frame center × 10, as integers. **Right and up are positive** (same as pushing the joystick right/up). Example: `250` = 25.0°.
- `flag`: 1 = target detected, 0 = not detected. `0,0,0` is still sent every frame as a heartbeat.

`--udp` sends `dx,dy,flag` to `control.py`, which owns the COM port and switches between keyboard (F1), joystick (F2) and auto (F3) modes. `--serial` opens the COM port itself and sends `A,dx,dy,flag\n` at 115200 baud; use it only when `control.py` is not running, since only one program can open the port. `--serial auto` picks the one connected Arduino (official boards and CH340/FTDI/CP210x clones) and lists the ports if it cannot.

Angles are computed with `atan` from the camera's diagonal field of view (`--dfov`, default 95.8 for the STCOM biz FHD60F). Keep the camera's native aspect ratio (e.g. 16:9 at 1280×720); a cropped mode changes the real field of view.

Show all options:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The included UAV model is a community model. Its published metrics do not guarantee accuracy with your camera or environment. Model attribution, license, and checksum are documented in [`models/README.md`](models/README.md).
