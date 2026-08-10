# ⚡ ESP32 Master

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/arduino-esp32-plugin)](https://github.com/tody-agent/arduino-esp32-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-Standard%201.0-blueviolet.svg)](https://modelcontextprotocol.io)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)

> **ESP32 Master** là bộ công cụ phát triển phần cứng nhúng **ESP32** chuyên nghiệp, tích hợp máy chủ Model Context Protocol (MCP) dành riêng cho các Trợ lý AI (Cursor, Claude Desktop, Antigravity, Cline, Roo Code) và các Nhà phát triển / Maker phần cứng.

Dự án giải quyết triệt để những nỗi đau lớn nhất khi lập trình vi điều khiển: **Tranh chấp cổng COM (Port Access Denied)**, **Mạch bị crash đơ chỉ in ra chuỗi hex khó hiểu**, **Thiếu giao diện giám sát trực quan**, và **Nguy cơ chập cháy hỏng mạch do khai báo nhầm chân GPIO**.

🇬🇧 **English Version**: Read the full English documentation at [README.md](README.md).

---

## 🌟 Các Tính Năng Đột Phá

### 1. 📱 Giao Diện Web UI ESP32 Mobile Studio (`http://localhost:8321`)
- **Vòng Tròn Nhịp Tim Thiết Bị (Heartbeat Ring)**: Hiển thị trạng thái mạch sống/chết trực quan bằng màu xanh/đỏ thời gian thực.
- **Trợ Lý Sửa Lỗi Tự Động (Smart Repair Assistant)**: Tự động phân tích các chuỗi lỗi hex crash phức tạp thành hướng dẫn khắc phục bằng **Tiếng Việt** dễ hiểu.
- **Nhật Ký Thời Gian Thực (Log Terminal)**: Giao diện dòng lệnh chuẩn font monospace, phân loại màu trực quan (`INFO`, `WARN`, `PANIC`).
- **Bảng Điều Khiển Nhanh 1-Click**: Nút bấm cảm ứng gửi lệnh nhanh (**Bật/Tắt LED**, **Reboot mạch**, **Giải mã Crash Stack**).
- **Thiết Kế Tối Ưu Cho Điện Thoại (Mobile-First)**: Thanh điều hướng lơ lửng bên dưới màn hình, kích thước nút bấm ≥ 48px, không cuộn ngang.

### 2. 🔒 Tự Động Quản Lý Khóa Cổng COM (Zero-Conflict Serial Lock)
- **Tự Động Nhường Cổng COM**: Tự động đóng Serial Monitor khi phát hiện `arduino-cli` tiến hành nạp code (flash) và tự động mở lại monitor ngay sau khi nạp xong. Tránh hoàn toàn lỗi **Access Denied / Port Busy**.

### 3. 🔍 Giải Mã Lỗi Crash Stack Trace 1-Click
- **Chuyển Mã Hex Thành File & Dòng Code**: Dùng công cụ `addr2line` đối chiếu file `.elf` để giải mã các chuỗi địa chỉ hex (`Backtrace: 0x400d1254:0x3ffb1f20...`) thành tên file C++ và **chính xác số dòng code bị lỗi** chỉ trong <2 giây.

### 4. 🧪 Mô Phỏng Logic & Giả Lập Cảm Biến Trên Máy Tính
- **Kiểm Thử Code Không Cần Mạch**: Tự động dịch chuyển logic sketch C++ sang Python để chạy mô phỏng vòng lặp host-side ngay trên máy tính mà không cần cắm mạch thật.
- **Bộ Tạo Sóng Giả Lập**: Tạo tín hiệu cảm biến giả lập (Sóng Sin, Nhiễu ngẫu nhiên, Tăng dần, Hằng số) cho chân cảm biến DHT, biến trở hoặc điện áp.

### 5. 🛡️ Kiểm Tra An Toàn Chân GPIO (Pin Safety Auditor)
- **Bảo Vệ Phần Cứng**: Tự động quét mã nguồn trước khi nạp code để cảnh báo nếu vô tình khai báo sai các chân nạp bootloader (GPIO0, GPIO2, GPIO12, GPIO15) hoặc các chân SPI Flash nội bộ, tránh chập cháy vi điều khiển.

---

## 💎 Bảng So Sánh Nỗi Đau & Giải Pháp

| Nỗi Đau Lập Trình Hardware | Giải Pháp Của ESP32 Master | Lợi Ích Mang Lại |
|---|---|---|
| **Bị báo lỗi Port Busy**<br>Serial Monitor và công cụ nạp tranh cổng COM. | **Cơ chế Khóa Tự Động**<br>Tự đóng monitor khi nạp code và mở lại sau nạp. | **Không còn lỗi bận cổng COM** |
| **Mạch đơ in lỗi Guru Meditation**<br>Toàn dòng lệnh hex không hiểu gì. | **Bộ Giải Mã Stack Trace**<br>Dịch hex thành file C++ & số dòng lỗi chính xác. | **Tìm ra lỗi ngay lập tức** |
| **Log dòng lệnh khó đọc**<br>Khó xem log trên điện thoại di động. | **ESP32 Studio Web UI**<br>Màn hình quản lý trực quan tại `http://localhost:8321`. | **Trải nghiệm UX đẹp & dễ dùng** |
| **Không có sẵn mạch phần cứng**<br>Không test được logic khi đi xa. | **Mô Phỏng Logic Python**<br>Chạy mô phỏng vòng lặp code trên máy tính. | **Kiểm thử logic mọi lúc mọi nơi** |
| **Nguy cơ cháy mạch**<br>Khai báo nhầm chân boot/nguồn. | **Kiểm Tra An Toàn GPIO**<br>Cảnh báo các chân nguy hiểm trước khi nạp. | **An toàn tuyệt đối cho phần cứng** |

---

## 🛠️ Danh Mục 12 Công Cụ MCP (MCP Tools Reference)

`ESP32 Master` đăng ký các công cụ MCP chuẩn hóa giúp Trợ lý AI làm việc tự động:

| Tên Công Cụ MCP | Tham Số Đầu Vào | Mô Tả Chức Năng |
|---|---|---|
| `detect_com_port` | `{ vid?: string, pid?: string }` | Tự động dò tìm cổng COM và thông tin USB CDC của ESP32. |
| `compile_sketch` | `{ sketch_path: string, fqbn?: string }` | Biên dịch file code C++ Arduino sử dụng `arduino-cli`. |
| `upload_sketch` | `{ sketch_path: string, port: string }` | Nạp chương trình xuống chip ESP32 an toàn không đụng cổng. |
| `start_serial_monitor` | `{ port: string, baud?: int }` | Chạy Serial Monitor nền, ghi log ra `.cm/esp32_serial.log`. |
| `read_serial_logs` | `{ lines?: int }` | Đọc các dòng log mới nhất từ Serial Monitor. |
| `send_serial_command` | `{ data: string }` | Gửi chuỗi lệnh xuống cổng Serial thông qua hàng đợi. |
| `decode_stack_trace` | `{ log_text: string, elf_path: string }` | Giải mã chuỗi lỗi hex thành file C++ & dòng code bị crash. |
| `launch_log_dashboard` | `{ port?: int }` | Khởi chạy trang Web UI Studio tại `http://localhost:8321`. |
| `simulate_sketch_logic` | `{ sketch_path: string }` | Dịch logic sketch sang Python để mô phỏng trên PC. |
| `audit_gpio_safety` | `{ sketch_path: string }` | Quét cấu hình chân GPIO để ngăn ngừa chập cháy. |
| `get_board_info` | `{ port: string }` | Lấy thông tin revision chip, địa chỉ MAC, tốc độ Flash. |
| `configure_mock_sensor` | `{ pin: int, waveform: string }` | Cấu hình dạng sóng tín hiệu cảm biến giả lập. |

---

## ⚙️ Hướng Dẫn Cài Đặt Nhanh

### 1. Yêu Cầu Môi Trường
- **Hệ điều hành**: Windows (PowerShell 5.1+)
- **Công cụ biên dịch**: `arduino-cli` đã được thêm vào biến môi trường `PATH`.
- **Python**: Phiên bản 3.8 trở lên.

### 2. Tích Hợp Vào Cấu Hình AI Client

Thêm cấu hình máy chủ MCP vào công cụ AI của bạn (Ví dụ: `%APPDATA%\Claude\claude_desktop_config.json` hoặc trong cài đặt MCP của Cursor / Antigravity):

```json
{
  "mcpServers": {
    "esp32-master": {
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

### 3. Khởi Chạy Web UI Studio Thủ Công

Bạn có thể chạy trực tiếp giao diện Web UI Studio bằng PowerShell:

```powershell
python C:\path-to-plugin\skills\cm-arduino-esp32\scripts\log_dashboard.py
```
Sau đó mở địa chỉ **`http://localhost:8321`** trên trình duyệt máy tính hoặc điện thoại!

---

## 📑 Danh Mục Tài Liệu Chi Tiết

Khám phá bộ tài liệu hướng dẫn chuyên sâu trong thư mục `docs/`:

- 📂 [analysis.md](docs/analysis.md) — Cấu trúc thư mục, luồng thực thi và chi tiết script.
- 👤 [personas.md](docs/personas.md) — Chân dung người dùng (IoT Engineers, AI Agents, Non-Tech Makers).
- 🎯 [jtbd.md](docs/jtbd.md) — Phân tích nhu cầu công việc (JTBD) và tiêu chí thành công.
- 🔒 [flows.md](docs/flows.md) — Sơ đồ Mermaid mô tả luồng nhường cổng Serial và giải mã stack trace.
- 🏗️ [architecture.md](docs/architecture.md) — Kiến trúc lai hybrid engine và nhật ký thiết kế ADR.
- 📖 [SOP: Biên Dịch & Nạp Code](docs/sop/sop-flashing.md) — Quy trình biên dịch và khóa nhường cổng COM.
- 📖 [SOP: Gỡ Lỗi & Giải Mã Crash](docs/sop/sop-debugging.md) — Quy trình giám sát Serial và giải mã lỗi stack trace.
- 📖 [SOP: Mô Phỏng & Giả Lập](docs/sop/sop-simulation.md) — Quy trình chạy mô phỏng logic và cảm biến giả lập.
- 🛠️ [API Reference](docs/api/api-reference.md) — Chi tiết bảng tin JSON-RPC và ví dụ dữ liệu mẫu.

---

## 📄 Giấy Phép Sử Dụng (License)

Dự án được phát hành theo giấy phép bản quyền mở **MIT License**.
