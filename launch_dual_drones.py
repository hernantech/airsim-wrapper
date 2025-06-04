#!/usr/bin/env python3
"""
Launch script for dual drone system with communication.
This script starts both drone controllers in separate processes.
"""

import multiprocessing
import time
import signal
import sys
import os
from communication_bridge import CommunicationBridge, MockLoRaTransceiver
from sample_controller import SampleDroneController

def run_drone_controller(drone_name, pipe_connection, data_dir):
    """Run a single drone controller in its own process."""
    try:
        # Create mock LoRa transceiver
        transceiver = MockLoRaTransceiver(drone_name, pipe_connection)
        
        # Create and run controller
        controller = SampleDroneController(
            drone_name=drone_name,
            data_dir=data_dir,
            communication_pipe=transceiver,
            target_altitude=-10.0,
            safe_distance=5.0
        )
        
        # Start control loop
        controller.control_loop()
        
    except Exception as e:
        print(f"Error in {drone_name}: {e}")
        raise

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down dual drone system...")
    sys.exit(0)

def main():
    """Main function to launch dual drone system."""
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Configuration
    drone_names = ["Drone1", "Drone2"]
    data_dir = "./simulation_data"
    
    # Create data directory
    os.makedirs(data_dir, exist_ok=True)
    
    print("=== AirSim Dual Drone System ===")
    print("Starting communication bridge and drone controllers...")
    
    # Create communication bridge
    comm_bridge = CommunicationBridge(drone_names, log_messages=True)
    
    # Start communication bridge
    comm_bridge.start_bridge()
    time.sleep(1)  # Give bridge time to start
    
    # Create processes for each drone
    processes = []
    for drone_name in drone_names:
        pipe = comm_bridge.get_drone_pipe(drone_name)
        process = multiprocessing.Process(
            target=run_drone_controller,
            args=(drone_name, pipe, data_dir)
        )
        processes.append(process)
        process.start()
        print(f"Started {drone_name} controller")
        time.sleep(2)  # Stagger drone startups
    
    print("\nAll drones launched! Press Ctrl+C to stop.")
    print("Data will be saved to:", os.path.abspath(data_dir))
    
    try:
        # Wait for all processes
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up
        comm_bridge.stop_bridge()
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()