---
title: Codebase Analysis - esp32-master
description: Technical codebase analysis of the ESP32 developer plugin, detailing its structure, scripts, and integration hooks.
keywords: esp32, codebase, structure, scripts, arduino-cli, powershell
robots: index, follow
---

# Codebase Analysis / Phân tích Mã nguồn

This page provides an architectural scan of the `esp32-master` codebase, exposing its layout, key entry points, scripts, and dependencies.

*Trang này phân tích chi tiết cấu trúc thư mục, các script bổ trợ, điểm khởi chạy và dependencies của dự án `esp32-master`.*

---

## 📂 Directory Layout / Cấu trúc Thư mục

```
esp32-master/
├── plugin.json                       # Registers the 5 skills as metadata
├── README.md                         # Bilingual overview & links
├── USER_GUIDE_EN.md                  # Detailed setup in English
├── USER_GUIDE_VI.md                  # Detailed setup in Vietnamese
├── MASTER_PROMPT.md                  # Developer prompt for QEMU simulation
├── CHANGELOG.md                      # Release histories
├── mcp/
│   ├── mcp_server.py                 # Stdio-based Python MCP Server (entry point)
│   └── config_example.json           # Integration sample config
└── skills/                           # Modular Agent Skills
    ├── cm-arduino-esp32/             # Orchestrator & Hardware TDD scripts
    │   ├── SKILL.md                  # Coordination instructions
    │   ├── scripts/                  # Automated scripts (.ps1 & .py)
    │   │   ├── detect_ports.ps1      # COM port scanner
    │   │   ├── serial_monitor.ps1    # Logs serial output & queue listener
    │   │   ├── decode_stack.ps1      # Guru Meditation decrypter
    │   │   ├── audit_pins.ps1        # GPIO pin safety scanner
    │   │   └── arduino_simulator.py  # Python sketch simulator
    │   └── tests/                    # Pester unit tests
    │       ├── detect_ports.tests.ps1
    │       ├── serial_monitor.tests.ps1
    │       ├── decode_stack.tests.ps1
    │       ├── audit_pins.tests.ps1
    │       ├── simulation_core.tests.ps1
    │       └── simulation_mcp.tests.ps1
    ├── cm-esp32-env/                 # Library & Partition manager instructions
    ├── cm-esp32-build/               # Compile cache & LittleFS/SPIFFS packaging
    ├── cm-esp32-flash/               # Serial Flasher & wireless OTA instructions
    └── cm-esp32-debug/               # FreeRTOS debug & crash explanations
```

---

## 🛠️ Key Components Analysis / Chi tiết Thành phần

### 1. The MCP Server Entry Point (`mcp/mcp_server.py`)
*   **Role**: Communicates with the AI client (e.g. Claude, Cursor) using JSON-RPC standard stdio.
*   **Dependencies**: Requires standard Python 3.x libraries (`json`, `subprocess`, `re`, `traceback`, `sys`, `os`). It is **zero-dependency** (no external pip libraries like `mcp` SDK needed) ensuring maximum portability.
*   **Core Logic**: Listens to `stdin` line-by-line, parses requests, routes calls to either local PowerShell scripts or Python handlers, and writes response blocks to `stdout`.

*   **Vai trò**: Cung cấp giao diện JSON-RPC kết nối Agent với các công cụ nhúng qua luồng stdio chuẩn.
*   **Đặc điểm**: Không phụ thuộc vào thư viện ngoài (zero-dependency), đảm bảo chạy ngay trên mọi máy tính Windows đã cài Python.

### 2. Physical Automation Scripts (`skills/cm-arduino-esp32/scripts/`)
*   **`detect_ports.ps1`**: Uses Windows WMI (Windows Management Instrumentation) queries (`Get-CimInstance Win32_PnPEntity`) to scan hardware USB descriptors, identifying COM ports corresponding to CP210x, CH340, and FTDI chips commonly used on ESP32 development boards.
*   **`serial_monitor.ps1`**: Uses the .NET `System.IO.Ports.SerialPort` class to log output at 115200 baud. It automatically suspends itself when a lock file `.cm/upload.lock` is present (so the compiler can flash code) and reconnects afterward. It also reads input from `.cm/serial_input.queue` for bidirectional send.
*   **`decode_stack.ps1`**: Parses crash log lines containing `Backtrace:0x...`. Invokes the ESP32 toolchain's `xtensa-esp32-elf-addr2line.exe` utility with the intermediate ELF file to print the matching source file and line numbers.
*   **`audit_pins.ps1`**: Scans Sketch C++ files using regex matching to find `pinMode(pin, OUTPUT)` declarations on unsafe lines (SPI flash interfaces, UART pins) and reports issues.

*   *`detect_ports.ps1`: Gọi WMI để nhận dạng nhanh chíp nạp (CH340/CP210x) qua cổng USB.*
*   *`serial_monitor.ps1`: Giám sát cổng nối tiếp bằng lớp .NET SerialPort, hỗ trợ đọc file lock và hàng đợi tệp tin.*
*   *`decode_stack.ps1`: Bóc tách mã hex Backtrace và gọi addr2line của toolchain ESP32 để biên dịch ngược dòng code.*
*   *`audit_pins.ps1`: Quét Regex phát hiện pinMode OUTPUT trên chân cấm.*

### 3. Simulation Engine (`skills/cm-arduino-esp32/scripts/arduino_simulator.py`)
*   **Role**: A Python-native sketch interpreter that parses variables, `setup()`, and `loop()` from C++ Arduino sketches, converts them to executable Python, and runs them in a background process.
*   **Features**: Mocks standard core Arduino APIs and implements dynamic analog sensor waveform models (`sine`, `constant`, `random`) configured via `.cm/simulation_sensors.json`.

*   *`arduino_simulator.py`: Bộ máy dịch mã và chạy giả lập logic cục bộ không cần vi điều khiển vật lý.*

---

## 📈 Test Coverage / Bộ Kiểm thử
The codebase features a comprehensive Pester test suite inside `skills/cm-arduino-esp32/tests/` verifying all automated scripts:
1.  `detect_ports.tests.ps1`: Mocks WMI data and checks JSON structure.
2.  `serial_monitor.tests.ps1`: Verifies log writing, lock file handling, and queue-based transmission.
3.  `decode_stack.tests.ps1`: Simulates hex dump parsing and decodes addresses.
4.  `audit_pins.tests.ps1`: Tests safety detection for SPI flash pins.
5.  `simulation_core.tests.ps1`: Tests sketch-to-python translation and sensor mocks.
6.  `simulation_mcp.tests.ps1`: Verifies standard stdio JSON-RPC calls for starting/stopping simulations.
