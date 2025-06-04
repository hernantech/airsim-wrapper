import airsim
import numpy as np
import time
import os
import cv2
import json
from datetime import datetime
from abc import ABC, abstractmethod
import threading
import queue

class BaseDroneController(ABC):
    """Base class for drone controllers with modular sensor interfaces."""
    
    def __init__(self, drone_name, data_dir="./data", communication_pipe=None):
        self.drone_name = drone_name
        self.data_dir = os.path.join(data_dir, drone_name)
        self.communication_pipe = communication_pipe
        
        # Create data directories
        self.rgb_dir = os.path.join(self.data_dir, "rgb_images")
        self.ir_dir = os.path.join(self.data_dir, "ir_images")
        self.lidar_dir = os.path.join(self.data_dir, "lidar_data")
        
        for dir_path in [self.rgb_dir, self.ir_dir, self.lidar_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Initialize AirSim client
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True, self.drone_name)
        self.client.armDisarm(True, self.drone_name)
        
        # Data collection variables
        self.telemetry_data = []
        self.sensor_data_queue = queue.Queue()
        self.running = False
        self.data_collection_thread = None
        self.timestep = 0
        
        # Communication variables
        self.message_queue = queue.Queue()
        self.comm_thread = None
        
        print(f"Initialized {self.drone_name} controller")
    
    def get_rgb_image(self):
        """Get RGB image from front camera."""
        responses = self.client.simGetImages([
            airsim.ImageRequest("rgb_front", airsim.ImageType.Scene, False, False)
        ], vehicle_name=self.drone_name)
        
        if responses:
            response = responses[0]
            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            img_rgb = img1d.reshape(response.height, response.width, 3)
            return img_rgb
        return None
    
    def get_ir_image(self):
        """Get IR image from front camera."""
        responses = self.client.simGetImages([
            airsim.ImageRequest("ir_front", airsim.ImageType.Infrared, False, False)
        ], vehicle_name=self.drone_name)
        
        if responses:
            response = responses[0]
            img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
            img_ir = img1d.reshape(response.height, response.width, 3)
            return img_ir
        return None
    
    def get_lidar_data(self):
        """Get LiDAR point cloud data."""
        lidar_data = self.client.getLidarData("lidar_front", vehicle_name=self.drone_name)
        if lidar_data:
            points = np.array(lidar_data.point_cloud, dtype=np.dtype('f4'))
            points = np.reshape(points, (int(points.shape[0]/3), 3))
            return points
        return None
    
    def get_telemetry(self):
        """Get current telemetry data."""
        state = self.client.getMultirotorState(vehicle_name=self.drone_name)
        gps = self.client.getGpsData(gps_name="gps", vehicle_name=self.drone_name)
        imu = self.client.getImuData(imu_name="imu", vehicle_name=self.drone_name)
        
        telemetry = {
            "timestamp": time.time(),
            "timestep": self.timestep,
            "position": {
                "x": state.kinematics_estimated.position.x_val,
                "y": state.kinematics_estimated.position.y_val,
                "z": state.kinematics_estimated.position.z_val
            },
            "velocity": {
                "x": state.kinematics_estimated.linear_velocity.x_val,
                "y": state.kinematics_estimated.linear_velocity.y_val,
                "z": state.kinematics_estimated.linear_velocity.z_val
            },
            "orientation": {
                "pitch": state.kinematics_estimated.orientation.pitch,
                "roll": state.kinematics_estimated.orientation.roll,
                "yaw": state.kinematics_estimated.orientation.yaw
            },
            "gps": {
                "lat": gps.gnss.geo_point.latitude,
                "lon": gps.gnss.geo_point.longitude,
                "alt": gps.gnss.geo_point.altitude
            },
            "imu": {
                "angular_velocity": {
                    "x": imu.angular_velocity.x_val,
                    "y": imu.angular_velocity.y_val,
                    "z": imu.angular_velocity.z_val
                },
                "linear_acceleration": {
                    "x": imu.linear_acceleration.x_val,
                    "y": imu.linear_acceleration.y_val,
                    "z": imu.linear_acceleration.z_val
                }
            }
        }
        return telemetry
    
    def collect_sensor_data(self):
        """Collect all sensor data for current timestep."""
        sensor_data = {
            "timestep": self.timestep,
            "timestamp": time.time(),
            "rgb": self.get_rgb_image(),
            "ir": self.get_ir_image(),
            "lidar": self.get_lidar_data(),
            "telemetry": self.get_telemetry()
        }
        return sensor_data
    
    def save_sensor_data(self, sensor_data):
        """Save sensor data to disk."""
        timestep = sensor_data["timestep"]
        
        # Save RGB image
        if sensor_data["rgb"] is not None:
            cv2.imwrite(
                os.path.join(self.rgb_dir, f"rgb_{timestep:06d}.png"),
                cv2.cvtColor(sensor_data["rgb"], cv2.COLOR_RGB2BGR)
            )
        
        # Save IR image
        if sensor_data["ir"] is not None:
            cv2.imwrite(
                os.path.join(self.ir_dir, f"ir_{timestep:06d}.png"),
                sensor_data["ir"]
            )
        
        # Save LiDAR data
        if sensor_data["lidar"] is not None:
            np.save(
                os.path.join(self.lidar_dir, f"lidar_{timestep:06d}.npy"),
                sensor_data["lidar"]
            )
        
        # Add telemetry to list (will be saved as CSV later)
        self.telemetry_data.append(sensor_data["telemetry"])
    
    def data_collection_loop(self):
        """Background thread for data collection."""
        while self.running:
            try:
                # Get sensor data from queue (with timeout)
                sensor_data = self.sensor_data_queue.get(timeout=0.1)
                self.save_sensor_data(sensor_data)
            except queue.Empty:
                continue
    
    def send_message(self, recipient, message):
        """Send message to another drone (mock LoRa communication)."""
        if self.communication_pipe:
            msg_packet = {
                "timestamp": time.time(),
                "sender": self.drone_name,
                "recipient": recipient,
                "payload": message
            }
            self.communication_pipe.send(json.dumps(msg_packet))
    
    def receive_messages(self):
        """Check for incoming messages."""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
    
    def communication_loop(self):
        """Background thread for handling communication."""
        while self.running and self.communication_pipe:
            try:
                if self.communication_pipe.poll(timeout=0.1):
                    msg = self.communication_pipe.recv()
                    msg_packet = json.loads(msg)
                    if msg_packet["recipient"] == self.drone_name:
                        self.message_queue.put(msg_packet)
            except Exception as e:
                print(f"Communication error: {e}")
    
    @abstractmethod
    def compute_control(self, sensor_data, messages):
        """
        Compute control commands based on sensor data and messages.
        Must be implemented by subclasses.
        
        Args:
            sensor_data: Dictionary containing all sensor readings
            messages: List of received messages from other drones
            
        Returns:
            Dictionary containing control commands
        """
        pass
    
    def control_loop(self):
        """Main control loop."""
        self.running = True
        
        # Start background threads
        self.data_collection_thread = threading.Thread(target=self.data_collection_loop)
        self.data_collection_thread.start()
        
        if self.communication_pipe:
            self.comm_thread = threading.Thread(target=self.communication_loop)
            self.comm_thread.start()
        
        try:
            while self.running:
                # Collect sensor data
                sensor_data = self.collect_sensor_data()
                
                # Queue data for saving
                self.sensor_data_queue.put(sensor_data)
                
                # Get messages
                messages = self.receive_messages()
                
                # Compute control
                control_commands = self.compute_control(sensor_data, messages)
                
                # Execute control commands
                if control_commands:
                    self.execute_control(control_commands)
                
                # Increment timestep
                self.timestep += 1
                
                # Sleep to maintain desired update rate (10 Hz)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\n{self.drone_name}: Stopping controller...")
        finally:
            self.cleanup()
    
    def execute_control(self, control_commands):
        """Execute control commands."""
        if "velocity" in control_commands:
            vel = control_commands["velocity"]
            self.client.moveByVelocityAsync(
                vel["x"], vel["y"], vel["z"], 
                duration=0.1,
                vehicle_name=self.drone_name
            )
        elif "position" in control_commands:
            pos = control_commands["position"]
            self.client.moveToPositionAsync(
                pos["x"], pos["y"], pos["z"],
                velocity=5,
                vehicle_name=self.drone_name
            )
    
    def cleanup(self):
        """Clean up and save data."""
        self.running = False
        
        # Wait for threads to finish
        if self.data_collection_thread:
            self.data_collection_thread.join()
        if self.comm_thread:
            self.comm_thread.join()
        
        # Save telemetry data as CSV
        if self.telemetry_data:
            import pandas as pd
            df = pd.json_normalize(self.telemetry_data)
            df.to_csv(os.path.join(self.data_dir, "telemetry.csv"), index=False)
        
        # Land and disarm
        self.client.landAsync(vehicle_name=self.drone_name).join()
        self.client.armDisarm(False, self.drone_name)
        self.client.enableApiControl(False, self.drone_name)
        
        print(f"{self.drone_name}: Controller stopped and data saved.")