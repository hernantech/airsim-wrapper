#!/usr/bin/env python3
"""
RGB-Native Camera Viewer for AirSim

This viewer maintains RGB format throughout, perfect for detectnet compatibility.
Uses imageio and matplotlib for RGB-native display.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import imageio
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from controllers.base_controller import BaseDroneController

class RGBNativeController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

class RGBCameraViewer:
    """RGB-native camera viewer using matplotlib."""
    
    def __init__(self, controller, camera_type="rgb"):
        self.controller = controller
        self.camera_type = camera_type
        self.running = False
        
        # Set up matplotlib
        plt.ion()  # Interactive mode
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_title(f"{controller.drone_name} - {camera_type.upper()} Camera (RGB Format)")
        self.ax.axis('off')
        
        # Initialize with empty image
        dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
        self.im = self.ax.imshow(dummy_img)
        
        self.frame_count = 0
        self.start_time = time.time()
        
    def get_image(self):
        """Get RGB image maintaining RGB format."""
        if self.camera_type == "rgb":
            return self.controller.get_rgb_image()
        elif self.camera_type == "ir":
            return self.controller.get_ir_image()
        else:
            return None
    
    def update_display(self):
        """Update the RGB display."""
        image = self.get_image()
        if image is not None:
            # Image is already in RGB format - perfect for matplotlib
            self.im.set_array(image)
            
            # Update title with info
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            self.ax.set_title(
                f"{self.controller.drone_name} - {self.camera_type.upper()} Camera "
                f"(RGB Format) - FPS: {fps:.1f}"
            )
            
            plt.draw()
            plt.pause(0.001)  # Small pause for display update
    
    def start_viewer(self, duration=None):
        """Start the RGB viewer."""
        print(f"Starting RGB-native viewer for {self.controller.drone_name}")
        print("RGB format maintained throughout - perfect for detectnet!")
        print("Close the matplotlib window to stop")
        
        self.running = True
        start_time = time.time()
        
        try:
            while self.running and plt.fignum_exists(self.fig.number):
                # Check duration limit
                if duration and (time.time() - start_time) > duration:
                    print(f"Duration limit reached: {duration}s")
                    break
                
                self.update_display()
                
                # Check if window was closed
                if not plt.fignum_exists(self.fig.number):
                    break
                    
        except KeyboardInterrupt:
            print("\nViewer interrupted by user")
        finally:
            self.stop_viewer()
    
    def stop_viewer(self):
        """Stop the viewer."""
        self.running = False
        plt.close(self.fig)
    
    def save_current_frame(self, filename=None):
        """Save current frame in RGB format."""
        image = self.get_image()
        if image is not None:
            if filename is None:
                timestamp = int(time.time())
                filename = f"rgb_frame_{self.controller.drone_name}_{timestamp}.png"
            
            # Use imageio to save RGB format
            imageio.imwrite(filename, image)
            print(f"RGB frame saved: {filename}")
            return filename
        return None

def quick_rgb_view(drone_name="Drone1", camera_type="rgb", duration=30):
    """Quick RGB camera view maintaining RGB format."""
    
    print(f"=== RGB-Native Camera Viewer ===")
    print(f"Drone: {drone_name}, Camera: {camera_type}")
    print("RGB format maintained throughout (detectnet compatible)")
    print(f"Duration: {duration}s")
    print()
    
    try:
        controller = RGBNativeController(drone_name)
        viewer = RGBCameraViewer(controller, camera_type)
        viewer.start_viewer(duration=duration)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AirSim is running!")

def interactive_rgb_viewer():
    """Interactive RGB viewer with camera controls."""
    
    print("=== Interactive RGB Camera Viewer ===")
    print("RGB format maintained throughout")
    
    try:
        controller = RGBNativeController("Drone1")
        viewer = RGBCameraViewer(controller, "rgb")
        
        print("\nCamera Controls (type in terminal):")
        print("  'w/s' - Pitch up/down")
        print("  'a/d' - Yaw left/right") 
        print("  'f' - Forward view")
        print("  'down' - Downward view")
        print("  'save' - Save current frame")
        print("  'quit' - Exit")
        
        # Start viewer in background
        import threading
        viewer_thread = threading.Thread(target=viewer.start_viewer, daemon=True)
        viewer_thread.start()
        
        current_pitch = 0
        current_yaw = 0
        
        while viewer.running:
            try:
                cmd = input("\nrgb_viewer> ").strip().lower()
                
                if cmd == "quit":
                    break
                elif cmd == "w":  # Pitch up
                    current_pitch = max(-90, current_pitch - 15)
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print(f"Pitch: {current_pitch}°")
                elif cmd == "s":  # Pitch down
                    current_pitch = min(90, current_pitch + 15)
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print(f"Pitch: {current_pitch}°")
                elif cmd == "a":  # Yaw left
                    current_yaw = current_yaw - 30
                    if current_yaw < -180:
                        current_yaw += 360
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print(f"Yaw: {current_yaw}°")
                elif cmd == "d":  # Yaw right
                    current_yaw = current_yaw + 30
                    if current_yaw > 180:
                        current_yaw -= 360
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print(f"Yaw: {current_yaw}°")
                elif cmd == "f":  # Forward
                    current_pitch, current_yaw = 0, 0
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print("Forward view")
                elif cmd == "down":  # Downward
                    current_pitch, current_yaw = 90, 0
                    controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                    print("Downward view")
                elif cmd == "save":
                    filename = viewer.save_current_frame()
                    if filename:
                        print(f"Frame saved in RGB format: {filename}")
                elif cmd == "":
                    continue
                else:
                    print("Unknown command")
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                break
        
        viewer.stop_viewer()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("RGB-Native Camera Viewer Options:")
    print("1. Quick RGB view (30 seconds)")
    print("2. Interactive RGB viewer with controls")
    print("3. Quick RGB view (custom duration)")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        quick_rgb_view()
    elif choice == "2":
        interactive_rgb_viewer()
    elif choice == "3":
        try:
            duration = int(input("Duration (seconds): "))
            quick_rgb_view(duration=duration)
        except ValueError:
            print("Invalid duration")
    else:
        print("Invalid choice") 