# Robomaster Tello — First-Practice

This repository contains Python example programs and tests for a Tello / Robomaster-style drone, developed and tested on Windows.

**Important:** These scripts were created for Windows and may not work on other operating systems.

## Quick setup (Windows)

1. Install Python 3.8+ and [conda] (optional but recommended).
2. (Optional) Create and activate a conda environment:

```powershell
conda create -n droneclean python=3.10 -y
conda activate droneclean
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Connect your PC to the Tello drone's Wi‑Fi network (the drone acts as an access point).

5. Run a script, for example:

```powershell
python check_connection.py
python test_flight.py
```

## Files overview

- `camera.py`: Camera helper utilities (capture/display).
- `check_connection.py`: Verify connection to the drone and basic API reachability.
- `circle.py`: Example flight that flies a circular trajectory.
- `flight_recorder.py`: Record telemetry/flight data to a file.
- `greendetector.py`: Simple color detector (green) using the camera frames.
- `test_flight.py`: Short test flight script — good for initial checks.
- `trajectory_test.py`: Follow a pre-planned trajectory for testing.
- `triangle.py`: Example flight making a triangle pattern.
- `requirements.txt`: Python dependencies used by the project.
- `camera.py`: Camera utilities used by other demos.

### `final_project/`

This folder contains personal experiments and the final project code.

- `activate.txt`: Notes or activation instructions for the final project.
- `colortest.py`: Color-detection experiments.
- `ledtest.py`: LED test scripts for the platform.
- `movestest.py`: FINAL project code — this is the main, final movement program for the project.

## Notes & safety

- Always test over a soft surface and in an open area free of obstacles.
- Make sure the drone battery is charged and firmware is up to date.
- Use small, incremental tests (connection → motors → short flight) before running full scripts.

## Troubleshooting

- If scripts cannot reach the drone, ensure your PC is connected to the drone Wi‑Fi and no VPN or firewall is blocking UDP/TCP ports.
- Use `check_connection.py` first to confirm connectivity.

## Want changes?
If you want a different layout, more detailed setup instructions, or CI/test automation, tell me which section to expand.

---
Created for personal Tello / Robomaster drone development (Windows only).

