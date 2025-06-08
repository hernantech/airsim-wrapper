#!/usr/bin/env python3
"""
Simple test to debug AirSim connection and create minimal RGB viewer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import airsim
import numpy as np
import cv2
import time
import imageio

def test_airsim_connection():
    """Test basic AirSim connection."""
    print("Testing AirSim connection...")
    
    try:
        client = airsim.MultirotorClient()
        client.confirmConnection()
        print("✓ Connected to AirSim")
        
        # Test getting an image
        responses = client.simGetImages([
            airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
        ], vehicle_name="Drone1")
        
        if responses:
            response = responses[0]
            print(f"✓ Got image: {response.width}x{response.height}")
            
            # Convert to RGB array
            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            img_rgb = img1d.reshape(response.height, response.width, 3)
            print(f"✓ Image shape: {img_rgb.shape}")
            print(f"✓ Sample pixel: {img_rgb[0, 0, :]}")
            
            return client, img_rgb
        else:
            print("✗ No image received")
            return None, None
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None, None

def minimal_rgb_viewer():
    """Minimal RGB viewer using OpenCV (but maintaining RGB data)."""
    
    print("=== Minimal RGB Viewer ===")
    print("This will display using OpenCV but maintain RGB data internally")
    
    client, test_image = test_airsim_connection()
    if client is None:
        return
    
    print("\nStarting minimal viewer...")
    print("Press 'q' to quit, 's' to save RGB frame")
    
    frame_count = 0
    
    try:
        while True:
            # Get RGB image from AirSim
            responses = client.simGetImages([
                airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
            ], vehicle_name="Drone1")
            
            if responses:
                response = responses[0]
                img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
                rgb_image = img1d.reshape(response.height, response.width, 3).copy()  # Make writable copy
                
                # Display RGB data directly - NO CONVERSION
                # Add overlay info
                cv2.putText(rgb_image, "RGB Data (No Conversion)", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(rgb_image, f"Frame: {frame_count}", (10, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(rgb_image, "Press 's' to save RGB frame", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow("RGB Camera (Direct Display)", rgb_image)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save the RGB data in correct RGB format for detectnet
                    timestamp = int(time.time())
                    filename = f"rgb_frame_{timestamp}.png"
                    # Use imageio.imwrite to maintain RGB format (per COLOR_FORMAT_GUIDE.md)
                    imageio.imwrite(filename, rgb_image)
                    print(f"RGB frame saved (detectnet compatible): {filename}")
                
                frame_count += 1
            
            else:
                print("No image received")
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nViewer interrupted")
    finally:
        cv2.destroyAllWindows()

def test_camera_control():
    """Test camera control without complex viewer."""
    
    print("=== Camera Control Test ===")
    
    client, _ = test_airsim_connection()
    if client is None:
        return
    
    try:
        print("Testing camera orientation...")
        
        # Test different angles
        angles = [
            (0, 0, "Forward"),
            (45, 0, "45° Down"),
            (90, 0, "Straight Down"),
            (0, 90, "Right Side"),
            (0, 0, "Reset Forward")
        ]
        
        for pitch, yaw, description in angles:
            print(f"Setting camera: {description} (pitch={pitch}°, yaw={yaw}°)")
            
            # Set camera orientation
            pitch_rad = np.radians(pitch)
            roll_rad = np.radians(0)
            yaw_rad = np.radians(yaw)
            
            orientation = airsim.to_quaternion(pitch_rad, roll_rad, yaw_rad)
            camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), orientation)
            
            client.simSetCameraPose("rgb_front", camera_pose, vehicle_name="Drone1")
            
            time.sleep(2)  # Wait to see change
            
            # Capture test image
            responses = client.simGetImages([
                airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
            ], vehicle_name="Drone1")
            
            if responses:
                print(f"✓ Captured image at {description}")
            else:
                print(f"✗ Failed to capture at {description}")
        
        print("Camera control test complete!")
        
    except Exception as e:
        print(f"Camera control error: {e}")

if __name__ == "__main__":
    print("Simple RGB Viewer Test")
    print("1. Test AirSim connection")
    print("2. Minimal RGB viewer") 
    print("3. Test camera control")
    
    choice = input("Select option (1-3): ").strip()
    
    if choice == "1":
        test_airsim_connection()
    elif choice == "2":
        minimal_rgb_viewer()
    elif choice == "3":
        test_camera_control()
    else:
        print("Invalid choice") 