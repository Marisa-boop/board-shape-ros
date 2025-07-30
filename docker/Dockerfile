# Use the base image from NVIDIA NGC
FROM nvcr.io/nvidia/pytorch:24.04-py3

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# 使用清华镜像替代官方源，加速国内镜像访问
RUN echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble main restricted universe multiverse" > /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-updates main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-backports main restricted universe multiverse" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ noble-security main restricted universe multiverse" >> /etc/apt/sources.list

# 先更新和升级系统已有的包
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update && \
    apt-get upgrade -y --no-install-recommends && \
    apt-get autoremove -y

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo \
    ca-certificates \
    git \
    wget \
    curl \
    vim \
    iproute2 \
    build-essential \
    cmake \
    gcc-11 g++-11 \
    clang-14 \
    libopencv-dev \
    libpcl-dev \
    libeigen3-dev \
    libgtest-dev \
    libtbb-dev \
    libffi-dev \
    libx11-dev \
    libglu1-mesa-dev \
    libgl1 \
    libglx0 \
    x11-xserver-utils \
    libxcb1 \
    libxcb-util1 \
    libgtk2.0-dev \
    libgtk-3-dev \
    pkg-config \
    libvtk9-dev \
    python3-vtk9 \
    gnupg2 \
    usbutils \
    tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置时区为上海
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 配置ROS2使用清华源
RUN echo 'export ROSDISTRO_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/rosdistro/index-v4.yaml' >> ~/.bashrc

# ROS2密钥及国内ROS2源配置（修正为noble版本）
# COPY ./packages/ros-archive-keyring.gpg /usr/share/keyrings/ros-archive-keyring.gpg
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu noble main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# ROS2 和相关工具安装
RUN apt-get update && \
    apt-get install -y \
    ros-jazzy-desktop \
    python3-argcomplete \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 配置全局 ROS2 rosdep hints（如有必要）
RUN mkdir -p /home/linux/.stack/pantry
COPY ./packages/global-hints.yaml /home/linux/.stack/pantry/global-hints-cache.yaml

RUN mkdir -p /etc/ros/rosdep/sources.list.d/
COPY ./packages/20-default.list /etc/ros/rosdep/sources.list.d/20-default.list
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && \
    bash -c "source ~/.bashrc && \
    rosdep update"

RUN useradd -m -d /home/linux -s /bin/bash linux && \
    echo "linux:linux101" | chpasswd && \
    usermod -aG sudo linux

RUN apt update && \
    apt install -y v4l-utils && \
    apt install -y ros-jazzy-image-pipeline

RUN apt install ros-jazzy-cv-bridge

RUN pip install --break-system-packages pydantic==1.10.9 && \
    pip install --break-system-packages git+https://github.com/ultralytics/ultralytics.git@main

COPY ./workdir /workdir

# 设置工作目录
WORKDIR /workdir/ros2_ws

RUN apt update && \ 
    rosdep install --from-paths src --ignore-src -y --rosdistro jazzy && \
    cd /root && \
    rm -rf /workdir

RUN echo "source /workdir/ros2_ws/install/setup.bash" >> ~/.bashrc
RUN mv /usr/local/bin/cmake /usr/local/bin/cmake.bak

Run apt install -y ros-jazzy-asio-cmake-module && \
    pip install --break-system-packages pyserial

CMD ["/bin/bash"]
