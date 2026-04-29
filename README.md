# Robomaster TT Activities

This project contains drone flight control and detection utilities for Robomaster TT activities.

## Drone Compatibility

These programs are **verified to work with the Robomaster TT Tello Talent drone by DJI**.

### Supported Drone Model
- **Manufacturer**: DJI
- **Model**: Robomaster TT Tello Talent
- **Series**: Robomaster TT (Educational/Competition Series)

### Technical Specifications (Compatible Device)
- **Flight Time**: Up to 13 minutes
- **Max Speed**: 8 m/s
- **Camera**: 5MP with color detection capabilities
- **Connectivity**: WiFi-based control and video transmission
- **Control Protocol**: SDK-based Python API support
- **Operating System Support**: Windows, macOS, Linux

### Why Compatible
This drone features:
- Built-in Python SDK support for autonomous flight control
- HD video camera suitable for green/color detection
- Reliable WiFi connectivity for real-time command execution
- Stable flight characteristics for trajectory testing
- Support for complex flight patterns and waypoint navigation

### Platform Compatibility
- **Windows**: ✅ Fully supported (verified)
- **Linux**: ⚠️ Limited support - The `robomaster` library has platform-specific limitations on Linux
- **macOS**: ⚠️ Limited support - Similar robomaster library constraints

**Note**: While the Robomaster TT programs are Windows-primary, this project also includes Tello drone support (via `djitellopy`), which works reliably on **both Windows and Linux**.

## Features

- **Flight Testing**: Test and record drone flight paths
- **Green Detection**: Detect green objects in camera feed
- **Trajectory Testing**: Test flight trajectories
- **Shape Detection**: Detect circles and triangles
- **Connection Checking**: Verify drone connection

## Files

- `camera.py` - Camera interface and capture
- `greendetector.py` - Green color detection
- `flight_recorder.py` - Record and playback flight data
- `test_flight.py` - Basic flight tests
- `trajectory_test.py` - Trajectory testing
- `circle.py` - Circle detection
- `triangle.py` - Triangle detection
- `check_connection.py` - Connection verification

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Anaconda/Miniconda**: Latest version recommended

### Anaconda Environment Setup

To easily set up the development environment using Anaconda:

1. **Create a new conda environment**:
   ```bash
   conda create -n droneclean python=3.9
   ```

2. **Activate the environment**:
   ```bash
   conda activate droneclean
   ```

3. **Install dependencies from requirements.txt**:
   ```bash
   pip install -r requirements.txt
   ```

### Dependencies
All required packages are listed in `requirements.txt`:
- `robomaster` - DJI Robomaster SDK
- `djitellopy` - Tello drone SDK
- `opencv-python` - Computer vision library
- `numpy` - Numerical computing

## Usage

Run individual test scripts as needed:
```
python test_flight.py
python greendetector.py
```
