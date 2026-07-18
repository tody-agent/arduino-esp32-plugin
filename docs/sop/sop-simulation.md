---
title: SOP - Local Logic Simulation and Sensor Mocking
description: Step-by-step Standard Operating Procedure for running the Python-native simulation engine and configuring mock sensor waveforms.
keywords: sop, simulation, mock, sensors, logic verification, python simulator
robots: index, follow
---

# SOP: Local Logic Simulation & Sensor Mocking / Giả lập Logic & Cảm biến ảo

This guide outlines the Standard Operating Procedure (SOP) for testing firmware logic offline using the Python-native simulation engine and configuring mock sensor configurations.

*Hướng dẫn chi tiết quy trình chạy giả lập chương trình cục bộ và thiết lập đồ thị cảm biến ảo phục vụ kiểm thử.*

---

## 💻 Step 1: Run Simulation / Khởi động Trình Giả lập
Simulate sketch execution on your local development machine.

1.  Call the MCP tool `start_simulation` specifying the target sketch path:
    ```json
    {
      "sketch_path": "C:/Users/block/Documents/antigravity/jolly-planck/my_project"
    }
    ```
2.  The engine translates the C++ syntax structure to executable Python and spawns a background subprocess.
3.  Virtual serial logs are written to `.cm/esp32_serial.log` (identical destination to the physical monitor logs).

*Gọi `start_simulation`. Lõi dịch mã sẽ chuyển đổi mã nguồn C++ sang cấu trúc Python tương ứng và chạy ngầm dưới dạng tiến trình nền.*

---

## 📈 Step 2: Configure Mock Sensors / Cấu hình Cảm biến ảo
Verify how your loop logic reacts to specific sensor inputs (e.g. high temperatures, voltage drops, cyclical patterns) by configuring virtual waveform generators on analog pins.

1.  Create or update the configuration file `.cm/simulation_sensors.json` in your workspace.
2.  Specify the target pins and desired behavior (e.g. constant, random, or cyclical sine wave patterns):
    ```json
    {
      "34": {
        "type": "sine",
        "min": 1000,
        "max": 3000,
        "period_seconds": 10
      },
      "35": {
        "type": "constant",
        "value": 2048
      },
      "36": {
        "type": "random",
        "min": 0,
        "max": 100
      }
    }
    ```
3.  Any calls to `analogRead(pin)` inside the running sketch will dynamically compute values according to this configuration.

*Tạo tệp cấu hình `.cm/simulation_sensors.json` để mô phỏng tín hiệu ở các ngõ vào của chân analogRead. Trình dịch hỗ trợ tạo sóng hình sin tuần hoàn, phát số ngẫu nhiên hoặc gán hằng số.*

---

## 📥 Step 3: Interactive Verification / Truyền dữ liệu tương tác
Test logic reaction by writing commands.

1.  Use `serial_send` to write strings (e.g. command inputs) to the simulation queue.
2.  The simulator checks `.cm/serial_input.queue` on every cycle, pushes characters to the `Serial` input buffer, and deletes the queue file.
3.  Check the status of the simulation process using `get_simulation_status` or stop it using `stop_simulation`.

*Dùng công cụ `serial_send` để gửi lệnh điều khiển và gọi `stop_simulation` khi muốn kết thúc.*
