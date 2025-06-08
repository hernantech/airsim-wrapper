#!/usr/bin/env python3
"""
Fast RGB-Native Camera Viewer using pygame

Much faster than matplotlib for real-time camera viewing.
Maintains RGB format throughout for detectnet compatibility.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
import pygame
import imageio
from controllers.base_controller import BaseDroneController

class FastRGBController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

class FastRGBViewer:
    """Fast RGB-native camera viewer using pygame."""
    
    def __init__(self, controller, camera_type="rgb", window_size=(800, 600)):
        self.controller = controller
        self.camera_type = camera_type
        self.window_size = window_size
        self.running = False
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption(f"{controller.drone_name} - {camera_type.upper()} Camera (RGB)")
        
        # Font for overlay text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_time = time.time()
        self.fps = 0
        
    def get_image(self):
        """Get RGB image maintaining RGB format."""
        if self.camera_type == "rgb":
            return self.controller.get_rgb_image()
        elif self.camera_type == "ir":
            return self.controller.get_ir_image()
        return None
    
    def start_viewer(self, show_info=True, target_fps=30):
        """Start the fast RGB viewer."""
        print(f"Starting fast RGB viewer for {self.controller.drone_name}")
        print("RGB format maintained throughout - perfect for detectnet!")
        print("Press ESC to quit, S to save frame, C to change camera angle")
        
        self.running = True
        clock = pygame.time.Clock()
        
        # Camera control state
        current_pitch = 0
        current_yaw = 0
        
        try:
            while self.running:
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_s:
                            self.save_frame()
                        elif event.key == pygame.K_w:  # Pitch up
                            current_pitch = max(-90, current_pitch - 15)
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print(f"Pitch: {current_pitch}°")
                        elif event.key == pygame.K_s:  # Pitch down
                            current_pitch = min(90, current_pitch + 15)
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print(f"Pitch: {current_pitch}°")
                        elif event.key == pygame.K_a:  # Yaw left
                            current_yaw = (current_yaw - 30) % 360
                            if current_yaw > 180:
                                current_yaw -= 360
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print(f"Yaw: {current_yaw}°")
                        elif event.key == pygame.K_d:  # Yaw right
                            current_yaw = (current_yaw + 30) % 360
                            if current_yaw > 180:
                                current_yaw -= 360
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print(f"Yaw: {current_yaw}°")
                        elif event.key == pygame.K_f:  # Forward
                            current_pitch, current_yaw = 0, 0
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print("Forward view")
                        elif event.key == pygame.K_DOWN:  # Downward view
                            current_pitch, current_yaw = 90, 0
                            self.controller.set_camera_orientation("rgb_front", pitch=current_pitch, yaw=current_yaw)
                            print("Downward view")
                
                # Get and display image
                image = self.get_image()
                if image is not None:
                    self.display_image(image, show_info, current_pitch, current_yaw)
                
                # Control frame rate
                clock.tick(target_fps)
                
        except KeyboardInterrupt:
            print("\nViewer interrupted")
        finally:
            self.stop_viewer()
    
    def display_image(self, image, show_info=True, pitch=0, yaw=0):
        """Display RGB image with pygame."""
        # Image is already in RGB format - perfect for pygame
        
        # Resize image to fit window while maintaining aspect ratio
        img_h, img_w = image.shape[:2]
        win_w, win_h = self.window_size
        
        # Calculate scaling to fit window
        scale_w = win_w / img_w
        scale_h = win_h / img_h
        scale = min(scale_w, scale_h)
        
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # Resize image using numpy (simple nearest neighbor)
        if scale != 1.0:
            # Simple resize by selecting pixels
            resized = np.zeros((new_h, new_w, 3), dtype=np.uint8)
            for y in range(new_h):
                for x in range(new_w):
                    orig_y = int(y / scale)
                    orig_x = int(x / scale)
                    if orig_y < img_h and orig_x < img_w:
                        resized[y, x] = image[orig_y, orig_x]
            image = resized
        
        # Convert to pygame surface (RGB native!)
        # pygame.surfarray.make_surface expects (width, height, 3) but numpy is (height, width, 3)
        image_swapped = np.swapaxes(image, 0, 1)  # Swap height/width for pygame
        surface = pygame.surfarray.make_surface(image_swapped)
        
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Center image on screen
        x_offset = (win_w - new_w) // 2
        y_offset = (win_h - new_h) // 2
        self.screen.blit(surface, (x_offset, y_offset))
        
        # Add info overlay
        if show_info:
            self.frame_count += 1
            current_time = time.time()
            
            # Calculate FPS
            if current_time - self.last_fps_time >= 1.0:
                self.fps = self.frame_count / (current_time - self.start_time)
                self.last_fps_time = current_time
            
            # Create info text
            info_lines = [
                f"RGB Format - Detectnet Compatible",
                f"FPS: {self.fps:.1f}",
                f"Pitch: {pitch:.1f}°  Yaw: {yaw:.1f}°",
                f"Controls: WASD=camera, F=forward, ↓=down, S=save, ESC=quit"
            ]
            
            # Render text with background
            y_pos = 10
            for line in info_lines:
                if "Controls" in line:
                    text = self.small_font.render(line, True, (255, 255, 255))
                else:
                    text = self.font.render(line, True, (0, 255, 0))
                
                # Add semi-transparent background
                text_rect = text.get_rect()
                text_rect.x = 10
                text_rect.y = y_pos
                
                bg_rect = pygame.Rect(text_rect.x - 5, text_rect.y - 2, 
                                    text_rect.width + 10, text_rect.height + 4)
                
                # Create semi-transparent surface
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
                bg_surface.set_alpha(128)
                bg_surface.fill((0, 0, 0))
                
                self.screen.blit(bg_surface, bg_rect)
                self.screen.blit(text, text_rect)
                
                y_pos += text_rect.height + 5
        
        # Update display
        pygame.display.flip()
    
    def save_frame(self):
        """Save current frame in RGB format."""
        image = self.get_image()
        if image is not None:
            timestamp = int(time.time())
            filename = f"fast_rgb_frame_{self.controller.drone_name}_{timestamp}.png"
            
            # Use imageio to save RGB format
            imageio.imwrite(filename, image)
            print(f"RGB frame saved: {filename}")
            return filename
        return None
    
    def stop_viewer(self):
        """Stop the viewer."""
        self.running = False
        pygame.quit()

def quick_fast_view(drone_name="Drone1", camera_type="rgb", duration=30):
    """Quick fast RGB camera view."""
    
    print(f"=== Fast RGB Camera Viewer ===")
    print(f"Drone: {drone_name}, Camera: {camera_type}")
    print("RGB format maintained - detectnet compatible")
    print("Much faster than matplotlib!")
    print()
    
    try:
        controller = FastRGBController(drone_name)
        viewer = FastRGBViewer(controller, camera_type, window_size=(1024, 768))
        
        # Run for specified duration
        import threading
        def stop_after_duration():
            time.sleep(duration)
            viewer.running = False
        
        timer_thread = threading.Thread(target=stop_after_duration, daemon=True)
        timer_thread.start()
        
        viewer.start_viewer(show_info=True, target_fps=30)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure AirSim is running!")

if __name__ == "__main__":
    print("Fast RGB Camera Viewer")
    print("Uses pygame for much faster display than matplotlib")
    print()
    
    print("Options:")
    print("1. Quick view (30 seconds)")
    print("2. Interactive view (unlimited)")
    print("3. Custom duration")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        quick_fast_view()
    elif choice == "2":
        try:
            controller = FastRGBController("Drone1") 
            viewer = FastRGBViewer(controller, "rgb", window_size=(1024, 768))
            viewer.start_viewer(show_info=True, target_fps=30)
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "3":
        try:
            duration = int(input("Duration (seconds): "))
            quick_fast_view(duration=duration)
        except ValueError:
            print("Invalid duration")
    else:
        print("Invalid choice") 