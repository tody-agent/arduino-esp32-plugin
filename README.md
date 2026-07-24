# ESP32 Arduino CLI Developer Plugin & MCP Server

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/arduino-esp32-plugin)](https://github.com/tody-agent/arduino-esp32-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An agent-first developer plugin and Model Context Protocol (MCP) server for professional **ESP32** firmware development using **Arduino CLI** on Windows. 

Designed specifically for AI-assisted workflows (Cursor, Claude Desktop, Cline, Roo Code, Antigravity) and human developers, it solves the most painful pain points of hardware development: COM port lock conflicts, hard-to-read register crash logs, lack of offline logical testing, and accidental hardware damage.

🌐 **Tiếng Việt**: Đọc bản tài liệu giới thiệu bằng Tiếng Việt tại [README_VI.md](README_VI.md).

---

## 💎 The Value Proposition: Why Choose This Plugin?

Firmware development is traditionally prone to interruption and friction. Here is how this plugin solves these issues:

| Pain Point | The Solution | Core Value |
|---|---|---|
| **Port Access Denied**<br>Serial monitors and upload tools fight for the same COM port. | **Automatic Lock Synchronization**<br>The monitor detects compiler activity, automatically closes the port, and reopens it after flashing. | **Zero "Port Busy" Errors**<br>No manual clicking or disconnecting needed. |
| **Confusing Register Dumps**<br>Guru Meditation crashes print raw hex stacks. | **Real-Time Stack Decrypter**<br>Translates hex addresses to file paths and C++ line numbers using `addr2line`. | **Instant Debugging**<br>Find the exact line that caused the crash in <2 seconds. |
| **No Board Attached**<br>Can't test or verify loop logic while offline or flying. | **Python-Native Logic Simulator**<br>Translates C++ Arduino code to Python and executes sketch logic host-side. | **Offline Logical TDD**<br>Verify loops, variables, and state machines offline. |
| **Unpredictable Sensors**<br>Testing extreme values at your desk is difficult. | **Mock Waveform Configurations**<br>Configures simulated pins to output constant values, random noise, or sine waves. | **Reproducible Testbenches**<br>Mock DHT, potentiometer, or threshold values. |
| **Bricked Hardware**<br>Accidentally driving boot pins or SPI lines as output. | **GPIO Pin Auditing**<br>Scans the code before flashing and warns of dangerous configurations. | **Hardware Safety**<br>Protects physical microcontrollers from short circuits. |

---

## 📑 Documentation Suite

Read the full guides inside the `docs/` folder:

*   📂 [analysis.md](docs/analysis.md) — Structural layout, entry points, and script details.
*   👤 [personas.md](docs/personas.md) — Targeted user profiles (IoT Engineers, AI coding agents, Educators).
*   🎯 [jtbd.md](docs/jtbd.md) — Functional and emotional jobs, success metrics, and user journey.
*   🔒 [flows.md](docs/flows.md) — Mermaid diagrams mapping serial monitor locking, stack decoding, and logic translation.
*   🏗️ [architecture.md](docs/architecture.md) — Hybrid architecture engine details and ADR design logs.
*   📖 [SOP: Compiling & Flashing](docs/sop/sop-flashing.md) — Guide for build compilation and flash locking.
*   📖 [SOP: Debugging & Decoding](docs/sop/sop-debugging.md) — Guide for serial monitors, command queues, and stack trace decryption.
*   📖 [SOP: Simulation & Mocks](docs/sop/sop-simulation.md) — Guide for running logic simulations and waveform config files.
*   🛠️ [api-reference.md](docs/api/api-reference.md) — Standard 11 JSON-RPC tools, schemas, and payload examples.

*To import the entire documentation suite into Google NotebookLM, load the absolute path list in [sitemap-urls.txt](docs/sitemap-urls.txt).*

---

## ⚙️ Quick Start & Integration

### 1. Requirements
*   **OS**: Windows
*   **Toolchain**: `arduino-cli` configured on your environment `PATH`.
*   **Python**: Version 3.x.

### 2. Integration with AI Clients
Add this server to your AI desktop client config (e.g. `%APPDATA%\Claude\claude_desktop_config.json`):

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
