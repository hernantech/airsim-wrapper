# Camera Control Guide - AirSim Dual Drone Project

## Overview

This guide explains how to change camera angles and what your cameras are pointing at in your AirSim dual drone project.

## 📹 Quick Start

### Run the Interactive Demo
```bash
python camera_control_demo.py
# Choose option 2 for interactive control
```

### Basic Commands in Interactive Mode
```
camera> pitch 45        # Tilt camera down 45°
camera> yaw 90         # Turn camera right 90°
camera> fov 120        # Set wide field of view
camera> capture        # Take a photo
camera> reset          # Return to default view
```

## 🎯 Camera Control Methods

### 1. **Programmatic Control** (Recommended)

Use the new methods added to `BaseDroneController`:

```python
from controllers.base_controller import BaseDroneController

# Initialize your drone controller
drone = YourDroneController("Drone1")

# Set camera orientation
drone.set_camera_orientation("rgb_front", pitch=45, roll=0, yaw=90)

# Adjust field of view  
drone.set_camera_fov("rgb_front", 120)

# Point at specific target
drone.point_camera_at_target("rgb_front", target_position={"x": 50, "y": 0, "z": -10})

# Track another drone
drone.point_camera_at_target("rgb_front", target_drone="Drone2")

# Get current camera status
pose = drone.get_camera_pose("rgb_front")
print(f"Camera orientation: {pose['orientation']}")
```

### 2. **AirSim Settings File** (Static Configuration)

Create or modify your AirSim `settings.json` file:

```json
{
  "SettingsVersion": 1.2,
  "SimMode": "Multirotor",
  "Vehicles": {
    "Drone1": {
      "VehicleType": "SimpleFlight",
      "Cameras": {
        "rgb_front": {
          "X": 0.0, "Y": 0.0, "Z": 0.0,
          "Pitch": 45,    // Down 45°
          "Roll": 0,      // No roll
          "Yaw": 0,       // Forward facing
          "CaptureSettings": [{
            "ImageType": 0,
            "Width": 1280,
            "Height": 720,
            "FOV_Degrees": 90
          }]
        },
        "rgb_down": {
          "X": 0.0, "Y": 0.0, "Z": 0.0,
          "Pitch": 90,    // Straight down
          "Roll": 0,
          "Yaw": 0,
          "CaptureSettings": [{
            "ImageType": 0,
            "Width": 1280,
            "Height": 720,
            "FOV_Degrees": 120
          }]
        }
      }
    }
  }
}
```

## 📐 Camera Orientation Explained

### Pitch (Up/Down Rotation)
- **`-90°`**: Camera points straight up
- **`0°`**: Camera points forward (default)
- **`45°`**: Camera tilts down 45°
- **`90°`**: Camera points straight down

### Yaw (Left/Right Rotation)
- **`-90°`**: Camera points left
- **`0°`**: Camera points forward (default)
- **`90°`**: Camera points right
- **`180°`**: Camera points backward

### Roll (Tilt Left/Right)
- **`-45°`**: Camera tilts left 45°
- **`0°`**: Camera level (default)
- **`45°`**: Camera tilts right 45°

### Field of View (FOV)
- **`30-60°`**: Narrow/telephoto view (zoomed in)
- **`90°`**: Normal view (default)
- **`120-140°`**: Wide angle view (fish-eye effect)

## 🎯 Common Use Cases

### 1. **Aerial Mapping**
```python
# Straight down view with wide angle
drone.set_camera_orientation("rgb_front", pitch=90, roll=0, yaw=0)
drone.set_camera_fov("rgb_front", 120)
```

### 2. **Search and Rescue**
```python
# 45° down-forward view for better coverage
drone.set_camera_orientation("rgb_front", pitch=45, roll=0, yaw=0)
drone.set_camera_fov("rgb_front", 100)
```

### 3. **Surveillance/Security**
```python
# Forward view with narrow FOV for detail
drone.set_camera_orientation("rgb_front", pitch=15, roll=0, yaw=0)
drone.set_camera_fov("rgb_front", 60)
```

### 4. **Infrastructure Inspection**
```python
# Side view for inspecting buildings/towers
drone.set_camera_orientation("rgb_front", pitch=0, roll=0, yaw=90)
drone.set_camera_fov("rgb_front", 75)
```

### 5. **Follow/Track Target**
```python
# Automatically point camera at another drone
drone.point_camera_at_target("rgb_front", target_drone="Drone2")

# Or point at GPS coordinates
target = {"x": 100, "y": 50, "z": -20}  # NED coordinates
drone.point_camera_at_target("rgb_front", target_position=target)
```

## 🔧 Integration with Your Controllers

### Update Your Existing Controllers

Add camera control to your mission planning by modifying your controller's `compute_control` method:

```python
def compute_control(self, sensor_data, messages):
    # Your existing control logic...
    
    # Add dynamic camera control based on mission phase
    if self.mission_phase == "search":
        self.set_camera_orientation("rgb_front", pitch=60, roll=0, yaw=0)
        self.set_camera_fov("rgb_front", 120)
    elif self.mission_phase == "approach_target":
        # Point camera at detected target
        if self.target_position:
            self.point_camera_at_target("rgb_front", target_position=self.target_position)
    elif self.mission_phase == "follow":
        self.point_camera_at_target("rgb_front", target_drone="Drone2")
    
    return control_commands
```

## 🚀 Testing Camera Controls

### 1. **Run the Demo Script**
```bash
# Make sure AirSim is running first
python camera_control_demo.py
```

Choose:
- **Option 1**: Automated demo showing different camera angles
- **Option 2**: Interactive mode for manual testing

### 2. **Quick Manual Test**
```python
# In Python console or script
from controllers.base_controller import BaseDroneController

class TestController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

drone = TestController("Drone1")
drone.client.takeoffAsync(vehicle_name="Drone1").join()

# Test different angles
drone.set_camera_orientation("rgb_front", pitch=45, roll=0, yaw=0)
image = drone.get_rgb_image()  # Capture test image
```

## 🛠️ Troubleshooting

### Camera Not Moving
- Check that AirSim is running and connected
- Ensure camera name exists ("rgb_front", "ir_front")
- Verify drone is spawned and armed

### Images Look Wrong
- Check if color conversion is needed (RGB vs BGR)
- Verify camera settings in AirSim settings.json
- Test with different FOV values

### Performance Issues
- Reduce camera resolution in settings.json
- Limit camera update frequency
- Use fewer simultaneous camera views

## 📚 API Reference

### Available Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `set_camera_orientation()` | Set camera pitch/roll/yaw | `camera_name, pitch, roll, yaw` |
| `set_camera_fov()` | Set field of view | `camera_name, fov_degrees` |
| `get_camera_pose()` | Get current camera position/orientation | `camera_name` |
| `point_camera_at_target()` | Point camera at coordinates or drone | `camera_name, target_position=None, target_drone=None` |

### Camera Names
- `"rgb_front"` - Main RGB camera
- `"ir_front"` - Infrared camera  
- `"rgb_down"` - Downward RGB camera (if configured)

### Coordinate System
- **X**: Forward (positive = forward)
- **Y**: Right (positive = right)  
- **Z**: Down (positive = down, negative = up)

---

*For more advanced camera configurations, see the AirSim documentation at: https://microsoft.github.io/AirSim/image_apis/* 