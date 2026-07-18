---
title: System Flows - process mapping
description: Process flows, lifecycles, and sequence diagrams for compilation, flashing, monitor synchronization, and local logic emulation.
keywords: flows, mermaid, diagrams, architecture flows, serial monitor lock
robots: index, follow
---

# System Flows / Sơ đồ Luồng hoạt động

This page details the operation sequences and synchronization patterns of the `arduino-esp32-plugin`.

*Trang này mô tả các sơ đồ quy trình hoạt động đồng bộ hóa và vòng đời vận hành hệ thống.*

---

## 🔒 1. Serial Monitor & Flashing Sync Flow
To prevent the common "Port Busy" (COM port sharing conflict) error when running compilation/upload tools, the plugin uses a lock file `.cm/upload.lock`.

*Quy trình khóa đồng bộ tránh xung đột cổng COM bằng tệp khóa lock-file.*

```mermaid
sequenceDiagram
    autonumber
    participant Agent as AI Coding Agent / User
    participant MCP as MCP Server (Python)
    participant Mon as Serial Monitor (PowerShell)
    participant CLI as Arduino CLI
    participant HW as Physical ESP32 Board

    Mon->>HW: Open COM Port & read logs
    Note over Mon: Active monitoring...
    Agent->>MCP: Call upload_sketch
    activate MCP
    MCP->>MCP: Create .cm/upload.lock file
    Mon->>Mon: Detect .cm/upload.lock
    Mon->>HW: Release/Close COM Port
    Note over Mon: Waiting...
    MCP->>CLI: run upload command
    CLI->>HW: Flash firmware binary
    Note over HW: Resetting board...
    MCP->>MCP: Remove .cm/upload.lock file
    deactivate MCP
    Mon->>Mon: Detect lock file removed
    Mon->>HW: Re-open COM Port
    Note over Mon: Resumed monitoring...
    Mon->>Agent: Stream logs
```

### Flow Explanation / Giải thích Quy trình
1.  **Monitor Listening**: The PowerShell monitor job is actively reading serial output from the ESP32 board.
2.  **Upload Initiated**: The developer or AI agent calls `upload_sketch` via the MCP server.
3.  **Lock File Creation**: The MCP server creates `.cm/upload.lock`.
4.  **Auto-release**: The background monitor detects this file, immediately closes the COM port, and goes into a waiting state.
5.  **Flashing**: The Arduino CLI safely uploads the binary without port conflicts.
6.  **Unlocking**: Once flashing finishes, the MCP server deletes the `.cm/upload.lock` file.
7.  **Auto-reconnect**: The monitor notices the file is gone, reopens the COM port, and resumes logging.

---

## 🛠️ 2. Guru Meditation Exception Stack Decoding Flow
When the ESP32 crashes, it prints a raw register dump to the serial console. The decoding script maps these hex pointers to C++ line numbers.

*Quy trình bóc tách mã lỗi crash và đối chiếu dòng lệnh C++ nguồn.*

```mermaid
graph TD
    A["Raw Serial Log (Register Dump)"] --> B["Identify 'Backtrace: 0x4008...' pattern via Regex"]
    B --> C["Extract Hex Address pointers"]
    C --> D["Locate compiled firmware ELF file in build cache"]
    D --> E["Invoke xtensa-esp32-elf-addr2line utility"]
    E --> F["Decode addresses to file paths and source lines"]
    F --> G["Return clean C++ call stack report to User/Agent"]
```

### Flow Explanation / Giải thích Quy trình
1.  **Regex Identification**: The decoder searches for the pattern `Backtrace:` followed by one or more hex pointers.
2.  **Addr2line Lookup**: It feeds these pointers into the GNU toolchain `addr2line` utility along with the intermediate `.elf` file built by the compiler.
3.  **Source Mapping**: The output translates addresses to file paths and exact C++ source line numbers.

---

## 💻 3. Virtual Emulation & Waveform Simulation Flow
For offline logic verification, the C++ sketch is translated to Python and runs with sensor waveform mocking.

*Luồng biên dịch giả lập và tạo xung tín hiệu cảm biến ảo.*

```mermaid
graph LR
    subgraph Host PC
        Sketch[".ino Sketch (C++)"] --> Trans["Translator Engine"]
        Trans --> PyRun[".cm/simulation_run.py"]
        PyRun --> Sub["Subprocess Execution"]
        Sub --> Log[".cm/esp32_serial.log"]
        Cfg[".cm/simulation_sensors.json"] -->|Configures analogRead| PyRun
        Queue[".cm/serial_input.queue"] -->|Mocks Serial.read| PyRun
    end
```

### Flow Explanation / Giải thích Quy trình
1.  **Code Translation**: The translation script scans the `.ino` file, removes C++ type specifiers, translates blocks to python indentation, and inserts python mock methods.
2.  **Runtime Emulation**: The generated Python file executes. It maps calls to `analogRead(pin)` to read waveform logic defined in `simulation_sensors.json`.
3.  **I/O Mocking**: Bidirectional communication is fully simulated via log files.
