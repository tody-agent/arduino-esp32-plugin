# ⚡ ESP32 Master

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/esp32-master)](https://github.com/tody-agent/esp32-master/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-Standard%201.0-blueviolet.svg)](https://modelcontextprotocol.io)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)

![Kiến Trúc Hệ Sinh Thái ESP32 Master & AI Agents](docs/assets/esp32_master_hero.jpg)

> **ESP32 Master** là bộ công cụ phát triển phần cứng nhúng **ESP32** chuyên nghiệp, tích hợp máy chủ Model Context Protocol (MCP) dành riêng cho các Trợ lý AI (**Claude Desktop**, **Cursor**, **OpenAI Codex**, **Antigravity**, **Roo Code**, **Cline**) và các Nhà phát triển / Maker phần cứng.

Dự án giải quyết triệt để những nỗi đau lớn nhất khi lập trình vi điều khiển: **Tranh chấp cổng COM (Port Access Denied)**, **Mạch bị crash đơ chỉ in ra chuỗi hex khó hiểu**, **Thiếu giao diện giám sát trực quan**, và **Nguy cơ chập cháy hỏng mạch do khai báo nhầm chân GPIO**.

🇬🇧 **English Version**: Read the full English documentation at [README.md](README.md).

---

## 🚀 Hướng Dẫn Sử Dụng Cùng Trợ Lý AI (Quy Trình 4 Bước)

![Quy Trình 4 Bước Tự Động Hóa Với AI](docs/assets/esp32_studio_webui.jpg)

### 1. 🤖 Ra Lệnh Cho Trợ Lý AI (Claude / Cursor / Codex)
Yêu cầu AI bằng ngôn ngữ tự nhiên:
> *"Viết cho tôi một sketch ESP32 đọc cảm biến nhiệt độ từ chân GPIO4 và điều khiển bật tắt LED qua cổng Serial."*

### 2. 🛡️ Tự Động Kiểm Tra An Toàn GPIO & Biên Dịch
AI gọi công cụ `audit_gpio_safety` để đảm bảo code không chập cháy các chân bootloader, sau đó biên dịch tự động bằng `compile_sketch` qua `arduino-cli`.

### 3. 🔒 Tự Động Nhường Cổng COM (Zero-Conflict Flashing)
AI gọi công cụ `upload_sketch`. Bộ quản lý khóa thông minh **Smart Lock Arbitrator** tự động tạm dừng Serial Monitor, giải phóng cổng COM, nạp code xuống ESP32 và mở lại monitor liên tục mà không bị lỗi bận cổng.

### 4. 💡 Giải Mã Crash Trace 1-Click Ngay Lập Tức
Nếu mạch ESP32 bị lỗi `Guru Meditation Error`, AI hoặc nhà phát triển gọi `decode_stack_trace` để tự động dịch chuỗi lỗi hex thành **file C++ và chính xác số dòng code bị lỗi** trong <2 giây.

---

## 🛠️ Cấu Hình 1-Click & Danh Mục 12 Công Cụ MCP

![Tích Hợp MCP Client & 12 Công Cụ MCP](docs/assets/esp32_stack_decoder.jpg)

### Thêm ESP32 Master Vào Trợ Lý AI

Thêm cấu hình máy chủ MCP vào công cụ AI của bạn (Ví dụ: `%APPDATA%\Claude\claude_desktop_config.json` hoặc trong cài đặt MCP của Cursor / Antigravity):

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

### Danh Mục 12 Công Cụ MCP Đã Đăng Ký

| Tên Công Cụ MCP | Chức Năng & Giá Trị Đem Lại |
|---|---|
| `detect_com_port` | Tự động dò tìm cổng COM và thông tin USB CDC của ESP32. |
| `compile_sketch` | Biên dịch file code C++ Arduino sử dụng `arduino-cli`. |
| `upload_sketch` | Nạp chương trình xuống chip ESP32 an toàn không đụng cổng. |
| `start_serial_monitor` | Chạy Serial Monitor nền, ghi log ra `.cm/esp32_serial.log`. |
| `read_serial_logs` | Đọc các dòng log mới nhất từ Serial Monitor cho AI phân tích. |
| `send_serial_command` | Gửi chuỗi lệnh xuống cổng Serial thông qua hàng đợi. |
| `decode_stack_trace` | Giải mã chuỗi lỗi hex thành file C++ & dòng code bị crash. |
| `launch_log_dashboard` | Khởi chạy trang Web UI Studio tại `http://localhost:8321`. |
| `simulate_sketch_logic` | Dịch logic sketch sang Python để mô phỏng trên PC không cần mạch. |
| `audit_gpio_safety` | Quét cấu hình chân GPIO để ngăn ngừa chập cháy vi điều khiển. |
| `get_board_info` | Lấy thông tin revision chip, địa chỉ MAC, tốc độ Flash. |
| `configure_mock_sensor` | Cấu hình dạng sóng tín hiệu cảm biến giả lập. |

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

## 📱 Giao Diện Web UI ESP32 Mobile Studio (`http://localhost:8321`)

Bên cạnh khả năng tự động hóa 100% qua AI Agent, ESP32 Master tích hợp sẵn giao diện Web UI Studio:
- **Vòng Tròn Nhịp Tim Thiết Bị (Heartbeat Ring)**: Hiển thị trạng thái mạch sống/chết trực quan bằng màu xanh/đỏ thời gian thực.
- **Trợ Lý Sửa Lỗi Tự Động**: Tự động dịch lỗi crash đơ mạch thành hướng dẫn khắc phục ngôn ngữ tự nhiên.
- **Nhật Ký Thời Gian Thực (Log Terminal)**: Giao diện dòng lệnh chuẩn font monospace, phân màu `INFO`, `WARN`, `PANIC`.
- **Bảng Điều Khiển Nhanh 1-Click**: Nút bấm cảm ứng gửi lệnh nhanh (**Bật/Tắt LED**, **Reboot**, **Decode Crash**).
- **Hỗ Trợ Song Ngữ**: Nút đổi ngôn ngữ Tiếng Anh / Tiếng Việt `[ 🌐 VI | 🌐 EN ]` linh hoạt.

---

## ⚙️ Hướng Dẫn Cài Đặt Nhanh

### 1. Yêu Cầu Môi Trường
- **Hệ điều hành**: Windows (PowerShell 5.1+)
- **Công cụ biên dịch**: `arduino-cli` đã được thêm vào biến môi trường `PATH`.
- **Python**: Phiên bản 3.8 trở lên.

### 2. Khởi Chạy Web UI Studio Thủ Công

Bạn có thể chạy trực tiếp giao diện Web UI Studio bằng PowerShell:

```powershell
python C:\path-to-plugin\skills\cm-arduino-esp32\scripts\log_dashboard.py
```
Sau đó mở địa chỉ **`http://localhost:8321`** trên trình duyệt máy tính hoặc điện thoại!

---

## 📑 Danh Mục Tài Liệu Chi Tiết

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
