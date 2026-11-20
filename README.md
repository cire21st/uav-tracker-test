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

Send the target to the Arduino (every frame):

```powershell
.\.venv\Scripts\python.exe main.py --serial auto    # find the Arduino automatically
.\.venv\Scripts\python.exe main.py --serial COM5    # or name the port
```

Each frame sends one text line `A,dx,dy,flag` at 115200 baud, the AUTO format of the team firmware (`uav-vision-tracker/firmware/motor_control`):

- `dx`, `dy`: pixel error from the frame center, as integers, like an x-y plane: **right and up are positive**. At 1280×720 the range is about ±640 and ±360.
- `flag`: 1 = target detected, 0 = not detected. `A,0,0,0` is still sent every frame as a heartbeat.
- The integers are sent as text digits, not 2-byte binary, the same way as the joystick message `M,x,y`.

The vision app opens the COM port itself, so it cannot run at the same time as another program that uses the same port (such as the joystick controller). `--serial auto` picks the one connected Arduino (official boards and CH340/FTDI/CP210x clones) and lists the ports if it cannot.

Show all options:

```powershell
.\.venv\Scripts\python.exe main.py --help
```

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The included UAV model is a community model. Its published metrics do not guarantee accuracy with your camera or environment. Model attribution, license, and checksum are documented in [`models/README.md`](models/README.md).
