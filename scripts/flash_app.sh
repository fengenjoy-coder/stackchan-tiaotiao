#!/bin/bash
# 刷入 app 分区（保留 WiFi/服务器配置，日常更新用这个）
# 用法: ./flash_app.sh [串口]   例如 ./flash_app.sh /dev/cu.usbmodem1101
set -e
PORT="${1:-/dev/cu.usbmodem1101}"
python3 -m esptool --chip esp32s3 -p "$PORT" -b 460800 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 16MB \
  0x20000 "$(dirname "$0")/../firmware/bin/xiaozhi.bin"
echo "完成。设备若停在下载模式，捅一下 RST 即可。"
