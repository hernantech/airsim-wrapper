#!/usr/bin/env python3
"""
Utility script to visualize collected drone data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from mpl_toolkits.mplot3d import Axes3D

class DroneDataVisualizer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        
    def plot_trajectories(self):
        """Plot 3D trajectories of both drones."""
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        colors = ['blue', 'red']
        drone_names = ['Drone1', 'Drone2']
        
        for i, drone_name in enumerate(drone_names):
            telemetry_file = os.path.join(self.data_dir, drone_name, 'telemetry.csv')
            if os.path.exists(telemetry_file):
                df = pd.read_csv(telemetry_file)
                ax.plot(df['position.x'], df['position.y'], df['position.z'], 
                       color=colors[i], label=drone_name, linewidth=2)
                
                # Mark start and end
                ax.scatter(df['position.x'].iloc[0], df['position.y'].iloc[0], 
                          df['position.z'].iloc[0], color=colors[i], s=100, marker='o')
                ax.scatter(df['position.x'].iloc[-1], df['position.y'].iloc[-1], 
                          df['position.z'].iloc[-1], color=colors[i], s=100, marker='x')
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Drone Trajectories')
        ax.legend()
        plt.show()
    
    def plot_telemetry_timeseries(self, drone_name):
        """Plot telemetry time series for a specific drone."""
        telemetry_file = os.path.join(self.data_dir, drone_name, 'telemetry.csv')
        if not os.path.exists(telemetry_file):
            print(f"No telemetry data found for {drone_name}")
            return
        
        df = pd.read_csv(telemetry_file)
        
        fig, axes = plt.subplots(3, 2, figsize=(12, 10))
        fig.suptitle(f'{drone_name} Telemetry Data', fontsize=16)
        
        # Position
        axes[0, 0].plot(df['timestep'], df['position.x'], label='X')
        axes[0, 0].plot(df['timestep'], df['position.y'], label='Y')
        axes[0, 0].plot(df['timestep'], df['position.z'], label='Z')
        axes[0, 0].set_title('Position')
        axes[0, 0].set_ylabel('Position (m)')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Velocity
        axes[0, 1].plot(df['timestep'], df['velocity.x'], label='Vx')
        axes[0, 1].plot(df['timestep'], df['velocity.y'], label='Vy')
        axes[0, 1].plot(df['timestep'], df['velocity.z'], label='Vz')
        axes[0, 1].set_title('Velocity')
        axes[0, 1].set_ylabel('Velocity (m/s)')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Orientation
        axes[1, 0].plot(df['timestep'], df['orientation.pitch'], label='Pitch')
        axes[1, 0].plot(df['timestep'], df['orientation.roll'], label='Roll')
        axes[1, 0].plot(df['timestep'], df['orientation.yaw'], label='Yaw')
        axes[1, 0].set_title('Orientation')
        axes[1, 0].set_ylabel('Angle (rad)')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # GPS
        axes[1, 1].plot(df['timestep'], df['gps.alt'], label='Altitude')
        axes[1, 1].set_title('GPS Altitude')
        axes[1, 1].set_ylabel('Altitude (m)')
        axes[1, 1].grid(True)
        
        # IMU Angular Velocity
        axes[2, 0].plot(df['timestep'], df['imu.angular_velocity.x'], label='ωx')
        axes[2, 0].plot(df['timestep'], df['imu.angular_velocity.y'], label='ωy')
        axes[2, 0].plot(df['timestep'], df['imu.angular_velocity.z'], label='ωz')
        axes[2, 0].set_title('Angular Velocity')
        axes[2, 0].set_ylabel('Angular Velocity (rad/s)')
        axes[2, 0].set_xlabel('Timestep')
        axes[2, 0].legend()
        axes[2, 0].grid(True)
        
        # IMU Linear Acceleration
        axes[2, 1].plot(df['timestep'], df['imu.linear_acceleration.x'], label='ax')
        axes[2, 1].plot(df['timestep'], df['imu.linear_acceleration.y'], label='ay')
        axes[2, 1].plot(df['timestep'], df['imu.linear_acceleration.z'], label='az')
        axes[2, 1].set_title('Linear Acceleration')
        axes[2, 1].set_ylabel('Acceleration (m/s²)')
        axes[2, 1].set_xlabel('Timestep')
        axes[2, 1].legend()
        axes[2, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def _create_additional_formats(self, images, drone_name, image_type, fps, width, height):
        """Create additional video formats for better compatibility."""
        # Try to create WebM format (better compression)
        try:
            webm_path = os.path.join(self.data_dir, f'{drone_name}_{image_type}_video.webm')
            fourcc_webm = cv2.VideoWriter_fourcc(*'VP80')
            video_writer_webm = cv2.VideoWriter(webm_path, fourcc_webm, fps, (width, height))
            
            if video_writer_webm.isOpened():
                print("Creating additional WebM format...")
                for image_name in images:
                    image_path = os.path.join(self.data_dir, drone_name, f'{image_type}_images', image_name)
                    frame = cv2.imread(image_path)
                    if frame is not None:
                        # Images are already in BGR format, use directly
                        video_writer_webm.write(frame)
                
                video_writer_webm.release()
                print(f"WebM video saved to: {webm_path}")
            else:
                video_writer_webm.release()
        except Exception as e:
            print(f"Could not create WebM format: {e}")

    def create_rgb_video_from_images(self, drone_name, image_type='rgb', fps=30):
        """Create RGB video from collected images using imageio (RGB-native)."""
        import imageio
        
        image_dir = os.path.join(self.data_dir, drone_name, f'{image_type}_images')
        if not os.path.exists(image_dir):
            print(f"No {image_type} images found for {drone_name}")
            return
        
        images = sorted([img for img in os.listdir(image_dir) if img.endswith('.png')])
        if not images:
            print(f"No images found in {image_dir}")
            return
        
        print(f"Creating RGB-native video with {len(images)} frames at {fps} FPS...")
        
        # Create video using imageio (preserves RGB format)
        output_path = os.path.join(self.data_dir, f'{drone_name}_{image_type}_video_rgb.mp4')
        
        # Use imageio to create RGB video
        with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8, macro_block_size=1) as writer:
            for i, image_name in enumerate(images):
                image_path = os.path.join(image_dir, image_name)
                
                # Read image preserving RGB format
                # Since we saved raw RGB data, we need to read it correctly
                frame = imageio.imread(image_path)
                
                if frame is None:
                    print(f"Warning: Could not read image {image_name}")
                    continue
                
                # Apply slight sharpening if desired (in RGB space)
                if image_type == 'rgb':
                    # Convert to float for processing
                    frame_float = frame.astype(np.float32)
                    
                    # Simple sharpening kernel
                    kernel = np.array([[-0.1, -0.1, -0.1], 
                                     [-0.1,  1.8, -0.1], 
                                     [-0.1, -0.1, -0.1]], dtype=np.float32)
                    
                    # Apply kernel to each channel
                    for c in range(3):
                        frame_float[:, :, c] = cv2.filter2D(frame_float[:, :, c], -1, kernel)
                    
                    # Convert back to uint8 and clip
                    frame = np.clip(frame_float, 0, 255).astype(np.uint8)
                
                # Write RGB frame directly (no conversion)
                writer.append_data(frame)
                
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(images)} frames...")
        
        print(f"RGB video saved to: {output_path}")
        return output_path

    def create_video_from_images(self, drone_name, image_type='rgb', fps=30, quality=95):
        """Create high-quality video from collected images."""
        image_dir = os.path.join(self.data_dir, drone_name, f'{image_type}_images')
        if not os.path.exists(image_dir):
            print(f"No {image_type} images found for {drone_name}")
            return
        
        images = sorted([img for img in os.listdir(image_dir) if img.endswith('.png')])
        if not images:
            print(f"No images found in {image_dir}")
            return
        
        # Read first image to get dimensions
        first_image = cv2.imread(os.path.join(image_dir, images[0]))
        height, width, _ = first_image.shape
        
        print(f"Creating high-quality video with {len(images)} frames at {fps} FPS...")
        
        # Try multiple codecs in order of preference
        codecs_to_try = [
            ('XVID', 'mp4v'),  # Most compatible
            ('mp4v', 'mp4v'),  # Fallback 1
            ('MJPG', 'avi'),   # Fallback 2 - Motion JPEG
        ]
        
        video_writer = None
        output_path = None
        
        for codec_name, file_ext in codecs_to_try:
            try:
                output_path = os.path.join(self.data_dir, f'{drone_name}_{image_type}_video.{file_ext}')
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                # Test if the video writer was created successfully
                if video_writer.isOpened():
                    print(f"Using codec: {codec_name}")
                    break
                else:
                    video_writer.release()
                    video_writer = None
            except Exception as e:
                print(f"Failed to initialize codec {codec_name}: {e}")
                if video_writer:
                    video_writer.release()
                    video_writer = None
        
        if video_writer is None:
            print("ERROR: Could not initialize any video codec!")
            print("Please install additional codec support:")
            print("  sudo apt update")
            print("  sudo apt install ffmpeg libavcodec-extra")
            print("  pip install opencv-python-headless")
            return
        
        # Process and write frames
        for i, image_name in enumerate(images):
            image_path = os.path.join(image_dir, image_name)
            frame = cv2.imread(image_path, cv2.IMREAD_COLOR)
            
            if frame is None:
                print(f"Warning: Could not read image {image_name}")
                continue
            
            # The saved images are already in BGR format (converted when saved)
            # so we can use them directly with OpenCV video writer
            if image_type == 'rgb':
                # Apply slight sharpening to improve perceived quality
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], dtype=np.float32)
                kernel = kernel * 0.1 + np.eye(3) * 0.9
                frame = cv2.filter2D(frame, -1, kernel)
            
            video_writer.write(frame)
            
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1}/{len(images)} frames...")
        
        video_writer.release()
        print(f"Video saved to: {output_path}")
        
        # Try to create an additional high-quality version if XVID worked
        if 'XVID' in str(fourcc):
            self._create_additional_formats(images, drone_name, image_type, fps, width, height)
    
    def visualize_lidar_snapshot(self, drone_name, timestep):
        """Visualize a single LiDAR snapshot."""
        lidar_file = os.path.join(self.data_dir, drone_name, 'lidar_data', 
                                 f'lidar_{timestep:06d}.npy')
        if not os.path.exists(lidar_file):
            print(f"No LiDAR data found for {drone_name} at timestep {timestep}")
            return
        
        points = np.load(lidar_file)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Color by distance
        distances = np.linalg.norm(points, axis=1)
        scatter = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                           c=distances, cmap='viridis', s=1)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'{drone_name} LiDAR Data - Timestep {timestep}')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Distance (m)')
        
        # Set equal aspect ratio
        ax.set_box_aspect([1,1,1])
        
        plt.show()

    def create_both_video_formats(self, drone_name, image_type='rgb', fps=30):
        """Create both RGB (for detectnet) and BGR (for display) videos."""
        print(f"Creating both video formats for {drone_name}...")
        
        # Create RGB video for detectnet/ML
        print("\n1. Creating RGB video (for detectnet/ML applications)...")
        rgb_path = self.create_rgb_video_from_images(drone_name, image_type, fps)
        
        # Create BGR video for display
        print("\n2. Creating BGR video (for display/viewing)...")
        bgr_path = self.create_video_from_images(drone_name, image_type, fps)
        
        print(f"\n=== VIDEO CREATION COMPLETE ===")
        if rgb_path:
            print(f"✓ RGB video (detectnet): {rgb_path}")
        if bgr_path:
            print(f"✓ BGR video (display): {bgr_path}")
        
        print(f"\nUsage:")
        print(f"- Use RGB video for detectnet, YOLO, or other ML inference")
        print(f"- Use BGR video for viewing in media players")
        
        return rgb_path, bgr_path

def main():
    """Main function for data visualization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize drone data')
    parser.add_argument('--data-dir', default='./simulation_data', 
                       help='Data directory path')
    parser.add_argument('--plot-trajectories', action='store_true',
                       help='Plot 3D trajectories')
    parser.add_argument('--plot-telemetry', type=str,
                       help='Plot telemetry for specific drone (Drone1 or Drone2)')
    parser.add_argument('--create-video', type=str,
                       help='Create video for specific drone (Drone1 or Drone2)')
    parser.add_argument('--video-type', default='rgb', choices=['rgb', 'ir'],
                       help='Type of video to create')
    parser.add_argument('--visualize-lidar', type=str,
                       help='Visualize LiDAR for specific drone (Drone1 or Drone2)')
    parser.add_argument('--timestep', type=int, default=100,
                       help='Timestep for LiDAR visualization')
    
    args = parser.parse_args()
    
    visualizer = DroneDataVisualizer(args.data_dir)
    
    if args.plot_trajectories:
        visualizer.plot_trajectories()
    
    if args.plot_telemetry:
        visualizer.plot_telemetry_timeseries(args.plot_telemetry)
    
    if args.create_video:
        visualizer.create_video_from_images(args.create_video, args.video_type)
    
    if args.visualize_lidar:
        visualizer.visualize_lidar_snapshot(args.visualize_lidar, args.timestep)
    
    if not any([args.plot_trajectories, args.plot_telemetry, 
                args.create_video, args.visualize_lidar]):
        parser.print_help()

if __name__ == "__main__":
    main()