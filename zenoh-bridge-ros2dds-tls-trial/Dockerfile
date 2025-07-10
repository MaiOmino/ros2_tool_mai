FROM osrf/ros:humble-desktop-full

RUN echo "deb [trusted=yes] https://download.eclipse.org/zenoh/debian-repo/ /" | tee -a /etc/apt/sources.list > /dev/null
RUN apt-get update && apt-get install -y \
    python3-pip \
    ros-humble-rqt* \
    ros-humble-rmw-cyclonedds-cpp \
    zenoh-bridge-ros2dds \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

RUN echo '#!/bin/bash\n\
    ip link set lo multicast on\n\
    exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

WORKDIR /root
RUN mkdir -p /root/mnt