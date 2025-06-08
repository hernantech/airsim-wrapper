#!/usr/bin/env python3
"""
Quick Camera Test - See what your programmatically controlled camera sees
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.base_controller import BaseDroneController
from utils.camera_display import quick_camera_view

class QuickTestController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

if __name__ == "__main__":
    print("Quick Camera Test")
    print("This will show you what your camera sees while you control it programmatically")
    
    try:
        # Connect to drone
        controller = QuickTestController("Drone1")
        print("✓ Connected to Drone1")
        
        # Test different camera angles
        angles = [
            (0, 0, "Forward view"),
            (45, 0, "45° down"),
            (90, 0, "Straight down"),
            (0, 90, "Right side"),
            (0, -90, "Left side"),
        ]
        
        print("\nTesting different camera angles...")
        print("Each view will show for 5 seconds")
        
        for pitch, yaw, description in angles:
            print(f"\n{description} (Pitch: {pitch}°, Yaw: {yaw}°)")
            
            # Set camera angle programmatically
            controller.set_camera_orientation("rgb_front", pitch=pitch, yaw=yaw)
            
            # Show what the camera sees for 5 seconds
            quick_camera_view(controller, camera_type="rgb", duration=5)
        
        print("\nTest complete! Camera reset to forward view.")
        controller.set_camera_orientation("rgb_front", pitch=0, yaw=0)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AirSim is running!") 