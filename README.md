# ESP32 Arduino CLI Developer Plugin

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/arduino-esp32-plugin)](https://github.com/tody-agent/arduino-esp32-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An agent-first developer plugin and Model Context Protocol (MCP) server for professional **ESP32** development using **Arduino CLI** on Windows. It empowers AI agents (like Antigravity, Claude Desktop, Cursor, Cline, Roo Code) with hardware compile, upload, bidirectional serial communication, smart diagnostics, local logic simulation, and CPU crash trace decoding.

🌐 **Tiếng Việt**: Đọc bản tài liệu giới thiệu bằng Tiếng Việt tại [README_VI.md](README_VI.md).

---

## 📑 Documentation Suite

We provide a comprehensive bilingual documentation suite inside the `docs/` directory:

1.  **Codebase Scan / Phân tích nguồn**:
    *   [analysis.md](docs/analysis.md) — Technical layouts, files, and dependencies.
2.  **Design & Strategy / Thiết kế & Chiến lược**:
    *   [personas.md](docs/personas.md) — User profiles (engineers, autonomous agents, educators).
    *   [jtbd.md](docs/jtbd.md) — Jobs-To-Be-Done frameworks and metrics.
3.  **System Layouts / Luồng hoạt động & Kiến trúc**:
    *   [flows.md](docs/flows.md) — Sequence diagrams of monitor locking, stack decoding, and logic translation.
    *   [architecture.md](docs/architecture.md) — Hybrid architecture engine details and ADR design logs.
4.  **SOP Guides / Hướng dẫn Quy trình**:
    *   [sop-flashing.md](docs/sop/sop-flashing.md) — Step-by-step flashing, upload synchronization, and compile diagnostics.
    *   [sop-debugging.md](docs/sop/sop-debugging.md) — Live serial logs, bidirectional queue send, and exception trace translation.
    *   [sop-simulation.md](docs/sop/sop-simulation.md) — Offline local logic simulation, mock sensors, and waveform config.
5.  **Developer API / Tra cứu API**:
    *   [api-reference.md](docs/api/api-reference.md) — Standard 11 JSON-RPC tools, schemas, and call payloads.

To import all files into Google NotebookLM or AI indexes, see the absolute path URL list:
👉 [sitemap-urls.txt](docs/sitemap-urls.txt)

---

## 🛠️ Core Features

*   💻 **Virtual Logic Simulation**: Simulates Arduino sketches offline by translating C++ to executable Python and running them in a lightweight background process.
*   📈 **Mock Waveform Sensors**: Simulates physical sensors (`analogRead`) using configured sine, constant, or random patterns in `simulation_sensors.json`.
*   🔒 **GPIO Safety Auditing (`audit_pins`)**: Scans code before flashing to block compilation if unsafe pins (such as SPI flash pins 6-11) or serial interfaces are driven as outputs, preventing hardware short circuits or bricking.
*   🧠 **Smart Compiler Diagnostics**: Intercepts compiler errors and converts them into structured diagnostics, suggesting the exact library to install on missing headers, or recommending partition configuration modifications for oversized sketches.
*   ⚡ **Bidirectional Serial Monitor**: Supports background serial monitor logging to a file while listening to a file-based command queue (`.cm/serial_input.queue`) for sending data downward to the board.
*   🔍 **Crash Stack Trace Decoding (`decode_crash_stack`)**: Translates ESP32 Guru Meditation backtrace hex addresses back to actual C++ filenames and line numbers using `addr2line`.
*   📦 **Workspace Caching (`board_state.json`)**: Persists the last detected board COM port and FQBN to speed up compilation and flashing cycles.

---

## ⚙️ Quick Integration

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

## 📄 License
This project is licensed under the **MIT License**.
