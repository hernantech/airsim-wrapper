#!/usr/bin/env python3
"""
Debug PNG Save Process

This script traces exactly what happens when we save PNG files
to identify where colors might be getting inverted.
"""

import sys
import os
sys.path.append(".")

import numpy as np
import imageio
import cv2
from controllers.base_controller import BaseDroneController

class DebugController(BaseDroneController):
    def compute_control(self, sensor_data, messages):
        return {"action": "hover"}

def debug_png_save_process():
    """Debug the PNG saving process step by step."""
    
    print("=== PNG Save Debug Trace ===")
    print("Tracing the complete image pipeline from AirSim → PNG file")
    print()
    
    try:
        controller = DebugController("Drone1", "./debug_data")
        print("✓ Connected to Drone1")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return
    
    # Step 1: Get raw image from AirSim
    print("Step 1: Getting raw image from AirSim...")
    rgb_image = controller.get_rgb_image()
    
    if rgb_image is None:
        print("✗ Failed to get image from AirSim")
        return
    
    print(f"✓ Got image: shape={rgb_image.shape}, dtype={rgb_image.dtype}")
    
    # Step 2: Analyze a few key pixels
    print("\nStep 2: Analyzing key pixels...")
    h, w = rgb_image.shape[:2]
    
    # Sky pixel (usually upper portion)
    sky_pixel = rgb_image[h//4, w//2, :]
    print(f"Sky pixel (R,G,B): {sky_pixel}")
    
    # Center pixel
    center_pixel = rgb_image[h//2, w//2, :]
    print(f"Center pixel (R,G,B): {center_pixel}")
    
    # Ground pixel (usually lower portion)
    ground_pixel = rgb_image[3*h//4, w//2, :]
    print(f"Ground pixel (R,G,B): {ground_pixel}")
    
    # Step 3: Test different save methods
    print("\nStep 3: Testing different save methods...")
    
    # Method 1: imageio.imwrite (what we're using now)
    print("Method 1: imageio.imwrite (current approach)")
    imageio.imwrite("debug_imageio_save.png", rgb_image)
    
    # Method 2: cv2.imwrite with raw data (wrong - for comparison)
    print("Method 2: cv2.imwrite with raw RGB (wrong - for comparison)")
    cv2.imwrite("debug_cv2_raw.png", rgb_image)
    
    # Method 3: cv2.imwrite with BGR conversion (traditional way)
    print("Method 3: cv2.imwrite with BGR conversion")
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite("debug_cv2_bgr.png", bgr_image)
    
    # Step 4: Read back and compare
    print("\nStep 4: Reading back saved images and comparing...")
    
    # Read back with imageio (RGB)
    reloaded_imageio = imageio.imread("debug_imageio_save.png")
    print(f"imageio reloaded: shape={reloaded_imageio.shape}, dtype={reloaded_imageio.dtype}")
    
    # Read back with cv2 (BGR)
    reloaded_cv2 = cv2.imread("debug_imageio_save.png")  # This reads as BGR
    print(f"cv2 reloaded: shape={reloaded_cv2.shape}, dtype={reloaded_cv2.dtype}")
    
    # Step 5: Compare key pixels after save/reload
    print("\nStep 5: Comparing pixels after save/reload...")
    
    # Original vs imageio roundtrip
    orig_sky = sky_pixel
    reload_sky_imageio = reloaded_imageio[h//4, w//2, :]
    reload_sky_cv2 = reloaded_cv2[h//4, w//2, :]  # This will be BGR order
    
    print(f"Original sky pixel (RGB): {orig_sky}")
    print(f"imageio roundtrip (RGB): {reload_sky_imageio}")
    print(f"cv2 readback (BGR): {reload_sky_cv2}")
    
    # Check if imageio preserved the RGB values
    if np.array_equal(orig_sky, reload_sky_imageio):
        print("✓ imageio preserved RGB values perfectly")
    else:
        print("✗ imageio changed RGB values!")
        print(f"  Difference: {orig_sky - reload_sky_imageio}")
    
    # Check if CV2 reading shows BGR inversion
    if np.array_equal(orig_sky, reload_sky_cv2[::-1]):  # Reverse BGR to RGB
        print("✓ cv2 readback shows expected BGR order")
    else:
        print("? cv2 readback doesn't show simple BGR inversion")
    
    # Step 6: Let's check what AirSim ACTUALLY returns
    print("\nStep 6: Deep dive into AirSim image format...")
    
    # Get the raw response
    import airsim
    responses = controller.client.simGetImages([
        airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
    ], vehicle_name=controller.drone_name)
    
    if responses:
        response = responses[0]
        print(f"AirSim response:")
        print(f"  Width: {response.width}")
        print(f"  Height: {response.height}")
        print(f"  Pixels as float: {response.pixels_as_float}")
        print(f"  Compress: {response.compress}")
        
        if response.pixels_as_float:
            print("  Using float data")
            raw_data = np.array(response.image_data_float, dtype=np.float32)
        else:
            print("  Using uint8 data")
            raw_data = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        
        print(f"  Raw data shape: {raw_data.shape}")
        print(f"  Expected size: {response.height * response.width * 3}")
        
        # Check first few pixels in raw data
        if len(raw_data) >= 9:
            first_pixel_flat = raw_data[:3]
            second_pixel_flat = raw_data[3:6] 
            third_pixel_flat = raw_data[6:9]
            print(f"  First 3 pixels (flat): {first_pixel_flat}, {second_pixel_flat}, {third_pixel_flat}")
    
    # Step 7: Create a known test pattern
    print("\nStep 7: Testing with known color pattern...")
    
    # Create test image: red square, green square, blue square
    test_img = np.zeros((300, 300, 3), dtype=np.uint8)
    test_img[0:100, 0:100, :] = [255, 0, 0]    # Red square
    test_img[0:100, 100:200, :] = [0, 255, 0]  # Green square  
    test_img[0:100, 200:300, :] = [0, 0, 255]  # Blue square
    
    print("Created test pattern: Red, Green, Blue squares")
    
    # Save with imageio
    imageio.imwrite("debug_test_pattern_imageio.png", test_img)
    
    # Save with cv2 + BGR conversion
    test_bgr = cv2.cvtColor(test_img, cv2.COLOR_RGB2BGR)
    cv2.imwrite("debug_test_pattern_cv2.png", test_bgr)
    
    # Read back and check
    reloaded_test = imageio.imread("debug_test_pattern_imageio.png")
    
    red_check = reloaded_test[50, 50, :]    # Should be [255, 0, 0]
    green_check = reloaded_test[50, 150, :] # Should be [0, 255, 0]
    blue_check = reloaded_test[50, 250, :]  # Should be [0, 0, 255]
    
    print(f"Test pattern readback:")
    print(f"  Red square: {red_check} (should be [255, 0, 0])")
    print(f"  Green square: {green_check} (should be [0, 255, 0])")
    print(f"  Blue square: {blue_check} (should be [0, 0, 255])")
    
    # Final analysis
    print("\n=== ANALYSIS ===")
    if np.array_equal(red_check, [255, 0, 0]) and np.array_equal(green_check, [0, 255, 0]) and np.array_equal(blue_check, [0, 0, 255]):
        print("✓ imageio is saving/loading RGB correctly")
        print("✓ The PNG save process preserves RGB format")
        print("→ If colors still look wrong, the issue is elsewhere in the pipeline")
    else:
        print("✗ imageio is NOT preserving RGB format correctly!")
        print("→ This is the source of the color inversion")
    
    print("\nDebug files created:")
    print("  - debug_imageio_save.png (AirSim image via imageio)")
    print("  - debug_cv2_raw.png (AirSim image via cv2 raw - should look wrong)")  
    print("  - debug_cv2_bgr.png (AirSim image via cv2 with BGR conversion)")
    print("  - debug_test_pattern_imageio.png (RGB test pattern)")
    print("  - debug_test_pattern_cv2.png (BGR test pattern)")
    
    # Cleanup
    controller.cleanup()

if __name__ == "__main__":
    debug_png_save_process() 