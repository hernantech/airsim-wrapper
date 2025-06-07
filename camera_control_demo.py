#!/usr/bin/env python3
"""
Camera Control Demo for AirSim Dual Drone Project

This script demonstrates how to:
1. Change camera angles programmatically
2. Point cameras at specific targets
3. Adjust camera field of view
4. Create different camera views for various use cases
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import numpy as np
from controllers.base_controller import BaseDroneController

class CameraDemoController(BaseDroneController):
    """Demo controller focused on camera operations."""
    
    def compute_control(self, sensor_data, messages):
        """Required abstract method - minimal implementation for demo."""
        return {"action": "hover"}

def demonstrate_camera_controls():
    """Demonstrate various camera control capabilities."""
    
    print("=== AirSim Camera Control Demo ===")
    print("Make sure AirSim is running with your dual drone setup!")
    input("Press Enter to continue...")
    
    # Initialize drone controller
    try:
        drone = CameraDemoController("Drone1", "./demo_data")
        print(f"✓ Connected to {drone.drone_name}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("Make sure AirSim is running!")
        return
    
    try:
        # Take off to a good demo height
        print("\n--- Taking off for demo ---")
        drone.client.takeoffAsync(vehicle_name=drone.drone_name).join()
        drone.client.moveToZAsync(-10, 3, vehicle_name=drone.drone_name).join()  # 10m altitude
        print("✓ Ready for camera demo")
        
        # Demo 1: Different camera orientations
        print("\n=== Demo 1: Basic Camera Orientations ===")
        
        orientations = [
            {"name": "Forward view", "pitch": 0, "roll": 0, "yaw": 0},
            {"name": "Downward view (mapping)", "pitch": 90, "roll": 0, "yaw": 0}, 
            {"name": "45° down-forward", "pitch": 45, "roll": 0, "yaw": 0},
            {"name": "Right side view", "pitch": 0, "roll": 0, "yaw": 90},
            {"name": "Left side view", "pitch": 0, "roll": 0, "yaw": -90},
            {"name": "Backward view", "pitch": 0, "roll": 0, "yaw": 180},
        ]
        
        for orient in orientations:
            print(f"\n{orient['name']}:")
            drone.set_camera_orientation("rgb_front", 
                                       pitch=orient['pitch'], 
                                       roll=orient['roll'], 
                                       yaw=orient['yaw'])
            
            # Capture an image with this orientation
            rgb_image = drone.get_rgb_image()
            if rgb_image is not None:
                print(f"  📸 Captured image: {rgb_image.shape}")
            
            time.sleep(2)  # Give time to see the change
        
        # Demo 2: Field of View changes
        print("\n=== Demo 2: Field of View Changes ===")
        
        # Reset to forward view
        drone.set_camera_orientation("rgb_front", pitch=0, roll=0, yaw=0)
        
        fov_values = [60, 90, 120]  # Narrow to wide
        for fov in fov_values:
            print(f"\nSetting FOV to {fov}°")
            drone.set_camera_fov("rgb_front", fov)
            rgb_image = drone.get_rgb_image()
            if rgb_image is not None:
                print(f"  📸 Captured image with {fov}° FOV: {rgb_image.shape}")
            time.sleep(2)
        
        # Demo 3: Target tracking (if Drone2 exists)
        print("\n=== Demo 3: Target Tracking ===")
        try:
            # Check if Drone2 exists
            drone2_state = drone.client.getMultirotorState(vehicle_name="Drone2")
            print("✓ Drone2 detected - demonstrating target tracking")
            
            # Point camera at Drone2
            drone.point_camera_at_target("rgb_front", target_drone="Drone2")
            time.sleep(2)
            
            # Capture image looking at Drone2
            rgb_image = drone.get_rgb_image()
            if rgb_image is not None:
                print(f"  📸 Captured image targeting Drone2: {rgb_image.shape}")
                
        except Exception as e:
            print(f"Drone2 not available for target tracking demo: {e}")
            
            # Demo with fixed target position instead
            print("Demonstrating fixed position targeting...")
            target_pos = {"x": 50, "y": 0, "z": -5}  # Point 50m ahead
            drone.point_camera_at_target("rgb_front", target_position=target_pos)
            time.sleep(2)
        
        # Demo 4: Multiple camera views
        print("\n=== Demo 4: Multiple Camera Setup ===")
        
        # Try to set up multiple camera views if available
        cameras = ["rgb_front", "ir_front"]
        
        for i, camera in enumerate(cameras):
            try:
                # Set different orientation for each camera
                if camera == "rgb_front":
                    drone.set_camera_orientation(camera, pitch=0, roll=0, yaw=0)  # Forward
                elif camera == "ir_front":
                    drone.set_camera_orientation(camera, pitch=45, roll=0, yaw=0)  # Angled down
                
                print(f"✓ Configured {camera}")
                
                # Get current pose to verify
                pose = drone.get_camera_pose(camera)
                if pose:
                    print(f"  Current orientation: {pose['orientation']}")
                    
            except Exception as e:
                print(f"Camera {camera} not available: {e}")
        
        # Demo 5: Practical use cases
        print("\n=== Demo 5: Practical Use Cases ===")
        
        use_cases = [
            {
                "name": "Search and Rescue (wide downward view)",
                "camera": "rgb_front",
                "pitch": 60, "roll": 0, "yaw": 0,
                "fov": 120
            },
            {
                "name": "Surveillance (forward focused)",
                "camera": "rgb_front", 
                "pitch": 15, "roll": 0, "yaw": 0,
                "fov": 60
            },
            {
                "name": "Mapping (straight down)",
                "camera": "rgb_front",
                "pitch": 90, "roll": 0, "yaw": 0,
                "fov": 90
            },
            {
                "name": "Inspection (close-up angled)",
                "camera": "rgb_front",
                "pitch": 30, "roll": 0, "yaw": 0,
                "fov": 45
            }
        ]
        
        for use_case in use_cases:
            print(f"\n{use_case['name']}:")
            drone.set_camera_orientation(use_case['camera'],
                                       pitch=use_case['pitch'],
                                       roll=use_case['roll'], 
                                       yaw=use_case['yaw'])
            drone.set_camera_fov(use_case['camera'], use_case['fov'])
            
            # Capture sample image
            rgb_image = drone.get_rgb_image()
            if rgb_image is not None:
                print(f"  📸 Sample image captured: {rgb_image.shape}")
            
            time.sleep(3)  # Longer pause to appreciate each setup
        
        print("\n=== Demo Complete ===")
        print("Camera has been reset to default forward view")
        
        # Reset to default
        drone.set_camera_orientation("rgb_front", pitch=0, roll=0, yaw=0)
        drone.set_camera_fov("rgb_front", 90)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")
    finally:
        # Clean up
        try:
            drone.cleanup()
            print("✓ Demo cleanup complete")
        except:
            pass

def interactive_camera_control():
    """Interactive camera control interface."""
    
    print("\n=== Interactive Camera Control ===")
    print("Commands:")
    print("  pitch <angle>     - Set pitch angle (-90 to 90)")
    print("  roll <angle>      - Set roll angle (-180 to 180)")  
    print("  yaw <angle>       - Set yaw angle (-180 to 180)")
    print("  fov <degrees>     - Set field of view (30-120)")
    print("  target <x> <y> <z> - Point at position")
    print("  track drone2      - Track Drone2")
    print("  reset             - Reset to default view")
    print("  capture           - Take a photo")
    print("  status            - Show current camera status")
    print("  quit              - Exit")
    
    try:
        drone = CameraDemoController("Drone1", "./interactive_data")
        print(f"✓ Connected to {drone.drone_name}")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    try:
        while True:
            cmd = input("\ncamera> ").strip().lower().split()
            if not cmd:
                continue
                
            try:
                if cmd[0] == "quit":
                    break
                elif cmd[0] == "pitch" and len(cmd) == 2:
                    angle = float(cmd[1])
                    drone.set_camera_orientation("rgb_front", pitch=angle, roll=0, yaw=0)
                elif cmd[0] == "roll" and len(cmd) == 2:
                    angle = float(cmd[1])
                    drone.set_camera_orientation("rgb_front", pitch=0, roll=angle, yaw=0)
                elif cmd[0] == "yaw" and len(cmd) == 2:
                    angle = float(cmd[1])
                    drone.set_camera_orientation("rgb_front", pitch=0, roll=0, yaw=angle)
                elif cmd[0] == "fov" and len(cmd) == 2:
                    fov = float(cmd[1])
                    drone.set_camera_fov("rgb_front", fov)
                elif cmd[0] == "target" and len(cmd) == 4:
                    x, y, z = float(cmd[1]), float(cmd[2]), float(cmd[3])
                    drone.point_camera_at_target("rgb_front", target_position={"x": x, "y": y, "z": z})
                elif cmd[0] == "track" and len(cmd) == 2 and cmd[1] == "drone2":
                    drone.point_camera_at_target("rgb_front", target_drone="Drone2")
                elif cmd[0] == "reset":
                    drone.set_camera_orientation("rgb_front", pitch=0, roll=0, yaw=0)
                    drone.set_camera_fov("rgb_front", 90)
                    print("✓ Camera reset to default")
                elif cmd[0] == "capture":
                    rgb_image = drone.get_rgb_image()
                    if rgb_image is not None:
                        timestamp = int(time.time())
                        filename = f"manual_capture_{timestamp}.png"
                        import cv2
                        cv2.imwrite(filename, cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))
                        print(f"📸 Image saved: {filename}")
                    else:
                        print("✗ Failed to capture image")
                elif cmd[0] == "status":
                    pose = drone.get_camera_pose("rgb_front")
                    if pose:
                        print(f"Camera orientation: {pose['orientation']}")
                    else:
                        print("✗ Could not get camera status")
                else:
                    print("Invalid command. Type commands as shown above.")
                    
            except ValueError:
                print("Invalid number format")
            except Exception as e:
                print(f"Command error: {e}")
                
    except KeyboardInterrupt:
        print("\nExiting interactive mode")
    finally:
        try:
            drone.cleanup()
        except:
            pass

if __name__ == "__main__":
    print("AirSim Camera Control Demo")
    print("1. Run automated demo")
    print("2. Interactive camera control")
    
    choice = input("Select option (1 or 2): ").strip()
    
    if choice == "1":
        demonstrate_camera_controls()
    elif choice == "2":
        interactive_camera_control()
    else:
        print("Invalid choice") 