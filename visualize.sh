#!/bin/bash
source venv/bin/activate
echo "Visualization Options:"
echo "1. Plot trajectories"
echo "2. Plot telemetry"
echo "3. Create video"
echo "4. Visualize LiDAR"
read -p "Select option (1-4): " option

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
        read -p "Enter timestep: " timestep
        python utils/data_visualizer.py --visualize-lidar $drone --timestep $timestep
        ;;
    *)
        echo "Invalid option"
        ;;
esac
