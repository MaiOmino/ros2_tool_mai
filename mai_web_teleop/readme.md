# mai_web_teleop

This project provides a web-based interface for teleoperating a ROS 2 robot, leveraging Zenoh for communication.  It allows users to control a robot from any device with a web browser, sending `geometry_msgs/Twist` commands over a Zenoh network to a robot running ROS 2.

## System Overview

The system consists of the following components:

1.  **Web UI (`index.html`):**  A simple HTML page with a joystick (using nipple.js) to control the robot.  User input is translated into linear and angular velocity commands and sent via WebSocket to the backend server.

2.  **Backend Server (`backend.py`):** A Python server built with FastAPI that handles WebSocket connections from the web UI. It receives velocity commands, serializes them into ROS 2 `geometry_msgs/Twist` messages, and publishes them to a Zenoh topic.

3.  **Zenoh Network:** Acts as the communication middleware, routing messages between the backend server and the robot.

4.  **`zenoh-bridge-ros2dds`:**  A bridge that connects the Zenoh network to the ROS 2 network on the robot, translating Zenoh messages into ROS 2 topics.

5.  **ROS 2 Robot (or Simulator):**  The robot or simulator that receives `geometry_msgs/Twist` commands on the `/cmd_vel` topic and executes them.

A visual representation of this architecture can be found in `system.md`.

## Prerequisites

*   **ROS 2:**  A working ROS 2 installation (e.g., Humble, Iron).

*   **Zenoh:** Ensure you have Zenoh installed and configured.  You'll need the `zenoh-bridge-ros2dds` for the robot side.

*   **Python:** Python 3.7 or higher is required for the backend server.  Install required packages:
    ```bash
    pip install fastapi uvicorn websockets zenoh rclpy geometry_msgs
    ```

*   **Web Browser:**  Any modern web browser to access the UI.

## Setup and Usage

**1. Configure Zenoh:**

*   Modify `config-server.json5` for the robot side (where `zenoh-bridge-ros2dds` will run).  Crucially, ensure the `mode` is set to `peer` or `router` and that it can connect to the Zenoh network (adjust `connect/endpoints` and `listen/endpoints` as needed). Allow the `cmd_vel` topic in the `allow` section. For example:
    ```json5
    {
      ...
      ros2dds: {
        ...
        allow: {
          subscribers: [".*/cmd_vel"],
        },
        ...
      },
      ...
      mode: "peer", // or "router" if this is the central Zenoh node
      connect: {
        endpoints: ["tcp/your_zenoh_router_ip:7447"] // Replace with your router's address
      },
      ...
    }
    ```

*   Modify `config-client.json5` for the client side (where the backend server will run).  Set the `mode` to `client` or `peer` and configure it to connect to the same Zenoh network as the robot. For example:
    ```json5
    {
      ...
      mode: "client",
      connect: {
        endpoints: ["tcp/your_zenoh_router_ip:7447"] // Replace with your router's address
      },
      ...
    }
    ```

**2.  Run the Zenoh Bridge on the Robot:**

```bash
# Source your ROS 2 environment
. /opt/ros/<your_ros2_distro>/setup.bash

# Run the bridge
zenoh-bridge-ros2dds -c config-server.json5
