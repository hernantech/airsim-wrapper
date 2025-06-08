#!/usr/bin/env python3
"""
Headless RGB Camera Viewer - No Display Required

Perfect for remote/headless systems. Maintains RGB format and saves frames.
Great for testing and when you can't display windows.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import airsim
import numpy as np
import time
import imageio

class HeadlessRGBViewer:
    """Headless RGB viewer that saves frames instead of displaying."""
    
    def __init__(self, drone_name="Drone1"):
        self.drone_name = drone_name
        self.client = None
        self.running = False
        
    def connect(self):
        """Connect to AirSim."""
        try:
            self.client = airsim.MultirotorClient()
            self.client.confirmConnection()
            print(f"✓ Connected to AirSim for {self.drone_name}")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def get_rgb_image(self):
        """Get RGB image maintaining RGB format."""
        try:
            responses = self.client.simGetImages([
                airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
            ], vehicle_name=self.drone_name)
            
            if responses:
                response = responses[0]
                img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                rgb_image = img1d.reshape(response.height, response.width, 3)
                return rgb_image
            return None
        except Exception as e:
            print(f"Error getting image: {e}")
            return None
    
    def set_camera_orientation(self, pitch=0, roll=0, yaw=0):
        """Set camera orientation."""
        try:
            pitch_rad = np.radians(pitch)
            roll_rad = np.radians(roll)
            yaw_rad = np.radians(yaw)
            
            orientation = airsim.to_quaternion(pitch_rad, roll_rad, yaw_rad)
            camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), orientation)
            
            self.client.simSetCameraPose("rgb_front", camera_pose, vehicle_name=self.drone_name)
            print(f"Camera set: pitch={pitch}°, roll={roll}°, yaw={yaw}°")
            return True
        except Exception as e:
            print(f"Error setting camera: {e}")
            return False
    
    def save_rgb_frame(self, rgb_image, filename=None):
        """Save RGB frame using imageio (maintains RGB format)."""
        if rgb_image is None:
            return False
            
        if filename is None:
            timestamp = int(time.time())
            filename = f"headless_rgb_{self.drone_name}_{timestamp}.png"
        
        try:
            # Use imageio to maintain RGB format
            imageio.imwrite(filename, rgb_image)
            print(f"✓ RGB frame saved: {filename}")
            return True
        except Exception as e:
            print(f"Error saving frame: {e}")
            return False
    
    def capture_sequence(self, num_frames=10, interval=1.0):
        """Capture a sequence of RGB frames."""
        print(f"\n=== Capturing {num_frames} RGB frames ===")
        print(f"Interval: {interval}s between frames")
        print("RGB format maintained for detectnet compatibility")
        
        if not self.connect():
            return
        
        captured = 0
        for i in range(num_frames):
            print(f"\nCapturing frame {i+1}/{num_frames}...")
            
            rgb_image = self.get_rgb_image()
            if rgb_image is not None:
                filename = f"sequence_rgb_{self.drone_name}_{i+1:03d}.png"
                if self.save_rgb_frame(rgb_image, filename):
                    captured += 1
                    print(f"  Shape: {rgb_image.shape}")
                    print(f"  Sample pixel (RGB): {rgb_image[100, 100, :]}")
            else:
                print("  Failed to capture image")
            
            if i < num_frames - 1:  # Don't wait after last frame
                time.sleep(interval)
        
        print(f"\n✓ Sequence complete: {captured}/{num_frames} frames saved")
    
    def test_camera_angles(self):
        """Test different camera angles and save RGB frames."""
        print("\n=== Testing Camera Angles ===")
        
        if not self.connect():
            return
        
        angles = [
            (0, 0, 0, "forward"),
            (-30, 0, 0, "up_30"),
            (45, 0, 0, "down_45"),
            (90, 0, 0, "straight_down"),
            (0, 0, -90, "left_90"),
            (0, 0, 90, "right_90"),
            (0, 0, 180, "backward"),
            (0, 0, 0, "reset_forward")
        ]
        
        for pitch, roll, yaw, name in angles:
            print(f"\n--- {name.replace('_', ' ').title()} View ---")
            
            # Set camera angle
            if self.set_camera_orientation(pitch, roll, yaw):
                time.sleep(1)  # Wait for camera to move
                
                # Capture RGB frame
                rgb_image = self.get_rgb_image()
                if rgb_image is not None:
                    filename = f"angle_test_{name}_rgb.png"
                    self.save_rgb_frame(rgb_image, filename)
                    print(f"  RGB shape: {rgb_image.shape}")
                else:
                    print("  Failed to capture image")
            else:
                print("  Failed to set camera angle")
        
        print("\n✓ Camera angle test complete")
    
    def live_monitoring(self, duration=60, save_interval=5):
        """Monitor camera and save RGB frames periodically."""
        print(f"\n=== Live RGB Monitoring ===")
        print(f"Duration: {duration}s, saving every {save_interval}s")
        print("RGB format maintained throughout")
        
        if not self.connect():
            return
        
        start_time = time.time()
        last_save = 0
        frame_count = 0
        
        try:
            while time.time() - start_time < duration:
                current_time = time.time() - start_time
                
                # Get RGB image
                rgb_image = self.get_rgb_image()
                if rgb_image is not None:
                    frame_count += 1
                    
                    # Save periodically
                    if current_time - last_save >= save_interval:
                        filename = f"monitor_rgb_{int(current_time):04d}s.png"
                        self.save_rgb_frame(rgb_image, filename)
                        last_save = current_time
                        
                        # Print stats
                        fps = frame_count / current_time if current_time > 0 else 0
                        print(f"  Time: {int(current_time)}s, Frames: {frame_count}, FPS: {fps:.1f}")
                
                time.sleep(0.1)  # 10 FPS monitoring
                
        except KeyboardInterrupt:
            print("\nMonitoring interrupted by user")
        
        print(f"\n✓ Monitoring complete: {frame_count} frames processed")

def interactive_headless():
    """Interactive headless camera control."""
    print("\n=== Interactive Headless RGB Viewer ===")
    
    viewer = HeadlessRGBViewer("Drone1")
    if not viewer.connect():
        return
    
    print("\nCommands:")
    print("  'cap' - Capture single RGB frame")
    print("  'seq <n>' - Capture sequence of n frames")
    print("  'angle <pitch> <yaw>' - Set camera angle and capture")
    print("  'test' - Test all camera angles")
    print("  'monitor <duration>' - Monitor and save frames")
    print("  'quit' - Exit")
    
    while True:
        try:
            cmd = input("\nheadless> ").strip().split()
            if not cmd:
                continue
            
            if cmd[0] == "quit":
                break
            elif cmd[0] == "cap":
                rgb_image = viewer.get_rgb_image()
                if rgb_image is not None:
                    viewer.save_rgb_frame(rgb_image)
                else:
                    print("Failed to capture image")
            elif cmd[0] == "seq" and len(cmd) == 2:
                try:
                    n = int(cmd[1])
                    viewer.capture_sequence(n, 1.0)
                except ValueError:
                    print("Invalid number")
            elif cmd[0] == "angle" and len(cmd) == 3:
                try:
                    pitch = float(cmd[1])
                    yaw = float(cmd[2])
                    viewer.set_camera_orientation(pitch, 0, yaw)
                    time.sleep(1)
                    rgb_image = viewer.get_rgb_image()
                    if rgb_image is not None:
                        viewer.save_rgb_frame(rgb_image)
                except ValueError:
                    print("Invalid angles")
            elif cmd[0] == "test":
                viewer.test_camera_angles()
            elif cmd[0] == "monitor" and len(cmd) == 2:
                try:
                    duration = int(cmd[1])
                    viewer.live_monitoring(duration, 5)
                except ValueError:
                    print("Invalid duration")
            else:
                print("Unknown command")
                
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    
    print("Interactive session ended")

if __name__ == "__main__":
    print("Headless RGB Camera Viewer")
    print("Perfect for remote systems - no display required")
    print("Maintains RGB format for detectnet compatibility")
    print()
    
    print("Options:")
    print("1. Capture 10-frame sequence")
    print("2. Test camera angles")
    print("3. Live monitoring (60s)")
    print("4. Interactive mode")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        viewer = HeadlessRGBViewer("Drone1")
        viewer.capture_sequence(10, 2.0)
    elif choice == "2":
        viewer = HeadlessRGBViewer("Drone1")
        viewer.test_camera_angles()
    elif choice == "3":
        viewer = HeadlessRGBViewer("Drone1")
        viewer.live_monitoring(60, 5)
    elif choice == "4":
        interactive_headless()
    else:
        print("Invalid choice") 