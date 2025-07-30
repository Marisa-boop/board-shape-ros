xhost +local:docker
docker run -it --rm \
  --privileged \
  --gpus all \
  -e QT_X11_NO_MITSHM=1 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /dev/dri:/dev/dri \
  -v /dev/video0:/dev/video0 \
  -v /dev/video2:/dev/video2 \
  -v ./workdir:/workdir \
  --name ros2_yolo_usb_driver \
  --workdir /workdir/ros2_ws \
  --user root \
  marisa101/private:ros2_yolo_usb_driver_latest \
  /bin/bash
xhost -local:docker
