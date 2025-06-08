# Camera Viewers and Controls

This folder contains various camera viewer implementations and controls for the AirSim dual drone project.

## Files Overview

### Main Viewers
- **`headless_rgb_viewer.py`** - Best for remote/SSH environments, no display needed
- **`fast_rgb_viewer.py`** - Fast RGB viewer using pygame (requires display)
- **`simple_rgb_viewer.py`** - Lightweight viewer using PIL + tkinter (requires display)
- **`rgb_camera_viewer.py`** - Matplotlib-based viewer (slower, requires display)
- **`camera_viewer.py`** - Original camera viewer with keyboard controls

### Control & Demo
- **`camera_control_demo.py`** - Interactive demo with automated and manual camera control modes
- **`quick_camera_test.py`** - Quick test script for basic camera functionality

### Testing & Debug
- **`test_color_format_fix.py`** - Test script for debugging RGB color format issues

### Documentation
- **`CAMERA_CONTROLS.md`** - Comprehensive documentation for camera control methods

## Usage Notes

### For Remote/SSH Environments
Use `headless_rgb_viewer.py` - it doesn't require a display and saves RGB frames.

### For Local Development with Display
Choose based on performance needs:
- `fast_rgb_viewer.py` (pygame) - fastest
- `simple_rgb_viewer.py` (PIL/tkinter) - lightweight  
- `rgb_camera_viewer.py` (matplotlib) - feature-rich but slower

### RGB Format Compliance
All viewers maintain RGB format throughout for detectnet compatibility as per `../COLOR_FORMAT_GUIDE.md`.

## Quick Start

```bash
# For headless/remote environments
python camera_viewers/headless_rgb_viewer.py

# For local development (choose one)
python camera_viewers/fast_rgb_viewer.py
python camera_viewers/simple_rgb_viewer.py

# For camera control demo
python camera_viewers/camera_control_demo.py
``` 