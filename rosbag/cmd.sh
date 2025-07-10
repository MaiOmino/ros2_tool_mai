#!/bin/bash

source /opt/ros/humble/setup.bash &&
mkdir -p /ros2_ws/rosbags &&
ros2 bag record $(cat /ros2_ws/topics.txt) -o /ros2_ws/bagfile
cp -r /ros2_ws/bagfile /ros2_ws/rosbagsk