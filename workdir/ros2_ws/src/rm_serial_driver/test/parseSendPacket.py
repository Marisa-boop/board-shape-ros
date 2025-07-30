# #!/usr/bin/env python3
# import serial
# import struct
# import argparse
#
#
# # 定义CRC16查表法实现（与C++代码完全一致）
# def crc16_table(data):
#     """CRC16查表法实现（多项式0x1021）"""
#     crc_table = [
#         0x0000,
#         0x1189,
#         0x2312,
#         0x329B,
#         0x4624,
#         0x57AD,
#         0x6536,
#         0x74BF,
#         0x8C48,
#         0x9DC1,
#         0xAF5A,
#         0xBED3,
#         0xCA6C,
#         0xDBE5,
#         0xE97E,
#         0xF8F7,
#         0x1081,
#         0x0108,
#         0x3393,
#         0x221A,
#         0x56A5,
#         0x472C,
#         0x75B7,
#         0x643E,
#         0x9CC9,
#         0x8D40,
#         0xBFDB,
#         0xAE52,
#         0xDAED,
#         0xCB64,
#         0xF9FF,
#         0xE876,
#         0x2102,
#         0x308B,
#         0x0210,
#         0x1399,
#         0x6726,
#         0x76AF,
#         0x4434,
#         0x55BD,
#         0xAD4A,
#         0xBCC3,
#         0x8E58,
#         0x9FD1,
#         0xEB6E,
#         0xFAE7,
#         0xC87C,
#         0xD9F5,
#         0x3183,
#         0x200A,
#         0x1291,
#         0x0318,
#         0x77A7,
#         0x662E,
#         0x54B5,
#         0x453C,
#         0xBDCB,
#         0xAC42,
#         0x9ED9,
#         0x8F50,
#         0xFBEF,
#         0xEA66,
#         0xD8FD,
#         0xC974,
#         0x4204,
#         0x538D,
#         0x6116,
#         0x709F,
#         0x0420,
#         0x15A9,
#         0x2732,
#         0x36BB,
#         0xCE4C,
#         0xDFC5,
#         0xED5E,
#         0xFCD7,
#         0x8868,
#         0x99E1,
#         0xAB7A,
#         0xBAF3,
#         0x5285,
#         0x430C,
#         0x7197,
#         0x601E,
#         0x14A1,
#         0x0528,
#         0x37B3,
#         0x263A,
#         0xDECD,
#         0xCF44,
#         0xFDDF,
#         0xEC56,
#         0x98E9,
#         0x8960,
#         0xBBFB,
#         0xAA72,
#         0x6306,
#         0x728F,
#         0x4014,
#         0x519D,
#         0x2522,
#         0x34AB,
#         0x0630,
#         0x17B9,
#         0xEF4E,
#         0xFEC7,
#         0xCC5C,
#         0xDDD5,
#         0xA96A,
#         0xB8E3,
#         0x8A78,
#         0x9BF1,
#         0x7387,
#         0x620E,
#         0x5095,
#         0x411C,
#         0x35A3,
#         0x242A,
#         0x16B1,
#         0x0738,
#         0xFFCF,
#         0xEE46,
#         0xDCDD,
#         0xCD54,
#         0xB9EB,
#         0xA862,
#         0x9AF9,
#         0x8B70,
#         0x8408,
#         0x9581,
#         0xA71A,
#         0xB693,
#         0xC22C,
#         0xD3A5,
#         0xE13E,
#         0xF0B7,
#         0x0840,
#         0x19C9,
#         0x2B52,
#         0x3ADB,
#         0x4E64,
#         0x5FED,
#         0x6D76,
#         0x7CFF,
#         0x9489,
#         0x8500,
#         0xB79B,
#         0xA612,
#         0xD2AD,
#         0xC324,
#         0xF1BF,
#         0xE036,
#         0x18C1,
#         0x0948,
#         0x3BD3,
#         0x2A5A,
#         0x5EE5,
#         0x4F6C,
#         0x7DF7,
#         0x6C7E,
#         0xA50A,
#         0xB483,
#         0x8618,
#         0x9791,
#         0xE32E,
#         0xF2A7,
#         0xC03C,
#         0xD1B5,
#         0x2942,
#         0x38CB,
#         0x0A50,
#         0x1BD9,
#         0x6F66,
#         0x7EEF,
#         0x4C74,
#         0x5DFD,
#         0xB58B,
#         0xA402,
#         0x9699,
#         0x8710,
#         0xF3AF,
#         0xE226,
#         0xD0BD,
#         0xC134,
#         0x39C3,
#         0x284A,
#         0x1AD1,
#         0x0B58,
#         0x7FE7,
#         0x6E6E,
#         0x5CF5,
#         0x4D7C,
#         0xC60C,
#         0xD785,
#         0xE51E,
#         0xF497,
#         0x8028,
#         0x91A1,
#         0xA33A,
#         0xB2B3,
#         0x4A44,
#         0x5BCD,
#         0x6956,
#         0x78DF,
#         0x0C60,
#         0x1DE9,
#         0x2F72,
#         0x3EFB,
#         0xD68D,
#         0xC704,
#         0xF59F,
#         0xE416,
#         0x90A9,
#         0x8120,
#         0xB3BB,
#         0xA232,
#         0x5AC5,
#         0x4B4C,
#         0x79D7,
#         0x685E,
#         0x1CE1,
#         0x0D68,
#         0x3FF3,
#         0x2E7A,
#         0xE70E,
#         0xF687,
#         0xC41C,
#         0xD595,
#         0xA12A,
#         0xB0A3,
#         0x8238,
#         0x93B1,
#         0x6B46,
#         0x7ACF,
#         0x4854,
#         0x59DD,
#         0x2D62,
#         0x3CEB,
#         0x0E70,
#         0x1FF9,
#         0xF78F,
#         0xE606,
#         0xD49D,
#         0xC514,
#         0xB1AB,
#         0xA022,
#         0x92B9,
#         0x8330,
#         0x7BC7,
#         0x6A4E,
#         0x58D5,
#         0x495C,
#         0x3DE3,
#         0x2C6A,
#         0x1EF1,
#         0x0F78,
#     ]
#
#     crc = 0xFFFF
#     for byte in data:
#         crc = (crc >> 8) ^ crc_table[(crc ^ byte) & 0xFF]
#     return crc
#
#
# def main():
#     parser = argparse.ArgumentParser(description="Serial Packet Receiver")
#     parser.add_argument(
#         "-p",
#         "--port",
#         type=str,
#         default="/dev/ttyACM0",
#         help="Serial port name (e.g. /dev/ttyACM0 or COM3)",
#     )
#     parser.add_argument(
#         "-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)"
#     )
#     args = parser.parse_args()
#
#     try:
#         # 配置串口参数（与C++配置完全一致）
#         ser = serial.Serial(
#             port=args.port,
#             baudrate=args.baud,
#             bytesize=serial.EIGHTBITS,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             timeout=1,  # 读取超时1秒
#         )
#         print(f"Listening on {args.port} at {args.baud} baud...")
#         print("Press Ctrl+C to exit")
#
#         # 清空串口缓冲区
#         ser.reset_input_buffer()
#
#         while True:
#             # 读取包头(0xA5)
#             header = ser.read(1)
#             if not header:
#                 continue
#
#             # 检查包头有效性
#             if header[0] != 0xA5:
#                 print(f"✗ Invalid header: 0x{header[0]:02X}")
#                 continue
#
#             # 读取剩余数据包(11字节)
#             data = ser.read(11)
#             if len(data) != 11:
#                 print(
#                     f"✗ Incomplete packet: expected 11 bytes, got {
#                         len(data)}"
#                 )
#                 continue
#
#             full_packet = header + data  # 完整数据包12字节
#
#             try:
#                 # 解析数据包: 包头(1B) + ID(1B) + X(4B) + Y(4B) + CRC(2B)
#                 # 使用小端格式解析（与C++结构体一致）
#                 packet_data = struct.unpack("<BBffH", full_packet)
#                 header_val, packet_id, x, y, received_checksum = packet_data
#
#                 # 计算CRC（只计算前10字节，不包含CRC字段）
#                 calculated_crc = crc16_table(full_packet[:10])
#
#                 # 验证CRC
#                 if calculated_crc == received_checksum:
#                     print(
#                         f"✓ ID: {packet_id:2d} | X: {
#                             x:8.3f} | Y: {y:8.3f} | CRC: OK"
#                     )
#                 else:
#                     print(
#                         f"✗ ID: {packet_id:2d} | X: {x:8.3f} | Y: {y:8.3f} | "
#                         f"CRC FAIL (calc: 0x{calculated_crc:04X}, recv: 0x{
#                             received_checksum:04X})"
#                     )
#             except struct.error as e:
#                 print(f"✗ Packet parsing error: {e}")
#             except Exception as e:
#                 print(f"✗ Unexpected error: {e}")
#
#     except serial.SerialException as e:
#         print(f"Serial error: {e}")
#         print("Possible solutions:")
#         print(
#             "1. Check port existence and permissions (e.g., sudo chmod 666 /dev/ttyACM0)"
#         )
#         print("2. Verify baud rate matches sender configuration")
#         print("3. Ensure no other program is using the serial port")
#     except KeyboardInterrupt:
#         print("\nProgram terminated by user")
#     finally:
#         if "ser" in locals() and ser.is_open:
#             ser.close()
#             print("Serial port closed")
#
#
# if __name__ == "__main__":
#     main()

# import serial
# import struct
# import argparse
#
#
# # 定义CRC16查表法实现（与C++代码完全一致）
# def crc16_table(data):
#     """CRC16查表法实现（多项式0x1021）"""
#     crc_table = [
#         0x0000,
#         0x1189,
#         0x2312,
#         0x329B,
#         0x4624,
#         0x57AD,
#         0x6536,
#         0x74BF,
#         0x8C48,
#         0x9DC1,
#         0xAF5A,
#         0xBED3,
#         0xCA6C,
#         0xDBE5,
#         0xE97E,
#         0xF8F7,
#         0x1081,
#         0x0108,
#         0x3393,
#         0x221A,
#         0x56A5,
#         0x472C,
#         0x75B7,
#         0x643E,
#         0x9CC9,
#         0x8D40,
#         0xBFDB,
#         0xAE52,
#         0xDAED,
#         0xCB64,
#         0xF9FF,
#         0xE876,
#         0x2102,
#         0x308B,
#         0x0210,
#         0x1399,
#         0x6726,
#         0x76AF,
#         0x4434,
#         0x55BD,
#         0xAD4A,
#         0xBCC3,
#         0x8E58,
#         0x9FD1,
#         0xEB6E,
#         0xFAE7,
#         0xC87C,
#         0xD9F5,
#         0x3183,
#         0x200A,
#         0x1291,
#         0x0318,
#         0x77A7,
#         0x662E,
#         0x54B5,
#         0x453C,
#         0xBDCB,
#         0xAC42,
#         0x9ED9,
#         0x8F50,
#         0xFBEF,
#         0xEA66,
#         0xD8FD,
#         0xC974,
#         0x4204,
#         0x538D,
#         0x6116,
#         0x709F,
#         0x0420,
#         0x15A9,
#         0x2732,
#         0x36BB,
#         0xCE4C,
#         0xDFC5,
#         0xED5E,
#         0xFCD7,
#         0x8868,
#         0x99E1,
#         0xAB7A,
#         0xBAF3,
#         0x5285,
#         0x430C,
#         0x7197,
#         0x601E,
#         0x14A1,
#         0x0528,
#         0x37B3,
#         0x263A,
#         0xDECD,
#         0xCF44,
#         0xFDDF,
#         0xEC56,
#         0x98E9,
#         0x8960,
#         0xBBFB,
#         0xAA72,
#         0x6306,
#         0x728F,
#         0x4014,
#         0x519D,
#         0x2522,
#         0x34AB,
#         0x0630,
#         0x17B9,
#         0xEF4E,
#         0xFEC7,
#         0xCC5C,
#         0xDDD5,
#         0xA96A,
#         0xB8E3,
#         0x8A78,
#         0x9BF1,
#         0x7387,
#         0x620E,
#         0x5095,
#         0x411C,
#         0x35A3,
#         0x242A,
#         0x16B1,
#         0x0738,
#         0xFFCF,
#         0xEE46,
#         0xDCDD,
#         0xCD54,
#         0xB9EB,
#         0xA862,
#         0x9AF9,
#         0x8B70,
#         0x8408,
#         0x9581,
#         0xA71A,
#         0xB693,
#         0xC22C,
#         0xD3A5,
#         0xE13E,
#         0xF0B7,
#         0x0840,
#         0x19C9,
#         0x2B52,
#         0x3ADB,
#         0x4E64,
#         0x5FED,
#         0x6D76,
#         0x7CFF,
#         0x9489,
#         0x8500,
#         0xB79B,
#         0xA612,
#         0xD2AD,
#         0xC324,
#         0xF1BF,
#         0xE036,
#         0x18C1,
#         0x0948,
#         0x3BD3,
#         0x2A5A,
#         0x5EE5,
#         0x4F6C,
#         0x7DF7,
#         0x6C7E,
#         0xA50A,
#         0xB483,
#         0x8618,
#         0x9791,
#         0xE32E,
#         0xF2A7,
#         0xC03C,
#         0xD1B5,
#         0x2942,
#         0x38CB,
#         0x0A50,
#         0x1BD9,
#         0x6F66,
#         0x7EEF,
#         0x4C74,
#         0x5DFD,
#         0xB58B,
#         0xA402,
#         0x9699,
#         0x8710,
#         0xF3AF,
#         0xE226,
#         0xD0BD,
#         0xC134,
#         0x39C3,
#         0x284A,
#         0x1AD1,
#         0x0B58,
#         0x7FE7,
#         0x6E6E,
#         0x5CF5,
#         0x4D7C,
#         0xC60C,
#         0xD785,
#         0xE51E,
#         0xF497,
#         0x8028,
#         0x91A1,
#         0xA33A,
#         0xB2B3,
#         0x4A44,
#         0x5BCD,
#         0x6956,
#         0x78DF,
#         0x0C60,
#         0x1DE9,
#         0x2F72,
#         0x3EFB,
#         0xD68D,
#         0xC704,
#         0xF59F,
#         0xE416,
#         0x90A9,
#         0x8120,
#         0xB3BB,
#         0xA232,
#         0x5AC5,
#         0x4B4C,
#         0x79D7,
#         0x685E,
#         0x1CE1,
#         0x0D68,
#         0x3FF3,
#         0x2E7A,
#         0xE70E,
#         0xF687,
#         0xC41C,
#         0xD595,
#         0xA12A,
#         0xB0A3,
#         0x8238,
#         0x93B1,
#         0x6B46,
#         0x7ACF,
#         0x4854,
#         0x59DD,
#         0x2D62,
#         0x3CEB,
#         0x0E70,
#         0x1FF9,
#         0xF78F,
#         0xE606,
#         0xD49D,
#         0xC514,
#         0xB1AB,
#         0xA022,
#         0x92B9,
#         0x8330,
#         0x7BC7,
#         0x6A4E,
#         0x58D5,
#         0x495C,
#         0x3DE3,
#         0x2C6A,
#         0x1EF1,
#         0x0F78,
#     ]
#
#     crc = 0xFFFF
#     for byte in data:
#         crc = (crc >> 8) ^ crc_table[(crc ^ byte) & 0xFF]
#     return crc
#
#
# def main():
#     parser = argparse.ArgumentParser(description="Serial Packet Receiver")
#     parser.add_argument(
#         "-p",
#         "--port",
#         type=str,
#         default="/dev/ttyACM0",
#         help="Serial port name (e.g. /dev/ttyACM0 or COM3)",
#     )
#     parser.add_argument(
#         "-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)"
#     )
#     args = parser.parse_args()
#
#     try:
#         # 配置串口参数（与C++配置完全一致）
#         ser = serial.Serial(
#             port=args.port,
#             baudrate=args.baud,
#             bytesize=serial.EIGHTBITS,
#             parity=serial.PARITY_NONE,
#             stopbits=serial.STOPBITS_ONE,
#             timeout=1,  # 读取超时1秒
#         )
#         print(f"Listening on {args.port} at {args.baud} baud...")
#         print("Press Ctrl+C to exit")
#
#         # 清空串口缓冲区
#         ser.reset_input_buffer()
#
#         while True:
#             # 一次性读取完整的12字节数据包
#             packet = ser.read(12)
#
#             if not packet:
#                 continue  # 没有读到数据，继续等待
#
#             if len(packet) != 12:
#                 print(f"✗ Incomplete packet: expected 12 bytes, got {
#                       len(packet)}")
#                 continue
#
#             # 检查包头有效性（第一个字节是否为0xA5）
#             if packet[0] != 0xA5:
#                 print(f"✗ Invalid header: 0x{packet[0]:02X}")
#                 continue
#
#             try:
#                 # 解析数据包: 包头(1B) + ID(1B) + X(4B) + Y(4B) + CRC(2B)
#                 # 使用小端格式解析（与C++结构体一致）
#                 header_val, packet_id, x, y, received_checksum = struct.unpack(
#                     "<BBffH", packet
#                 )
#
#                 # 计算CRC（只计算前10字节，不包含CRC字段）
#                 calculated_crc = crc16_table(packet[:10])
#
#                 # 验证CRC
#                 if calculated_crc == received_checksum:
#                     print(f"✓ ID: {packet_id:2d} | X: {
#                           x:8.3f} | Y: {y:8.3f} | CRC: OK")
#                 else:
#                     print(
#                         f"✗ ID: {packet_id:2d} | X: {x:8.3f} | Y: {y:8.3f} | "
#                         f"CRC FAIL (calc: 0x{calculated_crc:04X}, recv: 0x{
#                             received_checksum:04X})"
#                     )
#             except struct.error as e:
#                 print(f"✗ Packet parsing error: {e}")
#                 # 打印原始数据包帮助调试
#                 print(f"Raw packet: {packet.hex().upper()}")
#             except Exception as e:
#                 print(f"✗ Unexpected error: {e}")
#
#     except serial.SerialException as e:
#         print(f"Serial error: {e}")
#         print("Possible solutions:")
#         print(
#             "1. Check port existence and permissions (e.g., sudo chmod 666 /dev/ttyACM0)"
#         )
#         print("2. Verify baud rate matches sender configuration")
#         print("3. Ensure no other program is using the serial port")
#     except KeyboardInterrupt:
#         print("\nProgram terminated by user")
#     finally:
#         if "ser" in locals() and ser.is_open:
#             ser.close()
#             print("Serial port closed")
#
#
# if __name__ == "__main__":
#     main()

import serial
import struct
import argparse
import time


# 定义CRC16查表法实现（与C++代码完全一致）
def crc16_table(data):
    """CRC16查表法实现（多项式0x1021）"""
    crc_table = [
        0x0000,
        0x1189,
        0x2312,
        0x329B,
        0x4624,
        0x57AD,
        0x6536,
        0x74BF,
        0x8C48,
        0x9DC1,
        0xAF5A,
        0xBED3,
        0xCA6C,
        0xDBE5,
        0xE97E,
        0xF8F7,
        0x1081,
        0x0108,
        0x3393,
        0x221A,
        0x56A5,
        0x472C,
        0x75B7,
        0x643E,
        0x9CC9,
        0x8D40,
        0xBFDB,
        0xAE52,
        0xDAED,
        0xCB64,
        0xF9FF,
        0xE876,
        0x2102,
        0x308B,
        0x0210,
        0x1399,
        0x6726,
        0x76AF,
        0x4434,
        0x55BD,
        0xAD4A,
        0xBCC3,
        0x8E58,
        0x9FD1,
        0xEB6E,
        0xFAE7,
        0xC87C,
        0xD9F5,
        0x3183,
        0x200A,
        0x1291,
        0x0318,
        0x77A7,
        0x662E,
        0x54B5,
        0x453C,
        0xBDCB,
        0xAC42,
        0x9ED9,
        0x8F50,
        0xFBEF,
        0xEA66,
        0xD8FD,
        0xC974,
        0x4204,
        0x538D,
        0x6116,
        0x709F,
        0x0420,
        0x15A9,
        0x2732,
        0x36BB,
        0xCE4C,
        0xDFC5,
        0xED5E,
        0xFCD7,
        0x8868,
        0x99E1,
        0xAB7A,
        0xBAF3,
        0x5285,
        0x430C,
        0x7197,
        0x601E,
        0x14A1,
        0x0528,
        0x37B3,
        0x263A,
        0xDECD,
        0xCF44,
        0xFDDF,
        0xEC56,
        0x98E9,
        0x8960,
        0xBBFB,
        0xAA72,
        0x6306,
        0x728F,
        0x4014,
        0x519D,
        0x2522,
        0x34AB,
        0x0630,
        0x17B9,
        0xEF4E,
        0xFEC7,
        0xCC5C,
        0xDDD5,
        0xA96A,
        0xB8E3,
        0x8A78,
        0x9BF1,
        0x7387,
        0x620E,
        0x5095,
        0x411C,
        0x35A3,
        0x242A,
        0x16B1,
        0x0738,
        0xFFCF,
        0xEE46,
        0xDCDD,
        0xCD54,
        0xB9EB,
        0xA862,
        0x9AF9,
        0x8B70,
        0x8408,
        0x9581,
        0xA71A,
        0xB693,
        0xC22C,
        0xD3A5,
        0xE13E,
        0xF0B7,
        0x0840,
        0x19C9,
        0x2B52,
        0x3ADB,
        0x4E64,
        0x5FED,
        0x6D76,
        0x7CFF,
        0x9489,
        0x8500,
        0xB79B,
        0xA612,
        0xD2AD,
        0xC324,
        0xF1BF,
        0xE036,
        0x18C1,
        0x0948,
        0x3BD3,
        0x2A5A,
        0x5EE5,
        0x4F6C,
        0x7DF7,
        0x6C7E,
        0xA50A,
        0xB483,
        0x8618,
        0x9791,
        0xE32E,
        0xF2A7,
        0xC03C,
        0xD1B5,
        0x2942,
        0x38CB,
        0x0A50,
        0x1BD9,
        0x6F66,
        0x7EEF,
        0x4C74,
        0x5DFD,
        0xB58B,
        0xA402,
        0x9699,
        0x8710,
        0xF3AF,
        0xE226,
        0xD0BD,
        0xC134,
        0x39C3,
        0x284A,
        0x1AD1,
        0x0B58,
        0x7FE7,
        0x6E6E,
        0x5CF5,
        0x4D7C,
        0xC60C,
        0xD785,
        0xE51E,
        0xF497,
        0x8028,
        0x91A1,
        0xA33A,
        0xB2B3,
        0x4A44,
        0x5BCD,
        0x6956,
        0x78DF,
        0x0C60,
        0x1DE9,
        0x2F72,
        0x3EFB,
        0xD68D,
        0xC704,
        0xF59F,
        0xE416,
        0x90A9,
        0x8120,
        0xB3BB,
        0xA232,
        0x5AC5,
        0x4B4C,
        0x79D7,
        0x685E,
        0x1CE1,
        0x0D68,
        0x3FF3,
        0x2E7A,
        0xE70E,
        0xF687,
        0xC41C,
        0xD595,
        0xA12A,
        0xB0A3,
        0x8238,
        0x93B1,
        0x6B46,
        0x7ACF,
        0x4854,
        0x59DD,
        0x2D62,
        0x3CEB,
        0x0E70,
        0x1FF9,
        0xF78F,
        0xE606,
        0xD49D,
        0xC514,
        0xB1AB,
        0xA022,
        0x92B9,
        0x8330,
        0x7BC7,
        0x6A4E,
        0x58D5,
        0x495C,
        0x3DE3,
        0x2C6A,
        0x1EF1,
        0x0F78,
    ]

    crc = 0xFFFF
    for byte in data:
        crc = (crc >> 8) ^ crc_table[(crc ^ byte) & 0xFF]
    return crc


def main():
    parser = argparse.ArgumentParser(description="Serial Packet Receiver")
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="/dev/ttyUSB0",
        help="Serial port name (e.g. /dev/ttyACM0 or COM3)",
    )
    parser.add_argument(
        "-b", "--baud", type=int, default=115200, help="Baud rate (default: 115200)"
    )
    args = parser.parse_args()

    try:
        # 配置串口参数（与C++配置完全一致）[7](@ref)
        ser = serial.Serial(
            port=args.port,
            baudrate=args.baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.01,  # 缩短超时时间至10ms[5](@ref)
            rtscts=True,  # 启用硬件流控[6,7](@ref)
        )
        print(f"Listening on {args.port} at {args.baud} baud...")
        print("Press Ctrl+C to exit")

        # 清空串口缓冲区[7](@ref)
        ser.reset_input_buffer()

        # 创建接收缓冲区[5](@ref)
        buffer = bytearray()
        last_data_time = time.time()

        while True:
            # 读取所有可用数据（非阻塞）[3,5](@ref)
            data = ser.read(ser.in_waiting or 1)
            if data:
                buffer.extend(data)
                last_data_time = time.time()  # 更新最后接收时间

            # 检查缓冲区中是否有完整数据包（至少12字节）
            while len(buffer) >= 12:
                # 查找包头位置（0xA5）
                header_pos = -1
                for i in range(len(buffer) - 11):
                    if buffer[i] == 0xA5:
                        header_pos = i
                        break

                if header_pos == -1:
                    # 没有找到有效包头，清空缓冲区[1](@ref)
                    buffer.clear()
                    break

                if header_pos > 0:
                    # 跳过无效数据[1](@ref)
                    print(f"⚡ Skip {header_pos} bytes to next header")
                    buffer = buffer[header_pos:]

                # 提取完整数据包
                packet = bytes(buffer[:12])
                buffer = buffer[12:]  # 从缓冲区移除已处理数据

                try:
                    # 解析数据包[2](@ref)
                    header_val, packet_id, x, y, received_checksum = struct.unpack(
                        "<BBffH", packet
                    )

                    # 计算CRC（只计算前10字节）[1](@ref)
                    calculated_crc = crc16_table(packet[:10])

                    # 验证CRC并检查数据合理性[1](@ref)
                    if calculated_crc == received_checksum:
                        # 添加数据范围验证[1](@ref)
                        if -1000 <= x <= 1000 and -1000 <= y <= 1000:
                            print(
                                f"✓ ID: {packet_id:2d} | X: {
                                    x:8.3f} | Y: {y:8.3f} | CRC: OK"
                            )
                        else:
                            print(
                                f"⚠️ Invalid data: ID: {
                                    packet_id} | X: {x} | Y: {y}"
                            )
                    else:
                        print(
                            f"✗ ID: {packet_id:2d} | X: {
                                x:8.3f} | Y: {y:8.3f} | "
                            f"CRC FAIL (calc: 0x{calculated_crc:04X}, recv: 0x{
                                received_checksum:04X})"
                        )
                except struct.error as e:
                    print(f"✗ Packet parsing error: {e}")
                    print(
                        f"Raw packet: {packet.hex().upper()}"
                    )  # 输出原始数据帮助调试[1](@ref)
                except Exception as e:
                    print(f"✗ Unexpected error: {e}")

            # 超时处理：300ms无新数据则清空缓冲区[1](@ref)
            if time.time() - last_data_time > 0.3 and buffer:
                print(f"⌛ Timeout, discarded {len(buffer)} bytes")
                buffer.clear()

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("Possible solutions:")
        print(
            "1. Check port existence and permissions (e.g., sudo chmod 666 /dev/ttyACM0) [6](@ref)"
        )
        print("2. Verify baud rate matches sender configuration [3](@ref)")
        print("3. Ensure no other program is using the serial port [6](@ref)")
        print("4. Check cable quality and connection stability")
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    finally:
        if "ser" in locals() and ser.is_open:
            ser.close()
            print("Serial port closed")


if __name__ == "__main__":
    main()
