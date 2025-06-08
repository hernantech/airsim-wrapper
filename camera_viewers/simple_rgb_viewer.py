#!/usr/bin/env python3
"""
Simple RGB-Native Camera Viewer using PIL + tkinter

Lighter than matplotlib, simpler than pygame.
Maintains RGB format throughout for detectnet compatibility.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import imageio
from controllers.base_controller import BaseDroneController

class SimpleRGBController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

class SimpleRGBViewer:
    """Simple RGB-native camera viewer using tkinter + PIL."""
    
    def __init__(self, controller, camera_type="rgb", window_size=(800, 600)):
        self.controller = controller
        self.camera_type = camera_type
        self.window_size = window_size
        self.running = False
        
        # Create tkinter window
        self.root = tk.Tk()
        self.root.title(f"{controller.drone_name} - {camera_type.upper()} Camera (RGB)")
        self.root.geometry(f"{window_size[0]}x{window_size[1]+100}")
        
        # Create image label
        self.image_label = tk.Label(self.root)
        self.image_label.pack(pady=10)
        
        # Create info label
        self.info_label = tk.Label(self.root, text="RGB Format - Detectnet Compatible", 
                                  fg="green", font=("Arial", 12))
        self.info_label.pack()
        
        # Create control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5)
        
        # Camera control buttons
        tk.Button(control_frame, text="↑ Pitch Up", 
                 command=lambda: self.adjust_camera(-15, 0)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="↓ Pitch Down",
                 command=lambda: self.adjust_camera(15, 0)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="← Yaw Left",
                 command=lambda: self.adjust_camera(0, -30)).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="→ Yaw Right",
                 command=lambda: self.adjust_camera(0, 30)).pack(side=tk.LEFT, padx=2)
        
        # Quick preset buttons
        preset_frame = tk.Frame(self.root)
        preset_frame.pack(pady=5)
        
        tk.Button(preset_frame, text="Forward", 
                 command=lambda: self.set_camera_preset(0, 0)).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="Down", 
                 command=lambda: self.set_camera_preset(90, 0)).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="Left", 
                 command=lambda: self.set_camera_preset(0, -90)).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="Right", 
                 command=lambda: self.set_camera_preset(0, 90)).pack(side=tk.LEFT, padx=2)
        tk.Button(preset_frame, text="Save Frame", 
                 command=self.save_frame).pack(side=tk.LEFT, padx=2)
        
        # Camera state
        self.current_pitch = 0
        self.current_yaw = 0
        
        # Stats
        self.frame_count = 0
        self.start_time = time.time()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.stop_viewer)
        
    def get_image(self):
        """Get RGB image maintaining RGB format."""
        if self.camera_type == "rgb":
            return self.controller.get_rgb_image()
        elif self.camera_type == "ir":
            return self.controller.get_ir_image()
        return None
    
    def adjust_camera(self, pitch_delta, yaw_delta):
        """Adjust camera by delta amounts."""
        self.current_pitch = max(-90, min(90, self.current_pitch + pitch_delta))
        self.current_yaw = (self.current_yaw + yaw_delta) % 360
        if self.current_yaw > 180:
            self.current_yaw -= 360
            
        self.controller.set_camera_orientation("rgb_front", 
                                             pitch=self.current_pitch, 
                                             yaw=self.current_yaw)
        print(f"Camera: Pitch={self.current_pitch}°, Yaw={self.current_yaw}°")
    
    def set_camera_preset(self, pitch, yaw):
        """Set camera to preset position."""
        self.current_pitch = pitch
        self.current_yaw = yaw
        self.controller.set_camera_orientation("rgb_front", 
                                             pitch=self.current_pitch, 
                                             yaw=self.current_yaw)
        print(f"Camera preset: Pitch={self.current_pitch}°, Yaw={self.current_yaw}°")
    
    def update_display(self):
        """Update the RGB display."""
        if not self.running:
            return
            
        image = self.get_image()
        if image is not None:
            # Image is already in RGB format - perfect for PIL
            
            # Resize to fit window
            img_h, img_w = image.shape[:2]
            win_w, win_h = self.window_size
            
            # Calculate scaling
            scale = min(win_w / img_w, win_h / img_h)
            new_w = int(img_w * scale)
            new_h = int(img_h * scale)
            
            # Convert numpy array to PIL Image (RGB format maintained)
            pil_image = Image.fromarray(image, 'RGB')
            pil_image = pil_image.resize((new_w, new_h), Image.LANCZOS)
            
            # Convert to tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.image_label.configure(image=tk_image)
            self.image_label.image = tk_image  # Keep reference
            
            # Update info
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            info_text = (f"RGB Format - Detectnet Compatible | "
                        f"FPS: {fps:.1f} | "
                        f"Pitch: {self.current_pitch}° Yaw: {self.current_yaw}°")
            self.info_label.configure(text=info_text)
        
        # Schedule next update
        if self.running:
            self.root.after(33, self.update_display)  # ~30 FPS
    
    def save_frame(self):
        """Save current frame in RGB format."""
        image = self.get_image()
        if image is not None:
            timestamp = int(time.time())
            filename = f"simple_rgb_frame_{self.controller.drone_name}_{timestamp}.png"
            
            # Use imageio to save RGB format
            imageio.imwrite(filename, image)
            print(f"RGB frame saved: {filename}")
            
            # Show success in GUI
            self.info_label.configure(text=f"Frame saved: {filename}")
            self.root.after(2000, lambda: self.info_label.configure(
                text=f"RGB Format - Detectnet Compatible"))
    
    def start_viewer(self):
        """Start the simple RGB viewer."""
        print(f"Starting simple RGB viewer for {self.controller.drone_name}")
        print("RGB format maintained throughout - perfect for detectnet!")
        print("Use GUI buttons to control camera")
        
        self.running = True
        self.update_display()
        self.root.mainloop()
    
    def stop_viewer(self):
        """Stop the viewer."""
        self.running = False
        self.root.quit()
        self.root.destroy()

def quick_simple_view(drone_name="Drone1", camera_type="rgb"):
    """Quick simple RGB camera view."""
    
    print(f"=== Simple RGB Camera Viewer ===")
    print(f"Drone: {drone_name}, Camera: {camera_type}")
    print("RGB format maintained - detectnet compatible")
    print("Lightweight GUI with camera controls")
    print()
    
    try:
        controller = SimpleRGBController(drone_name)
        viewer = SimpleRGBViewer(controller, camera_type, window_size=(800, 600))
        viewer.start_viewer()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AirSim is running!")

if __name__ == "__main__":
    print("Simple RGB Camera Viewer")
    print("Uses PIL + tkinter - lighter than matplotlib")
    print()
    
    quick_simple_view() 