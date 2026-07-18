---
title: SOP - Compiling and Flashing Firmware
description: Step-by-step Standard Operating Procedure for compiling and flashing ESP32 sketches.
keywords: sop, flashing, compile, upload, arduino-cli
robots: index, follow
---

# SOP: Compiling and Flashing Firmware / Hướng dẫn Biên dịch & Nạp Code

This guide outlines the Standard Operating Procedure (SOP) for compiling Arduino C++ sketches and uploading them to ESP32 microcontrollers.

*Hướng dẫn các bước biên dịch mã nguồn C++ và nạp chương trình xuống vi điều khiển ESP32.*

---

## 🛠️ Step 1: Detect Connected Devices / Nhận diện Thiết bị
Before compilation, identify which COM port is connected to the ESP32 board.

1.  Open the workspace command console.
2.  Call the MCP tool `detect_ports`.
3.  The tool scans system USB descriptors and writes the default configuration to cache:
    ```json
    {
      "port": "COM4",
      "name": "Silicon Labs CP210x USB to UART Bridge",
      "fqbn": "esp32:esp32:esp32"
    }
    ```

*Gọi công cụ `detect_ports` để quét thiết bị USB nạp. Kết quả sẽ tự động lưu lại trong bộ nhớ cache để tái sử dụng ở các bước tiếp theo.*

---

## 🏗️ Step 2: Compile the Sketch / Biên dịch Chương trình
Compile the sketch to verify syntax and generate intermediate binary files.

1.  Call the MCP tool `compile_sketch` with your sketch directory path:
    ```json
    {
      "sketch_path": "C:/Users/block/Documents/antigravity/jolly-planck/my_project"
    }
    ```
2.  **Diagnostics Analysis**:
    *   If compilation succeeds: Returns exit code `0` and paths to the generated `.bin` and `.elf` files.
    *   If compilation fails: The server automatically parses the compiler stderr output, providing detailed explanations (e.g. missing libraries, program size exceeding partition constraints, syntax errors).

*Gọi công cụ `compile_sketch`. Nếu xảy ra lỗi cú pháp hoặc thiếu thư viện, máy chủ sẽ tự động phân tích và đưa ra giải pháp khắc phục bằng tiếng Việt.*

---

## ⚡ Step 3: Upload Sketch / Nạp Chương trình
Upload the compiled binary to the ESP32 chip.

1.  Call the MCP tool `upload_sketch`.
2.  The tool checks `.cm/board_state.json` to extract the cached COM port and FQBN automatically.
3.  **Serial Port Handshake**:
    *   The tool creates `.cm/upload.lock`.
    *   Any active background `start_serial_monitor` task immediately releases its COM port handle.
    *   `arduino-cli` flashes the board.
    *   The tool deletes `.cm/upload.lock` and the monitor re-opens the port.

*Gọi công cụ `upload_sketch`. Cổng COM sẽ tự động được giải phóng để nạp code mà không lo xung đột port.*

---

## ❓ Troubleshooting / Xử lý Sự cố

::: warning CẢNH BÁO: Lỗi Access Denied (COM Port Busy)
If you get a "Port Access Denied" error during uploads, verify if a third-party application (such as Putty, Arduino IDE Serial Monitor, or ESP-IDF Monitor) is holding the COM port open. Make sure to close external monitors first.
:::
