# Changelog: arduino-esp32-plugin

All notable changes to this project will be documented in this file.

---

## [1.1.0] - 2026-07-18
### Added
*   **Virtual Emulation & Simulation Core (`arduino_simulator.py`)**: Built a Python-native C++ translation engine to parse Arduino sketches (`setup()`, `loop()`, standard logic structures) and execute them on host-side without requiring QEMU/Docker.
*   **Dynamic Sensor Waveform Emulation**: Enabled `analogRead` mock sensors config in `.cm/simulation_sensors.json` supporting `sine`, `constant`, and `random` sensor patterns.
*   **New MCP Simulation Tools**: Added `start_simulation`, `stop_simulation`, and `get_simulation_status` to `mcp_server.py`.
*   **Integrated Pester Tests**: Added `simulation_core.tests.ps1` and `simulation_mcp.tests.ps1` validating translation accuracy, sensor mock logic, and JSON-RPC subprocess control.

---

## [1.0.0] - 2026-07-18
### Added
*   Initial official release of `arduino-esp32-plugin`.
*   **5 Modular Agent Skills**: `cm-arduino-esp32`, `cm-esp32-env`, `cm-esp32-build`, `cm-esp32-flash`, `cm-esp32-debug`.
*   **Stdio MCP Server (`mcp_server.py`)**: Exposes compilation, physical flashing, background serial logging, stack trace decoding, and GPIO safety audits.
*   **Automated PowerShell Scripts**: `detect_ports.ps1`, `serial_monitor.ps1`, `decode_stack.ps1`, `audit_pins.ps1`.
*   **Bilingual Documentation**: Dual-language guides in `USER_GUIDE_VI.md` (Vietnamese) and `USER_GUIDE_EN.md` (English).
