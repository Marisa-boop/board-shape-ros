# Attributions

This project directly incorporates the following third-party open-source packages in
`workdir/ros2_ws/src/`. Their licenses and copyright notices are reproduced below.

---

## usb_cam

- **Source:** [ROS 2 community / Bosch](https://github.com/ros-drivers/usb_cam)
- **License:** BSD 3-Clause
- **Copyright:** 2014 Robert Bosch, LLC and contributors
- **Files:** `workdir/ros2_ws/src/usb_cam/`

### BSD 3-Clause License

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

---

## rm_serial_driver

- **Source:** [ChenJun / SMBU-PolarBear-Robotics-Team](https://gitee.com/SMBU-POLARBEAR/PB_RM_Vision/tree/sentry/src/rm_serial_driver)
- **License:** Apache-2.0
- **Copyright:** 2022 ChenJun
- **Files:** `workdir/ros2_ws/src/rm_serial_driver/`

### Apache 2.0 License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

## mindvision_camera

- **Source:** [ChenJun / chenjunnn](https://github.com/chenjunnn/ros2_mindvision_camera)
- **License:** MIT
- **Copyright:** 2022 ChenJun
- **Files:** `workdir/ros2_ws/src/rm_shared/rm_hardware/mindvision_camera/`

---

## hikvision_camera

- **Source:** [nolem / chenjunnn](https://github.com/chenjunnn/ros2_hik_camera)
- **License:** Not explicitly declared (TBD)
- **Files:** `workdir/ros2_ws/src/rm_shared/rm_hardware/hikvision_camera/`

---

## Others in rm_shared

The following packages are included via `rm_shared`; their licenses are to be confirmed
from their respective upstream sources:

| Package | Source | License |
|---------|--------|---------|
| daheng_camera | [CSU-FYT-Vision](https://github.com/CSU-FYT-Vision/FYT2024_vision) | TBD |
| livox_ros_driver2 | [SMBU-PolarBear](https://github.com/SMBU-PolarBear-Robotics-Team/livox_ros_driver2) | TBD |
| rm_utils | [CSU-FYT-Vision](https://github.com/CSU-FYT-Vision/FYT2024_vision) | TBD |

---

## Ultralytics (runtime dependency)

- **Source:** [Ultralytics](https://github.com/ultralytics/ultralytics)
- **License:** AGPL-3.0
- This project uses `ultralytics` as a Python package dependency (not distributed
  in source form). For commercial use, a separate license from Ultralytics is required.

---

*This document was generated to comply with the attribution requirements of the
incorporated open-source packages. If any attribution is missing or incorrect,
please open an issue.*
