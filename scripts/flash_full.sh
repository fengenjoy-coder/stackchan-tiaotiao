#!/bin/bash
# 全量刷机（清空前 16MB，WiFi 配置丢失需重新配网，救砖/首次刷入用这个）
# 用法: ./flash_full.sh [串口]
set -e
PORT="${1:-/dev/cu.usbmodem1101}"
python3 -m esptool --chip esp32s3 -p "$PORT" erase_flash
python3 -m esptool --chip esp32s3 -p "$PORT" -b 460800 \
  write_flash -z --flash_mode dio --flash_freq 80m --flash_size 16MB \
  0x0 "$(dirname "$0")/../firmware/bin/merged-binary.bin"
echo "完成。捅一下 RST，然后手机配网: 连热点 Xiaozhi-XXXX -> http://192.168.4.1"
