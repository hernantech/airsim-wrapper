#!/bin/bash
source venv/bin/activate
echo "Visualization Options:"
echo "1. Plot trajectories"
echo "2. Plot telemetry"
echo "3. Create video (BGR - for display)"
echo "4. Create high-quality video (BGR - for display)"
echo "5. Create RGB video (for detectnet/ML)"
echo "6. Create both RGB and BGR videos"
echo "7. Visualize LiDAR"
read -p "Select option (1-7): " option

case $option in
    1)
        python utils/data_visualizer.py --plot-trajectories
        ;;
    2)
        read -p "Enter drone name (Drone1/Drone2): " drone
        python utils/data_visualizer.py --plot-telemetry $drone
        ;;
    3)
        read -p "Enter drone name (Drone1/Drone2): " drone
        read -p "Enter video type (rgb/ir): " vtype
        python utils/data_visualizer.py --create-video $drone --video-type $vtype
        ;;
    4)
        read -p "Enter drone name (Drone1/Drone2): " drone
        read -p "Enter video type (rgb/ir): " vtype
        read -p "Enter FPS (default 30): " fps
        fps=${fps:-30}
        echo "Creating high-quality video at ${fps} FPS..."
        python -c "
from utils.data_visualizer import DroneDataVisualizer
vis = DroneDataVisualizer('./simulation_data')
vis.create_video_from_images('${drone}', '${vtype}', ${fps})
"
        ;;
    5)
        read -p "Enter drone name (Drone1/Drone2): " drone
        read -p "Enter video type (rgb/ir): " vtype
        read -p "Enter FPS (default 30): " fps
        fps=${fps:-30}
        echo "Creating RGB-native video at ${fps} FPS (for detectnet/ML)..."
        python -c "
from utils.data_visualizer import DroneDataVisualizer
vis = DroneDataVisualizer('./simulation_data')
vis.create_rgb_video_from_images('${drone}', '${vtype}', ${fps})
"
        ;;
    6)
        read -p "Enter drone name (Drone1/Drone2): " drone
        read -p "Enter video type (rgb/ir): " vtype
        read -p "Enter FPS (default 30): " fps
        fps=${fps:-30}
        echo "Creating both RGB and BGR videos at ${fps} FPS..."
        python -c "
from utils.data_visualizer import DroneDataVisualizer
vis = DroneDataVisualizer('./simulation_data')
vis.create_both_video_formats('${drone}', '${vtype}', ${fps})
"
        ;;
    7)
        read -p "Enter drone name (Drone1/Drone2): " drone
        read -p "Enter timestep: " timestep
        python utils/data_visualizer.py --visualize-lidar $drone --timestep $timestep
        ;;
    *)
        echo "Invalid option"
        ;;
esac
