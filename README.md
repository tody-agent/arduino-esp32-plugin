# ESP32 Arduino CLI Developer Plugin

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/arduino-esp32-plugin)](https://github.com/tody-agent/arduino-esp32-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An agent-first developer plugin and Model Context Protocol (MCP) server for professional **ESP32** development using **Arduino CLI** on Windows. It empowers AI agents (like Antigravity, Claude Desktop, Cursor, Cline, Roo Code) with hardware compile, upload, bidirectional serial communication, smart diagnostics, and CPU crash trace decoding.

Bộ plugin và máy chủ MCP hỗ trợ AI Agent phát triển chuyên nghiệp trên dòng chip **ESP32** sử dụng **Arduino CLI** trên Windows. Giúp Agent có khả năng tự động kiểm định an toàn phần cứng, biên dịch, nạp code, giám sát nối tiếp hai chiều và giải mã lỗi CPU crash thời gian thực.

---

## Language Guides / Hướng dẫn theo Ngôn ngữ

*   🇺🇸 **English**: Read the full setup & usage instructions in [USER_GUIDE_EN.md](USER_GUIDE_EN.md).
*   🇻🇳 **Tiếng Việt**: Đọc hướng dẫn cài đặt & sử dụng chi tiết bằng tiếng Việt tại [USER_GUIDE_VI.md](USER_GUIDE_VI.md).

---

## Core Features / Các Tính năng Chính

*   🔒 **GPIO Safety Auditing (`audit_pins`)**: Scans code before flashing to block compilation if unsafe pins (such as SPI flash pins 6-11) or serial interfaces are driven as outputs, preventing hardware short circuits or bricking.
    *   *Kiểm định an toàn GPIO (`audit_pins`): Quét code trước khi nạp để cảnh báo các chân cấm (như SPI flash 6-11) tránh chập mạch hoặc làm đơ chip.*
*   🧠 **Smart Compiler Diagnostics**: Intercepts compiler errors and converts them into structured diagnostics, suggesting the exact library to install on missing headers, or recommending partition configuration modifications for oversized sketches.
    *   *Chẩn đoán lỗi thông minh: Phân tích lỗi compiler và gợi ý trực quan (ví dụ: tên thư viện cần tải, thuộc tính phân vùng cần cấu hình lại).*
*   ⚡ **Bidirectional Serial Monitor**: Supports background serial monitor logging to a file while listening to a file-based command queue (`.cm/serial_input.queue`) for sending data downward to the board.
    *   *Giám sát Serial 2 chiều: Chạy ghi log nối tiếp ngầm đồng thời hỗ trợ ghi lệnh điều khiển trực tiếp từ Agent xuống mạch qua hàng đợi lệnh.*
*   🔍 **Crash Stack Trace Decoding (`decode_crash_stack`)**: Translates ESP32 Guru Meditation backtrace hex addresses back to actual C++ filenames and line numbers using `addr2line`.
    *   *Giải mã lỗi CPU crash: Chuyển đổi mã hex Backtrace của ESP32 Guru Meditation Error về file code và số dòng cụ thể.*
*   📦 **Workspace Caching (`board_state.json`)**: Persists the last detected board COM port and FQBN to speed up compilation and flashing cycles.
    *   *Bộ nhớ đệm Workspace: Tự động ghi nhớ cấu hình bo mạch và cổng COM để Agent thực thi biên dịch/nạp nhanh mà không cần quét lại.*

---

## Directory Structure / Cấu trúc Thư mục

```
arduino-esp32-plugin/
├── plugin.json                       # Plugin metadata (registers the 5 skills)
├── README.md                         # This file
├── USER_GUIDE_EN.md                  # Comprehensive English User Guide
├── USER_GUIDE_VI.md                  # Comprehensive Vietnamese User Guide
├── mcp/
│   ├── mcp_server.py                 # Stdio-based Python MCP Server (zero-dependency)
│   └── config_example.json           # Example config for IDEs/Clients
└── skills/                           # 5 Modular Agent Skills
    ├── cm-arduino-esp32/             # Orchestrator & Hardware TDD scripts
    ├── cm-esp32-env/                 # Library & Partition manager
    ├── cm-esp32-build/               # Compile cache & Filesystem (LittleFS/SPIFFS)
    ├── cm-esp32-flash/               # Serial Flasher & ArduinoOTA wireless
    └── cm-esp32-debug/               # FreeRTOS debug, memory leak, WDT, crash decrypter
```

---

## Quick Setup / Cài đặt Nhanh

### 1. Requirements / Yêu cầu
*   **OS**: Windows
*   **Toolchain**: `arduino-cli` installed and configured on User `PATH` (see instructions inside the guides).
*   **Python**: Version 3.x (to run the stdio MCP server).

### 2. Integration / Tích hợp
Add this server to your AI agent config (e.g. `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "arduino-esp32-mcp": {
      "command": "python",
      "args": [
        "C:/path-to-plugin/arduino-esp32-plugin/mcp/mcp_server.py"
      ],
      "env": {
        "LOCALAPPDATA": "C:/Users/YOUR_USER/AppData/Local"
      }
    }
  }
}
```

---

## License / Giấy phép
This project is licensed under the **MIT License**. See full details in guides.
