#!/usr/bin/env python3
"""
Color Format Fix Test

This script tests the color format fixes in the camera display utilities
according to the COLOR_FORMAT_GUIDE.md recommendations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
import time
from controllers.base_controller import BaseDroneController
from utils.camera_display import add_camera_display_to_controller, quick_camera_view

class ColorTestController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

def test_color_formats():
    """Test that color formats are handled correctly."""
    
    print("=== Color Format Fix Test ===")
    print("Based on COLOR_FORMAT_GUIDE.md:")
    print("- AirSim returns RGB data")
    print("- OpenCV display expects BGR data")
    print("- This test verifies the conversion is working correctly")
    print()
    
    try:
        controller = ColorTestController("Drone1")
        print("✓ Connected to Drone1")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        print("Make sure AirSim is running!")
        return False
    
    # Test 1: Direct image format check
    print("\n--- Test 1: Image Format Analysis ---")
    rgb_image = controller.get_rgb_image()
    if rgb_image is not None:
        print(f"✓ RGB image captured: {rgb_image.shape}")
        
        # Check a few pixels for color analysis
        h, w = rgb_image.shape[:2]
        center_pixel = rgb_image[h//2, w//2, :]
        print(f"Center pixel RGB values: {center_pixel}")
        
        # Look for sky pixel (should have high blue component in RGB)
        top_pixel = rgb_image[h//4, w//2, :]
        print(f"Sky pixel RGB values: {top_pixel}")
        
        # Check if this looks like realistic sky color (high blue in RGB)
        if top_pixel[2] > top_pixel[0] and top_pixel[2] > top_pixel[1]:
            print("✓ Sky pixel has high blue component (looks correct for RGB)")
        else:
            print("⚠ Sky pixel doesn't have expected high blue (may indicate color issue)")
    else:
        print("✗ Could not capture RGB image")
        return False
    
    # Test 2: Display format test
    print("\n--- Test 2: Display Format Test ---")
    print("Testing camera display with color conversion...")
    
    # Set camera to point at sky for better color testing
    controller.set_camera_orientation("rgb_front", pitch=-45, yaw=0)  # Look up at sky
    time.sleep(1)  # Wait for camera to move
    
    print("Camera pointed up at sky for color testing")
    print("The sky should appear BLUE in the display window")
    print("If it appears ORANGE/RED, there's a color format issue")
    
    # Test the camera display
    display = add_camera_display_to_controller(controller, "rgb")
    print("\nStarting display test for 10 seconds...")
    print("Observe if the sky appears blue (correct) or orange/red (incorrect)")
    
    display.start_display(show_info=True, fps_limit=30)
    time.sleep(10)
    display.stop_display()
    
    # Test 3: Save and verify test
    print("\n--- Test 3: Save and Reload Test ---")
    
    # Capture current image
    test_image = controller.get_rgb_image()
    if test_image is not None:
        # Save in RGB format (as per COLOR_FORMAT_GUIDE.md)
        import imageio
        imageio.imwrite("color_test_rgb_format.png", test_image)  # Save raw RGB
        
        # Save in BGR format for comparison
        bgr_image = cv2.cvtColor(test_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite("color_test_bgr_format.png", bgr_image)
        
        print("✓ Saved test images:")
        print("  - color_test_rgb_format.png (raw RGB from AirSim)")
        print("  - color_test_bgr_format.png (converted to BGR)")
        
        # Read back and check
        reloaded_bgr = cv2.imread("color_test_bgr_format.png")  # OpenCV reads as BGR
        if reloaded_bgr is not None:
            print("✓ Successfully reloaded BGR test image")
            
            # Display the reloaded image briefly
            cv2.namedWindow("Reloaded BGR Test", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Reloaded BGR Test", 400, 300)
            cv2.imshow("Reloaded BGR Test", reloaded_bgr)
            print("Showing reloaded BGR image - sky should be blue")
            cv2.waitKey(3000)  # Show for 3 seconds
            cv2.destroyWindow("Reloaded BGR Test")
        else:
            print("✗ Failed to reload BGR test image")
    
    # Reset camera
    controller.set_camera_orientation("rgb_front", pitch=0, yaw=0)
    print("\n✓ Camera reset to forward view")
    
    print("\n=== Test Summary ===")
    print("1. Check console output for pixel analysis")
    print("2. Verify sky appeared BLUE in display window (not orange/red)")
    print("3. Check saved test images for correct colors")
    print()
    print("If sky appeared blue in all tests: ✓ Color format fix is working")
    print("If sky appeared orange/red: ✗ Color format issue still exists")
    
    return True

def quick_visual_test():
    """Quick visual test to check colors."""
    print("\n=== Quick Visual Test ===")
    print("This will show RGB camera feed for 15 seconds")
    print("Look for these indicators of correct color:")
    print("- Sky should be BLUE")
    print("- Grass/vegetation should be GREEN") 
    print("- Any red objects should appear RED")
    print()
    
    try:
        controller = ColorTestController("Drone1")
        print("Starting 15-second visual test...")
        quick_camera_view(controller, "rgb", duration=15)
        print("Visual test complete")
    except Exception as e:
        print(f"Visual test failed: {e}")

if __name__ == "__main__":
    print("Color Format Test Options:")
    print("1. Full color format test")
    print("2. Quick visual test")
    
    choice = input("Select option (1 or 2): ").strip()
    
    if choice == "1":
        test_color_formats()
    elif choice == "2":
        quick_visual_test()
    else:
        print("Invalid choice") 