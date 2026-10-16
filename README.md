# StackChan 跳跳老师 — 儿童陪伴机器人全栈方案

M5Stack StackChan（K151）+ 自编译固件 + 本地小智服务器，给两岁半宝宝的 AI 陪伴机器人：
**"跳跳老师"** 中文人设、哪吒主题表情、屏幕字幕、本地儿歌点播。唤醒词用 WakeNet "你好小智"（MultiNet 自定义词在 PR#370 有稳定性 bug，见踩坑记录）。

![哪吒表情](firmware/avatar/pngs/idle.png)

## 硬件

- [M5Stack StackChan](https://docs.m5stack.com/en/StackChan)（K151，CoreS3 底座：ESP32-S3 + 2寸屏 + 双麦 + 双舵机）
- Mac（M 芯片）×1：跑服务器 + 编译/刷固件
- USB-C 数据线（必须支持数据，不是充电线）

## 快速开始（30 分钟）

### 1. 刷固件

```bash
git clone https://github.com/fengenjoy-coder/stackchan-tiaotiao.git
cd stackchan-tiaotiao
pip3 install esptool

# 首次刷入（或救砖）：全量刷机，之后需配网
./scripts/flash_full.sh

# 日常更新固件：只刷 app 分区，保留 WiFi 配置
./scripts/flash_app.sh
```

刷完捅一下 **RST**（卡针轻捅复位孔，别长按——长按 3 秒进刷机模式绿灯）。

### 2. 启动服务器

```bash
cd server
cp data/.config.yaml.example data/.config.yaml
# 编辑 data/.config.yaml：填入你的 DeepSeek API key（https://platform.deepseek.com）
docker compose up -d
```

M 芯片 Mac 已配置 `platform: linux/arm64` 原生镜像（ASR 快 10 倍）；Intel Mac 改成 `linux/amd64`。

服务器起来后，把 `.config.yaml` 里的 `websocket` 地址改成这台 Mac 的局域网 IP：
`ws://<Mac的IP>:8000/xiaozhi/v1/`（`ipconfig getifaddr en0` 查看）。

### 3. 配网（2 分钟，全量刷机后需要）

1. 手机连设备热点 **Xiaozhi-XXXX**（屏幕上有名字）
2. 浏览器开 `http://192.168.4.1`
3. 填家里 WiFi + 服务器地址 `ws://<Mac的IP>:8000/xiaozhi/v1/`
4. 保存，设备自动重启连接

### 4. 测试

- 说 **"你好小智"** → 屏幕哪吒睁眼、字幕条显示识别文字
- 说 **"唱首小星星"** → 播放 `server/music/` 里的歌

往 `server/music/` 丢 mp3，5 分钟内自动入库，无需重启。

## 系统架构

```
说话 → StackChan(本地唤醒: WakeNet "你好小智")
     → Mac docker: FunASR 语音识别(SenseVoiceSmall 本地)
     → DeepSeek 大模型("跳跳老师"人设 prompt)
     → EdgeTTS 语音合成
     → StackChan 播放 + 哪吒表情/口型 + 舵机动作 + 屏幕字幕
     → 点歌: play_music 插件播 server/music/ 本地曲库
```

## 固件特性（基于 stackchan-mcp PR #370 定制）

| 特性 | 说明 |
|---|---|
| 唤醒词 | WakeNet **"你好小智"**（快且稳定；MultiNet 自定义词有 bug，见踩坑第 3 条） |
| 对话模式 | 连续对话：唤醒后可多轮，不用每句都喊 |
| 屏幕形象 | 哪吒 chibi 六表情 + 眨眼/口型（`firmware/avatar/pngs/`） |
| 字幕条 | 识别文字实时显示在屏幕底部（说完约 1 秒内出现） |
| 触摸/摸头 | 点屏幕或摸头也能触发对话（单次按压模式） |
| 版本检查 | 已关闭（无可用 OTA 源，避免弹错打扰） |

## 二次开发

### 换唤醒词（⚠️ MultiNet 模式一次对话后会卡死 AFE 管道，见踩坑第 3 条，生产建议保持 WakeNet）

改 `firmware/sdkconfig.defaults.local` 里：
```
CONFIG_CUSTOM_WAKE_WORD="tiao tiao lao shi"     # 拼音，空格分隔
CONFIG_CUSTOM_WAKE_WORD_DISPLAY="跳跳老师"
CONFIG_CUSTOM_WAKE_WORD_THRESHOLD=15            # 越低越灵敏，误唤醒越多
```

### 换表情形象

`firmware/avatar/pngs/` 是 320×240 PNG（6 表情 + 眼睛/嘴巴变体），
替换后跑 `convert_avatars.py` 重新生成 C 数组（详见脚本注释），重编译。

### 重新编译固件

```bash
# ESP-IDF 5.5.4 环境（参考 https://gitee.com/EspressifSystems/esp-idf）
source ~/esp-idf/export.sh
export IDF_SKIP_CHECK_SUBMODULES=1
cd firmware
python3 scripts/release.py stackchan
# 产物 build/xiaozhi.bin，用 scripts/flash_app.sh 的思路刷入 0x20000
```

源码基于 [kisaragi-mochi/stackchan-mcp](https://github.com/kisaragi-mochi/stackchan-mcp) PR #370 head (21ab663)，
本地修改见 `firmware/patches/`（字幕条功能 + 关闭版本检查）。

## 踩坑记录（血泪）

1. **`xiaozhi.bin` 是 app-only 镜像，刷 0x0 会砖**（`Invalid image block`）。完整镜像 `merged-binary.bin` 刷 0x0
2. **官方 v1.17.0 固件语音唤醒只生效一次**（之后必须摸头），对话式修复在 PR #370，至今未合并
3. **MultiNet 自定义唤醒词有稳定性 bug**：一次对话后 AFE 管道卡死（Ringbuffer FEED full）、唤醒彻底失效——PR #370 只验证过 WakeNet 模式，生产用 WakeNet
3. **PR370 的动作网关（action gateway）不能指向小智服务器**——会卡死音频管道（AFE Ringbuffer 满、设备变聋）。必须留空
5. **OTA 版本检查要么指向能用的源，要么关掉**——固件里已注释掉 `CheckNewVersion()`，重编译时注意保留
6. **M 芯片 Mac 跑服务器务必用 arm64 镜像**——amd64 走 Rosetta 后 ASR 识别要 3 秒且识别率暴跌
7. NVS 存 WiFi/服务器配置在 0x9000 分区，**只刷 0x20000 的 app 分区可以保留配置**；全量刷要重配网
8. esptool 刷完设备可能停在"等待下载"模式，**捅 RST** 即恢复正常开机

## 目录结构

```
firmware/bin/            预编译固件（app + 完整镜像）
firmware/patches/        对 PR370 源码的补丁
firmware/avatar/         哪吒表情生成脚本 + PNG 帧
server/                  docker 服务器（小智 ESP32 服务端）
scripts/                 一键刷机脚本
```

## 后续可玩

- 英语儿歌库扩容（丢 mp3 进 `server/music/`）
- 换豆包/火山引擎 LLM+TTS（国内 API，更快更稳，需 key）
- 流式 ASR 字幕（逐字显示，需讯飞/阿里云/豆包流式 ASR key）
- stackchan-mcp gateway（电脑摄像头联动、姿态跟随等高级玩法）

---

固件上游：[78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) · [kisaragi-mochi/stackchan-mcp](https://github.com/kisaragi-mochi/stackchan-mcp)
服务器：[xinnan-tech/xiaozhi-esp32-server](https://github.com/xinnan-tech/xiaozhi-esp32-server)
