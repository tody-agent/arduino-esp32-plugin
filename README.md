# ⚡ ESP32 Master

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/esp32-master)](https://github.com/tody-agent/esp32-master/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-Standard%201.0-blueviolet.svg)](https://modelcontextprotocol.io)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)

![ESP32 Master Ecosystem Architecture](docs/assets/esp32_master_hero.jpg)

> **ESP32 Master** is the ultimate AI-first and human-friendly developer suite and Model Context Protocol (MCP) server for professional **ESP32** firmware development using **Arduino CLI**.

Designed specifically for AI-assisted workflows (**Claude Desktop**, **Cursor**, **OpenAI Codex**, **Antigravity**, **Roo Code**, **Cline**) as well as non-tech makers and professional IoT engineers. It eliminates the most frustrating pain points of embedded development: **COM port conflicts**, **cryptic hex stack crashes**, **lack of visual debugging**, and **accidental hardware damage**.

🌐 **Tiếng Việt**: Đọc bản tài liệu tiếng Việt đầy đủ tại [README_VI.md](README_VI.md).

---

## 🚀 How To Use With AI Assistants (4-Step Workflow)

![4-Step AI Automated Workflow](docs/assets/esp32_studio_webui.jpg)

### 1. 🤖 Prompt Your Favorite AI Assistant
Ask **Claude Desktop**, **Cursor**, or **Codex** in natural language:
> *"Write an ESP32 sketch that reads temperature from GPIO4 and controls an onboard LED via Serial commands."*

### 2. 🛡️ Automated GPIO Safety Audit & Build
AI invokes `audit_gpio_safety` to ensure code won't short-circuit boot-strapping pins, then compiles using `compile_sketch` via `arduino-cli`.

### 3. 🔒 Zero-Conflict Flashing
AI invokes `upload_sketch`. ESP32 Master's **Smart Lock Arbitrator** auto-pauses the serial monitor, releases the COM port, flashes the binary, and re-engages logging seamlessly.

### 4. 💡 Instant 1-Click Crash Debugging
If the ESP32 encounters a `Guru Meditation Error`, AI or developer invokes `decode_stack_trace` to translate raw hex dumps into exact C++ filenames and line numbers in <2 seconds.

---

## 🛠️ 1-Click Setup & 12 MCP Tools Reference

![MCP Config & Registered Tools](docs/assets/esp32_stack_decoder.jpg)

### Adding ESP32 Master to AI Clients

Add `esp32-master` to your AI desktop client config (e.g. `%APPDATA%\Claude\claude_desktop_config.json` or Cursor / Antigravity settings):

```json
{
  "mcpServers": {
    "esp32-master": {
      "command": "python",
      "args": [
        "C:/path-to-plugin/esp32-master/mcp/mcp_server.py"
      ],
      "env": {
        "LOCALAPPDATA": "C:/Users/YOUR_USER/AppData/Local"
      }
    }
  }
}
```

### Complete MCP Tools List

| Tool Name | Key Function & Value |
|---|---|
| `detect_com_port` | Auto-detects connected ESP32 COM port and USB CDC details. |
| `compile_sketch` | Compiles Arduino C++ sketch using `arduino-cli`. |
| `upload_sketch` | Safely flashes binary to ESP32 with zero COM port conflicts. |
| `start_serial_monitor` | Launches background serial monitor with `.cm/serial_input.queue`. |
| `read_serial_logs` | Reads live serial log stream for AI analysis. |
| `send_serial_command` | Enqueues command strings to serial monitor input queue. |
| `decode_stack_trace` | Translates raw hex stack trace to exact C++ source file & line numbers. |
| `launch_log_dashboard` | Launches mobile & desktop Web UI Studio at `http://localhost:8321`. |
| `simulate_sketch_logic` | Translates C++ logic to Python for host-side simulation without hardware. |
| `audit_gpio_safety` | Audits pin initialization to prevent short circuits & bricked boards. |
| `get_board_info` | Reads ESP32 chip revision, MAC address, and flash speed. |
| `configure_mock_sensor` | Configures simulated pin waveform output for testbenches. |

---

## 💎 Pain Point vs. Solution Matrix

| Hardware Pain Point | ESP32 Master Solution | Benefit |
|---|---|---|
| **Port Access Denied**<br>Serial monitor and uploader fight for COM port. | **Automatic Lock Arbitration**<br>Serial monitor auto-pauses when upload starts. | **Zero Port Conflicts** |
| **Guru Meditation Crash**<br>Raw hex register dumps hard to read. | **Stack Trace Decrypter**<br>Translates hex addresses to file & line numbers in <2s. | **Instant Root Cause Fix** |
| **Command Line Logs**<br>Hard to filter or view on mobile devices. | **ESP32 Studio Web UI**<br>Visual dashboard at `http://localhost:8321`. | **Intuitive Monitoring** |
| **No Board Attached**<br>Can't test sketch logic offline. | **Python Logic Simulator**<br>Translates C++ loops to host-side Python. | **Offline TDD Testing** |
| **Bricked Hardware**<br>Accidentally driving boot pins. | **GPIO Safety Auditor**<br>Scans code for dangerous pin modes before flashing. | **Hardware Safety** |

---

## 📱 Web UI Mobile & Desktop Studio (`http://localhost:8321`)

In addition to full AI agent automation, ESP32 Master includes a visual web studio:
- **Visual Heartbeat Ring**: Real-time pulsing status indicator showing ESP32 health.
- **Smart Repair Assistant**: Translates crash stack dumps into plain-language repair steps.
- **Real-Time Log Stream**: Monospaced terminal with live filtering (`INFO`, `WARN`, `PANIC`).
- **Touch-Friendly Controls**: 1-click serial command buttons (**LED ON/OFF**, **Reboot**, **Decode Crash**).
- **Mobile-First Design**: Floating bottom nav bar, 48px+ touch targets, bilingual i18n support.

---

## ⚙️ Quick Start Guide

### 1. Prerequisites
- **OS**: Windows (PowerShell 5.1+)
- **Toolchain**: `arduino-cli` configured on your system `PATH`
- **Python**: Version 3.8+

### 2. Manual Web UI Studio Launch

Run the Web UI Studio directly from PowerShell:

```powershell
python C:\path-to-plugin\skills\cm-arduino-esp32\scripts\log_dashboard.py
```
Open **`http://localhost:8321`** in any browser or mobile device.

---

## 📑 Documentation Sitemap

- 📂 [analysis.md](docs/analysis.md) — Structural layout, entry points, and script details.
- 👤 [personas.md](docs/personas.md) — Target user profiles (IoT Engineers, AI Agents, Non-Tech Makers).
- 🎯 [jtbd.md](docs/jtbd.md) — Functional/emotional Jobs-To-Be-Done and success metrics.
- 🔒 [flows.md](docs/flows.md) — Mermaid diagrams for serial lock arbitration and stack decoding.
- 🏗️ [architecture.md](docs/architecture.md) — Hybrid architecture engine details and design records.
- 📖 [SOP: Compiling & Flashing](docs/sop/sop-flashing.md) — Compilation and upload lock management.
- 📖 [SOP: Debugging & Decoding](docs/sop/sop-debugging.md) — Serial monitoring and stack trace decoding.
- 📖 [SOP: Simulation & Mocks](docs/sop/sop-simulation.md) — Logic simulation and sensor mock testing.
- 🛠️ [API Reference](docs/api/api-reference.md) — Complete JSON-RPC schemas and payload examples.

---

## 📄 License

This project is licensed under the **MIT License**.
