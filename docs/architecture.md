---
title: System Architecture - arduino-esp32-plugin
description: Technical architecture of the ESP32 plugin, detailing the hybrid automation engine, state caches, and architectural design records.
keywords: architecture, design, hybrid engine, adr, workspace caching
robots: index, follow
---

# System Architecture / Kiến trúc Hệ thống

This document details the architectural decisions (ADRs), workspace states, and the hybrid design of `arduino-esp32-plugin`.

*Tài liệu phân tích kiến trúc hệ thống lai (kết hợp phần cứng và giả lập), cách quản lý dữ liệu lưu vết và các quyết định thiết kế cốt lõi (ADR).*

---

## 🏗️ The Hybrid Automation Engine / Mô hình Lai
The plugin operates in two modes depending on hardware availability:

```
                          ┌──────────────────────────┐
                          │     AI Coding Agent      │
                          └─────────────┬────────────┘
                                        │ (JSON-RPC via Stdio)
                                        ▼
                          ┌──────────────────────────┐
                          │    Python MCP Server     │
                          └──────┬────────────┬──────┘
                                 │            │
             (Physical Mode)     │            │     (Virtual Mode)
            ┌────────────────────┘            └────────────────────┐
            ▼                                                      ▼
  ┌───────────────────┐                                  ┌───────────────────┐
  │ PowerShell Engine │                                  │  Python Simulator │
  └─────────┬─────────┘                                  └─────────┬─────────┘
            │                                                      │
            ▼ (USB/COM)                                            ▼ (.cm/ Cache logs)
  ┌───────────────────┐                                  ┌───────────────────┐
  │  ESP32 Hard chip  │                                  │   Mock Testbench  │
  └───────────────────┘                                  └───────────────────┘
```

1.  **Physical Automation Mode**:
    *   Targets real ESP32 silicon over a physical USB-UART bridge.
    *   Powershell scripts handle COM port lock synchronization and high-fidelity .NET-based serial streaming.
2.  **Virtual Emulation Mode**:
    *   Requires **no physical hardware** or virtualization software (Docker, VirtualBox).
    *   Uses a Python-native translation engine to parse C++ sketch logic and mock CPU registers, IO registers, and analog sensor peripherals on the host.

---

## 📂 Cache Directory State (`.cm/`) / Tổ chức Vùng nhớ Cache
All intermediate outputs, simulation logs, locks, and persistent states are kept inside the `.cm/` workspace cache folder.

*Toàn bộ tệp tin trung gian, trạng thái thiết bị và log truyền nhận được quản lý tại thư mục ẩn `.cm/`:*

| File / Tệp | Type / Loại | Description / Mô tả |
|---|---|---|
| `board_state.json` | JSON Cache | Stores the last-detected COM port and target FQBN (e.g., `esp32:esp32:esp32`). |
| `upload.lock` | Lock Semaphore | If present, signal to the background serial monitor to release the COM port. |
| `serial_input.queue` | ASCII Pipe | Text queue file. Reading or sending commands is simulated by writing to this queue. |
| `esp32_serial.log` | UTF-8 Log | The unified serial output file, shared between physical monitors and virtual runs. |
| `simulator.pid` | Process Tracker| Stores the host process ID of the currently running logic simulation. |
| `simulation_sensors.json` | JSON Config | Holds configuration parameters for mocking analog pins (sine waves, constants, random). |

---

## 📝 Architectural Design Records (ADR)

### ADR 01: Native C++ to Python Translation over QEMU/Docker Virtualization
*   **Context**: Building an virtual emulation system using QEMU-ESP32 or Docker is extremely heavy, slow, and fails on host machines lacking Docker daemon or GCC compilers.
*   **Decision**: Implement a **pure Python-native translation engine** that compiles Arduino C++ structures directly to Python and executes the testbench in a lightweight subprocess.
*   **Consequences**: Zero host-side pre-requisites (extremely easy setup). Very fast execution speeds (< 100ms startup). Perfect for logical verification of loops, calculations, and sensor-based thresholds, though it does not verify raw machine-level assembler code.

*   *Lựa chọn phát triển lõi biên dịch C++ sang Python thay vì ảo hóa QEMU/Docker giúp hệ thống đạt độ nhẹ tối đa (Zero-dependency), khởi chạy lập tức dưới 100ms và không yêu cầu cấu hình môi trường phức tạp.*

### ADR 02: Lock File Semaphores for Serial Port Handshakes
*   **Context**: Windows does not allow multiple processes to open the same COM port simultaneously. Initiating a compilation flash upload while the serial monitor is listening results in a "Port Access Denied" crash.
*   **Decision**: Introduce a `.cm/upload.lock` file as a simple lock semaphore.
*   **Consequences**: The PowerShell monitor checks for the file on every cycle and releases the handle before a conflict occurs, then reclaims it when the lock is deleted. This completely solves port sharing issues.
