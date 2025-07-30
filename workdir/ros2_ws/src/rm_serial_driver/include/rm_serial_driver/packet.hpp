// Copyright (c) 2022 ChenJun
// Licensed under the Apache-2.0 License.

#ifndef RM_SERIAL_DRIVER__PACKET_HPP_
#define RM_SERIAL_DRIVER__PACKET_HPP_

#include <algorithm>
#include <cstdint>
#include <vector>

namespace rm_serial_driver
{
struct ReceivePacket
{
  // TODO: 为验证自发自收，暂时改成0xA5
  // 因自发自收成功，改回0x5A
  // uint8_t header = 0x5A;
  // uint8_t header = 0xA5;
  uint8_t header = 0x5A;
  uint8_t id;
  float x;
  float y;
  uint16_t checksum = 0;
} __attribute__((packed));

struct SendPacket
{
  uint8_t header = 0xA5;
  // uint8_t id;
  // 任务一
  float board_x1;
  float board_y1;
  float board_x2;
  float board_y2;
  float board_x3;
  float board_y3;
  float board_x4;
  float board_y4;
  float laser1_x5;
  float laser1_y5;
  uint8_t end = 0xAF;
  // 任务二
  uint8_t header2 = 0xBA;
  float laser_follow_x6;
  float laser_follow_y6;
  float laser_followed_x7;
  float laser_followed_y7;
  uint8_t end2 = 0xBF;
  // 暂时不用
  uint16_t checksum = 0;
} __attribute__((packed));

inline ReceivePacket fromVector(const std::vector<uint8_t> & data)
{
  ReceivePacket packet;
  std::copy(data.begin(), data.end(), reinterpret_cast<uint8_t *>(&packet));
  return packet;
}

inline std::vector<uint8_t> toVector(const SendPacket & data)
{
  std::vector<uint8_t> packet(sizeof(SendPacket));
  std::copy(
    reinterpret_cast<const uint8_t *>(&data),
    reinterpret_cast<const uint8_t *>(&data) + sizeof(SendPacket), packet.begin());
  return packet;
}

}  // namespace rm_serial_driver

#endif  // RM_SERIAL_DRIVER__PACKET_HPP_
