from base_controller import BaseDroneController
import numpy as np

class SampleDroneController(BaseDroneController):
    """Sample implementation of a drone controller with basic obstacle avoidance."""
    
    def __init__(self, drone_name, data_dir="./data", communication_pipe=None, 
                 target_altitude=-10, safe_distance=5.0):
        super().__init__(drone_name, data_dir, communication_pipe)
        self.target_altitude = target_altitude
        self.safe_distance = safe_distance
        self.other_drone_position = None
        self.mode = "hover"  # modes: hover, explore, avoid
        
    def compute_control(self, sensor_data, messages):
        """
        Compute control based on sensor data and messages.
        This is a simple example that maintains altitude and avoids obstacles.
        """
        control_commands = {}
        
        # Process messages from other drone
        for msg in messages:
            if msg["payload"].get("type") == "position_update":
                self.other_drone_position = msg["payload"]["position"]
        
        # Get current position
        current_pos = sensor_data["telemetry"]["position"]
        
        # Basic altitude control
        altitude_error = self.target_altitude - current_pos["z"]
        vz = np.clip(altitude_error * 0.5, -2, 2)  # P-controller with limits
        
        # Initialize velocities
        vx, vy = 0, 0
        
        # Process LiDAR for obstacle avoidance
        if sensor_data["lidar"] is not None:
            points = sensor_data["lidar"]
            if len(points) > 0:
                # Find closest point in front
                front_points = points[points[:, 0] > 0]  # Points in front
                if len(front_points) > 0:
                    distances = np.linalg.norm(front_points, axis=1)
                    min_distance = np.min(distances)
                    
                    if min_distance < self.safe_distance:
                        self.mode = "avoid"
                        # Simple avoidance: move backward and to the side
                        vx = -1.0
                        vy = 1.0 if self.drone_name == "Drone1" else -1.0
                    else:
                        self.mode = "explore"
        
        # Check distance to other drone if we know its position
        if self.other_drone_position:
            dx = self.other_drone_position["x"] - current_pos["x"]
            dy = self.other_drone_position["y"] - current_pos["y"]
            dz = self.other_drone_position["z"] - current_pos["z"]
            distance_to_other = np.sqrt(dx**2 + dy**2 + dz**2)
            
            if distance_to_other < self.safe_distance * 1.5:
                # Avoid other drone
                self.mode = "avoid"
                avoid_vector_x = -dx / distance_to_other
                avoid_vector_y = -dy / distance_to_other
                vx = avoid_vector_x * 2.0
                vy = avoid_vector_y * 2.0
        
        # If not avoiding, do simple exploration
        if self.mode == "explore":
            # Simple pattern: move in expanding square
            t = self.timestep * 0.1
            pattern_size = 10 + t * 0.1
            vx = np.cos(t) * 0.5
            vy = np.sin(t) * 0.5
        
        # Send position update to other drone
        if self.timestep % 10 == 0:  # Every 10 timesteps
            self.send_message(
                "Drone2" if self.drone_name == "Drone1" else "Drone1",
                {
                    "type": "position_update",
                    "position": current_pos,
                    "mode": self.mode
                }
            )
        
        # Apply velocity limits
        vx = np.clip(vx, -3, 3)
        vy = np.clip(vy, -3, 3)
        vz = np.clip(vz, -2, 2)
        
        control_commands["velocity"] = {
            "x": vx,
            "y": vy,
            "z": vz
        }
        
        # Print status every 50 timesteps
        if self.timestep % 50 == 0:
            print(f"{self.drone_name} - Mode: {self.mode}, Pos: ({current_pos['x']:.1f}, "
                  f"{current_pos['y']:.1f}, {current_pos['z']:.1f}), "
                  f"Vel: ({vx:.1f}, {vy:.1f}, {vz:.1f})")
        
        return control_commands