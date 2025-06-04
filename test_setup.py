#!/usr/bin/env python3
"""
Test script to verify AirSim dual drone setup.
Run this before launching the full system to ensure everything is configured correctly.
"""

import airsim
import numpy as np
import time
import sys

def test_connection():
    """Test basic connection to AirSim."""
    print("Testing AirSim connection...")
    try:
        client = airsim.MultirotorClient()
        client.confirmConnection()
        print("✓ Successfully connected to AirSim")
        return client
    except Exception as e:
        print(f"✗ Failed to connect to AirSim: {e}")
        print("Make sure AirSim is running!")
        return None

def test_vehicles(client):
    """Test that both vehicles are available."""
    print("\nTesting vehicle availability...")
    vehicles = ["Drone1", "Drone2"]
    available = []
    
    for vehicle in vehicles:
        try:
            client.enableApiControl(True, vehicle)
            client.enableApiControl(False, vehicle)
            print(f"✓ {vehicle} is available")
            available.append(vehicle)
        except Exception as e:
            print(f"✗ {vehicle} not found: {e}")
    
    return available

def test_sensors(client, vehicle_name):
    """Test sensor availability for a vehicle."""
    print(f"\nTesting sensors for {vehicle_name}...")
    
    # Test cameras
    try:
        images = client.simGetImages([
            airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False),
            airsim.ImageRequest("ir_front", airsim.ImageType.Infrared, False, False)
        ], vehicle_name=vehicle_name)
        
        if len(images) == 2:
            print(f"✓ RGB camera: {images[0].width}x{images[0].height}")
            print(f"✓ IR camera: {images[1].width}x{images[1].height}")
        else:
            print("✗ Camera configuration error")
    except Exception as e:
        print(f"✗ Camera error: {e}")
    
    # Test LiDAR
    try:
        lidar_data = client.getLidarData("lidar_front", vehicle_name=vehicle_name)
        if lidar_data.point_cloud:
            points = np.array(lidar_data.point_cloud, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0]/3), 3))
            print(f"✓ LiDAR: {len(points)} points")
        else:
            print("✗ No LiDAR data")
    except Exception as e:
        print(f"✗ LiDAR error: {e}")
    
    # Test GPS
    try:
        gps = client.getGpsData("gps", vehicle_name=vehicle_name)
        print(f"✓ GPS: Lat={gps.gnss.geo_point.latitude:.6f}, "
              f"Lon={gps.gnss.geo_point.longitude:.6f}")
    except Exception as e:
        print(f"✗ GPS error: {e}")
    
    # Test IMU
    try:
        imu = client.getImuData("imu", vehicle_name=vehicle_name)
        print(f"✓ IMU: Available")
    except Exception as e:
        print(f"✗ IMU error: {e}")

def test_movement(client, vehicle_name):
    """Test basic movement capabilities."""
    print(f"\nTesting movement for {vehicle_name}...")
    
    try:
        # Enable control
        client.enableApiControl(True, vehicle_name)
        client.armDisarm(True, vehicle_name)
        
        # Take off
        print("  Taking off...")
        client.takeoffAsync(vehicle_name=vehicle_name).join()
        
        # Hover
        print("  Hovering for 2 seconds...")
        client.hoverAsync(vehicle_name=vehicle_name).join()
        time.sleep(2)
        
        # Small movement
        print("  Moving forward...")
        client.moveByVelocityAsync(1, 0, 0, 2, vehicle_name=vehicle_name).join()
        
        # Land
        print("  Landing...")
        client.landAsync(vehicle_name=vehicle_name).join()
        
        # Cleanup
        client.armDisarm(False, vehicle_name)
        client.enableApiControl(False, vehicle_name)
        
        print(f"✓ Movement test completed for {vehicle_name}")
        return True
        
    except Exception as e:
        print(f"✗ Movement test failed: {e}")
        # Try to clean up
        try:
            client.armDisarm(False, vehicle_name)
            client.enableApiControl(False, vehicle_name)
        except:
            pass
        return False

def main():
    """Run all tests."""
    print("=== AirSim Dual Drone Setup Test ===\n")
    
    # Test connection
    client = test_connection()
    if not client:
        sys.exit(1)
    
    # Test vehicles
    available_vehicles = test_vehicles(client)
    if len(available_vehicles) != 2:
        print("\n⚠ Warning: Not all vehicles are available!")
        print("Check your settings.json configuration.")
    
    # Test sensors for each available vehicle
    for vehicle in available_vehicles:
        test_sensors(client, vehicle)
    
    # Optional: Test movement
    print("\nWould you like to test drone movement? (y/n): ", end='')
    if input().lower() == 'y':
        for vehicle in available_vehicles:
            test_movement(client, vehicle)
            time.sleep(3)  # Wait between drones
    
    print("\n=== Test Complete ===")
    print(f"✓ {len(available_vehicles)}/2 drones configured")
    print("\nYou can now run: python launch_dual_drones.py")

if __name__ == "__main__":
    main()