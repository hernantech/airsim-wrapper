#!/usr/bin/env python3
"""
Camera Display Utilities

Simple functions to add real-time camera viewing to existing drone controllers.
"""

import cv2
import numpy as np
import time
import threading
import imageio
from typing import Optional, Tuple, Callable

class CameraDisplay:
    """Utility class for displaying camera feeds in real-time."""
    
    def __init__(self, window_name="Camera Feed", window_size=(640, 480)):
        self.window_name = window_name
        self.window_size = window_size
        self.running = False
        self.display_thread = None
        self.image_callback = None
        
    def set_image_source(self, callback: Callable[[], Optional[np.ndarray]]):
        """Set the function that provides camera images."""
        self.image_callback = callback
    
    def start_display(self, show_info=True, fps_limit=30):
        """Start displaying camera feed in a separate thread."""
        if self.image_callback is None:
            raise ValueError("No image source set. Call set_image_source() first.")
        
        self.running = True
        self.display_thread = threading.Thread(
            target=self._display_loop,
            args=(show_info, fps_limit),
            daemon=True
        )
        self.display_thread.start()
        
        print(f"Camera display started: {self.window_name}")
        print("Press 'q' in camera window to stop display")
    
    def stop_display(self):
        """Stop the camera display."""
        self.running = False
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=1.0)
        cv2.destroyWindow(self.window_name)
    
    def _display_loop(self, show_info, fps_limit):
        """Internal display loop running in separate thread."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.window_size[0], self.window_size[1])
        
        frame_delay = 1.0 / fps_limit if fps_limit > 0 else 0
        last_frame_time = 0
        frame_count = 0
        fps_start_time = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Limit FPS
            if frame_delay > 0 and (current_time - last_frame_time) < frame_delay:
                time.sleep(0.001)
                continue
            
            try:
                # Get image from callback
                image = self.image_callback()
                if image is None:
                    time.sleep(0.01)
                    continue
                
                display_image = image.copy()
                
                # Add info overlay
                if show_info:
                    frame_count += 1
                    
                    # Calculate FPS every second
                    if current_time - fps_start_time >= 1.0:
                        current_fps = frame_count / (current_time - fps_start_time)
                        frame_count = 0
                        fps_start_time = current_time
                    else:
                        current_fps = frame_count / max(0.1, current_time - fps_start_time)
                    
                    # Add timestamp and FPS
                    timestamp = time.strftime("%H:%M:%S")
                    cv2.putText(display_image, f"Time: {timestamp}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(display_image, f"FPS: {current_fps:.1f}", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Use RGB-native display - no color conversion needed
                # AirSim provides RGB, detectnet expects RGB, keep RGB throughout
                
                # For now still use cv2.imshow but convert RGB->BGR only for display
                if len(display_image.shape) == 3 and display_image.shape[2] == 3:
                    display_bgr = cv2.cvtColor(display_image, cv2.COLOR_RGB2BGR)
                    cv2.imshow(self.window_name, display_bgr)
                else:
                    cv2.imshow(self.window_name, display_image)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                last_frame_time = current_time
                
            except Exception as e:
                print(f"Display error: {e}")
                time.sleep(0.1)
        
        cv2.destroyWindow(self.window_name)

def add_camera_display_to_controller(controller, camera_type="rgb", window_name=None):
    """
    Add real-time camera display to an existing drone controller.
    
    Args:
        controller: Drone controller instance with get_rgb_image() or get_ir_image()
        camera_type: "rgb" or "ir"
        window_name: Custom window name (optional)
    
    Returns:
        CameraDisplay instance that can be started/stopped
    """
    if window_name is None:
        window_name = f"{controller.drone_name} - {camera_type.upper()} Camera"
    
    display = CameraDisplay(window_name)
    
    if camera_type.lower() == "rgb":
        # RGB camera returns RGB data from AirSim - keep as RGB for detectnet compatibility
        display.set_image_source(controller.get_rgb_image)
    elif camera_type.lower() == "ir":
        # IR camera - use directly
        display.set_image_source(controller.get_ir_image)
    else:
        raise ValueError(f"Unknown camera type: {camera_type}")
    
    return display

def quick_camera_view(controller, camera_type="rgb", duration=None):
    """
    Quickly view a camera feed for testing/debugging.
    
    Args:
        controller: Drone controller instance
        camera_type: "rgb" or "ir"
        duration: How long to show (seconds), None for indefinite
    """
    print(f"Starting quick camera view: {camera_type.upper()}")
    print("Press 'q' to quit, 'c' to capture screenshot")
    
    window_name = f"Quick View - {controller.drone_name} {camera_type.upper()}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 600)
    
    start_time = time.time()
    screenshot_count = 0
    
    try:
        while True:
            # Check duration limit
            if duration and (time.time() - start_time) > duration:
                print(f"Duration limit reached: {duration}s")
                break
            
            # Get image
            if camera_type.lower() == "rgb":
                image = controller.get_rgb_image()
            elif camera_type.lower() == "ir":
                image = controller.get_ir_image()
            else:
                print(f"Unknown camera type: {camera_type}")
                break
            
            if image is None:
                time.sleep(0.01)
                continue
            
            display_image = image.copy()
            
            # Add timestamp
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(display_image, timestamp, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Keep RGB format for detectnet compatibility - only convert for cv2.imshow
            if camera_type.lower() == "rgb" and len(display_image.shape) == 3 and display_image.shape[2] == 3:
                # Convert RGB to BGR only for OpenCV display, but keep original RGB data
                display_for_show = cv2.cvtColor(display_image, cv2.COLOR_RGB2BGR)
            else:
                display_for_show = display_image
            
            cv2.imshow(window_name, display_for_show)
            
            # Handle keys
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                screenshot_count += 1
                filename = f"quick_capture_{controller.drone_name}_{camera_type}_{screenshot_count:03d}.png"
                cv2.imwrite(filename, display_image)
                print(f"Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\nQuick view interrupted")
    finally:
        cv2.destroyWindow(window_name)

def side_by_side_view(controller, duration=None):
    """Show RGB and IR cameras side by side."""
    
    print("Starting side-by-side camera view (RGB + IR)")
    print("Press 'q' to quit")
    
    window_name = f"{controller.drone_name} - Dual Camera View"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1280, 400)
    
    start_time = time.time()
    
    try:
        while True:
            if duration and (time.time() - start_time) > duration:
                break
            
            # Get both images
            rgb_image = controller.get_rgb_image()
            ir_image = controller.get_ir_image()
            
            if rgb_image is None or ir_image is None:
                time.sleep(0.01)
                continue
            
            # Resize images to same height
            target_height = 360
            rgb_resized = cv2.resize(
                cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR),
                (int(target_height * rgb_image.shape[1] / rgb_image.shape[0]), target_height)
            )
            ir_resized = cv2.resize(
                ir_image,
                (int(target_height * ir_image.shape[1] / ir_image.shape[0]), target_height)
            )
            
            # Add labels
            cv2.putText(rgb_resized, "RGB Camera", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(ir_resized, "IR Camera", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Combine side by side
            combined = np.hstack([rgb_resized, ir_resized])
            
            cv2.imshow(window_name, combined)
            
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nDual view interrupted")
    finally:
        cv2.destroyWindow(window_name)

# Convenience functions for common use cases
def start_rgb_display(controller, **kwargs):
    """Start RGB camera display."""
    display = add_camera_display_to_controller(controller, "rgb", **kwargs)
    display.start_display()
    return display

def start_ir_display(controller, **kwargs):
    """Start IR camera display."""
    display = add_camera_display_to_controller(controller, "ir", **kwargs)
    display.start_display()
    return display 