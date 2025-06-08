#!/usr/bin/env python3
"""
Real-time Camera Viewer for AirSim Dual Drone Project

This script provides real-time visualization of camera feeds while 
controlling camera orientation programmatically.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import time
import threading
from controllers.base_controller import BaseDroneController

class CameraViewer(BaseDroneController):
    """Real-time camera viewer with programmatic control."""
    
    def __init__(self, drone_name="Drone1"):
        super().__init__(drone_name, "./viewer_data")
        self.running = False
        self.display_thread = None
        self.current_rgb = None
        self.current_ir = None
        
    def compute_control(self, sensor_data, messages):
        """Required abstract method - minimal implementation."""
        return {"action": "hover"}
    
    def capture_loop(self):
        """Continuously capture images from cameras."""
        while self.running:
            try:
                # Capture RGB and IR images
                self.current_rgb = self.get_rgb_image()
                self.current_ir = self.get_ir_image()
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(0.1)
    
    def display_cameras(self, show_rgb=True, show_ir=True, window_size=(640, 480)):
        """Display camera feeds in real-time windows."""
        
        if show_rgb:
            cv2.namedWindow('RGB Camera', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('RGB Camera', window_size[0], window_size[1])
        
        if show_ir:
            cv2.namedWindow('IR Camera', cv2.WINDOW_NORMAL) 
            cv2.resizeWindow('IR Camera', window_size[0], window_size[1])
        
        print("Camera viewer started!")
        print("Controls:")
        print("  'q' - Quit viewer")
        print("  '1' - Point camera forward")
        print("  '2' - Point camera down")
        print("  '3' - Point camera left")
        print("  '4' - Point camera right")
        print("  '5' - Point camera back")
        print("  'w/s' - Adjust pitch up/down")
        print("  'a/d' - Adjust yaw left/right")
        print("  '+/-' - Zoom in/out (FOV)")
        
        current_pitch = 0
        current_yaw = 0
        current_fov = 90
        
        while self.running:
            key_pressed = False
            
            # Display RGB camera
            if show_rgb and self.current_rgb is not None:
                # Add overlay information
                display_rgb = self.current_rgb.copy()
                
                # Add camera info overlay
                cv2.putText(display_rgb, f"Pitch: {current_pitch:.1f}°", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_rgb, f"Yaw: {current_yaw:.1f}°", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_rgb, f"FOV: {current_fov:.1f}°", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(display_rgb, "RGB Camera", (10, display_rgb.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Convert RGB to BGR for OpenCV display
                display_rgb_bgr = cv2.cvtColor(display_rgb, cv2.COLOR_RGB2BGR)
                cv2.imshow('RGB Camera', display_rgb_bgr)
            
            # Display IR camera
            if show_ir and self.current_ir is not None:
                display_ir = self.current_ir.copy()
                cv2.putText(display_ir, "IR Camera", (10, display_ir.shape[0] - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.imshow('IR Camera', display_ir)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('1'):  # Forward
                current_pitch, current_yaw = 0, 0
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('2'):  # Down
                current_pitch, current_yaw = 90, 0
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('3'):  # Left
                current_pitch, current_yaw = 0, -90
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('4'):  # Right
                current_pitch, current_yaw = 0, 90
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('5'):  # Back
                current_pitch, current_yaw = 0, 180
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('w'):  # Pitch up
                current_pitch = max(-90, current_pitch - 15)
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('s'):  # Pitch down
                current_pitch = min(90, current_pitch + 15)
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('a'):  # Yaw left
                current_yaw = current_yaw - 15
                if current_yaw < -180:
                    current_yaw += 360
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('d'):  # Yaw right
                current_yaw = current_yaw + 15
                if current_yaw > 180:
                    current_yaw -= 360
                self.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                key_pressed = True
            elif key == ord('+') or key == ord('='):  # Zoom in (decrease FOV)
                current_fov = max(30, current_fov - 10)
                self.set_camera_fov("rgb_front", current_fov)
                key_pressed = True
            elif key == ord('-'):  # Zoom out (increase FOV)
                current_fov = min(120, current_fov + 10)
                self.set_camera_fov("rgb_front", current_fov)
                key_pressed = True
            
            if key_pressed:
                print(f"Camera: Pitch={current_pitch:.1f}°, Yaw={current_yaw:.1f}°, FOV={current_fov:.1f}°")
        
        cv2.destroyAllWindows()
    
    def start_viewer(self, show_rgb=True, show_ir=True):
        """Start the real-time camera viewer."""
        self.running = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
        # Start display (blocking)
        try:
            self.display_cameras(show_rgb, show_ir)
        except KeyboardInterrupt:
            print("\nViewer interrupted by user")
        finally:
            self.stop_viewer()
    
    def stop_viewer(self):
        """Stop the camera viewer."""
        self.running = False
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1.0)
        cv2.destroyAllWindows()

def view_single_camera(drone_name="Drone1", camera_name="rgb_front"):
    """Simple single camera viewer without controls."""
    
    print(f"Starting simple viewer for {drone_name} - {camera_name}")
    print("Press 'q' to quit, 'c' to capture screenshot")
    
    viewer = CameraViewer(drone_name)
    
    cv2.namedWindow(f'{drone_name} - {camera_name}', cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f'{drone_name} - {camera_name}', 800, 600)
    
    screenshot_count = 0
    
    try:
        while True:
            if camera_name == "rgb_front":
                image = viewer.get_rgb_image()
                if image is not None:
                    # Convert RGB to BGR for display
                    display_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                else:
                    continue
            elif camera_name == "ir_front":
                image = viewer.get_ir_image()
                if image is not None:
                    display_image = image
                else:
                    continue
            else:
                print(f"Unknown camera: {camera_name}")
                break
            
            # Add timestamp
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(display_image, timestamp, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow(f'{drone_name} - {camera_name}', display_image)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Capture screenshot
                screenshot_count += 1
                filename = f"screenshot_{drone_name}_{camera_name}_{screenshot_count:03d}.png"
                cv2.imwrite(filename, display_image)
                print(f"Screenshot saved: {filename}")
                
    except KeyboardInterrupt:
        print("\nViewer interrupted")
    finally:
        cv2.destroyAllWindows()
        viewer.cleanup()

if __name__ == "__main__":
    print("AirSim Camera Viewer Options:")
    print("1. Interactive camera viewer (with controls)")
    print("2. Simple RGB camera viewer")
    print("3. Simple IR camera viewer")
    print("4. Dual camera viewer (RGB + IR)")
    
    choice = input("Select option (1-4): ").strip()
    
    try:
        if choice == "1":
            viewer = CameraViewer("Drone1")
            viewer.start_viewer(show_rgb=True, show_ir=True)
        elif choice == "2":
            view_single_camera("Drone1", "rgb_front")
        elif choice == "3":
            view_single_camera("Drone1", "ir_front")
        elif choice == "4":
            viewer = CameraViewer("Drone1")
            viewer.start_viewer(show_rgb=True, show_ir=True)
        else:
            print("Invalid choice")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AirSim is running and drone is connected!") 