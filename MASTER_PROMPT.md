# Master Prompt: Hướng dẫn Triển khai Giả lập ESP32 QEMU cho AI Agent

> [!IMPORTANT]
> **Hướng dẫn dành cho AI Agent kế nhiệm:**
> Hãy đọc và thực hiện chính xác theo tài liệu OpenSpec và lộ trình 4 pha dưới đây để nâng cấp bộ plugin `arduino-esp32-plugin` hỗ trợ giả lập ảo bằng QEMU Docker và kiểm thử logic offline.

---

## 1. Triết lý Triển khai (Core Principles)
*   **TDD (Test-Driven Development)**: Luôn viết tệp test Pester (`.tests.ps1`) trước (để xác nhận trạng thái thất bại - RED), sau đó mới viết code sản phẩm để vượt qua test (GREEN).
*   **Windows Native & Zero-dependency**: Không cài thêm thư viện Python hay Node bên ngoài. Chỉ sử dụng PowerShell, Python thư viện chuẩn và các lệnh hệ thống có sẵn (như Docker, arduino-cli).
*   **Tính kế thừa (Backward Compatibility)**: Đảm bảo các tiến trình giả lập xuất log ra cùng định dạng và vị trí để tái sử dụng toàn bộ tool `decode_crash_stack` và `serial_send`.

---

## 2. Nhiệm vụ từng Pha (Phased Deliverables)

### Pha 1: Tích hợp esptool.py & Khởi chạy QEMU Docker
1.  **Viết Test**: Tạo `arduino-esp32-plugin/skills/cm-arduino-esp32/tests/simulation_core.tests.ps1`. Test cần kiểm định việc tạo file `merged-flash.bin` qua `esptool.py` và khởi chạy container QEMU qua lệnh docker.
2.  **Viết Code**:
    *   Tạo script `skills/cm-arduino-esp32/scripts/launch_qemu.ps1` để gộp file bin và khởi chạy container `Esp32QemuSim` sử dụng image `lcgamboa/qemu-esp32`.
3.  **Xác nhận**: Chạy `Invoke-Pester` để pass test.

### Pha 2: Chuyển tiếp cổng Serial ảo & Đồng bộ hóa Log
1.  **Viết Test**: Tạo `tests/virtual_serial.tests.ps1`. Ghi dòng log giả lập từ QEMU Docker và kiểm tra sự xuất hiện trong `.cm/esp32_serial.log`.
2.  **Viết Code**:
    *   Cập nhật `serial_monitor.ps1` thêm tham số `-Virtual` để tự động chuyển dòng log stdout của container QEMU Docker vào tệp log của dự án.
3.  **Xác nhận**: Chạy `Invoke-Pester` để pass test.

### Pha 3: Đăng ký các Công cụ Giả lập trên MCP Server
1.  **Viết Test**: Tạo kiểm thử python `tests/mcp_simulation.tests.py` để verify cấu trúc JSON-RPC của các tool mới.
2.  **Viết Code**:
    *   Sửa `mcp/mcp_server.py`, khai báo và xử lý 3 công cụ mới: `start_simulation`, `stop_simulation`, và `get_simulation_status`.
3.  **Xác nhận**: Xác thực cú pháp Python và chạy test suite.

### Pha 4: Thiết lập Thư viện Mocking Logic (ArduinoFake)
1.  **Viết Test**: Tạo `tests/host_mock.tests.ps1` kiểm tra biên dịch sketch Blink ảo trên Windows.
2.  **Viết Code**:
    *   Tạo thư mục mock headers `skills/cm-arduino-esp32/resources/arduino_fake_headers/` định nghĩa sẵn `Arduino.h`, `Serial`, `pinMode`, v.v.
    *   Tạo script `scripts/test_host_logic.ps1` tự động gọi compiler GCC cục bộ để kiểm định logic code.
3.  **Xác nhận**: Chạy `Invoke-Pester` để pass test.

---

## 3. Lệnh Xác thực Cuối cùng (All Green Verification)
Sau khi kết thúc Pha 4, hãy chạy lệnh sau từ thư mục gốc của dự án để đảm bảo tất cả 4 pha đều hoạt động chính xác:
```powershell
Invoke-Pester -Script .agents/skills/cm-arduino-esp32/tests/
```

Hãy cập nhật lịch sử thay đổi vào tệp `CHANGELOG.md` sau mỗi pha hoàn thành.
