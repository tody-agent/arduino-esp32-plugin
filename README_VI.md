# ⚡ ESP32 Master

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/esp32-master)](https://github.com/tody-agent/esp32-master/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Server](https://img.shields.io/badge/MCP%20Server-Standard%201.0-blueviolet.svg)](https://modelcontextprotocol.io)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)](https://microsoft.com/windows)

![Hệ Sinh Thái ESP32 Master & Trợ Lý AI](docs/assets/hero_banner.png)

> **ESP32 Master** là bộ công cụ phát triển phần cứng nhúng **ESP32 / ESP32-S3** chuyên nghiệp, tích hợp máy chủ Model Context Protocol (MCP) dành riêng cho các Trợ lý AI (**Claude Desktop**, **Cursor**, **OpenAI Codex**, **Antigravity**, **Roo Code**) và Nhà phát triển phần cứng.

Dự án kết nối trực tiếp các Trợ lý AI với phần cứng vi điều khiển ESP32, tự động biến các câu lệnh ngôn ngữ tự nhiên thành chương trình nạp xuống phần cứng hoàn chỉnh, hỗ trợ giải mã lỗi crash stack trace 1-touch tự động.

🇬🇧 **English Version**: Read the full English documentation at [README.md](README.md).

---

## ⚡ Bảng So Sánh Nỗi Đau & Giải Pháp Đột Phá

![So Sánh Nỗi Đau Lập Trình Truyền Thống vs Giải Pháp ESP32 Master](docs/assets/before_after_comparison.png)

| Nỗi Đau Lập Trình Truyền Thống | Giải Pháp Đột Phá ESP32 Master | Giá Trị Mang Lại |
|---|---|---|
| ❌ **Bị Lỗi Cổng COM Bận (Port Access Denied)**<br>Serial Monitor và uploader tranh nhau cổng COM làm đơ nạp code. | ⚡ **Bộ Quản Lý Khóa Thông Minh**<br>Serial Monitor tự động ngắt kết nối khi nạp code và tự động kết nối lại sau nạp. | **100% Không Lỗi Tranh Cổng** |
| ❌ **Mạch Crash Ra Chuỗi Hex Khó Hiểu**<br>Lỗi `Guru Meditation Error` chỉ in ra chuỗi địa chỉ hex bí ẩn. | ⚡ **Bộ Giải Mã Stack Trace 1-Touch**<br>Tự động dịch chuỗi địa chỉ hex thành chính xác **tên file C++ & số dòng lỗi** trong <2 giây. | **Sửa Lỗi Ngay Lập Tức** |
| ❌ **Giao Diện Dòng Lệnh Khó Dùng**<br>Khó theo dõi log hoặc phát lệnh điều khiển từ thiết bị di động. | ⚡ **ESP32 Mobile & PC Web Studio**<br>Màn hình Web UI trực quan, vòng nhịp tim thiết bị & nút bấm cảm ứng tại `http://localhost:8321`. | **Trải Nghiệm UX Cao Cấp** |
| ❌ **Nguy Cơ Chập Cháy Mạch Nhúng**<br>Khai báo sai các chân bootloader/strapping làm hỏng vi điều khiển. | ⚡ **Bộ Kiểm Tra An Toàn GPIO**<br>Tự động quét cấu hình chân trước khi nạp code để tránh chập mạch. | **An Toàn Phần Cứng Tuyệt Đối** |

---

## 🚀 Quy Trình 4 Bước Tự Động Hóa Với AI

![Quy Trình 4 Bước Tự Động Hóa](docs/assets/infographic_workflow.png)

### 1. 🤖 Ra Lệnh Ngôn Ngữ Tự Nhiên
Yêu cầu **Claude Desktop**, **Cursor**, hoặc **Codex**:
> *"Viết cho tôi một sketch ESP32 đọc cảm biến nhiệt độ chân GPIO4 và điều khiển bật tắt LED."*

### 2. 🛡️ Kiểm Tra An Toàn GPIO & Biên Dịch Tự Động
AI gọi công cụ `audit_gpio_safety` để đảm bảo an toàn phần cứng, sau đó biên dịch bằng `compile_sketch` qua `arduino-cli`.

### 3. 🔒 Nạp Code An Toàn Không Đụng Cổng
AI gọi `upload_sketch`. Bộ **Smart Lock Arbitrator** tự động ngắt Serial Monitor, nhường cổng COM cho uploader nạp code và kết nối lại monitor sau khi hoàn tất.

### 4. 💡 Trợ Lý Sửa Lỗi & Giải Mã Crash
Nếu mạch gặp lỗi `Guru Meditation Error`, AI gọi `decode_stack_trace` để dịch chuỗi hex thành tên file C++ và chính xác số dòng lỗi trong <2 giây.

---

## 📱 Giao Diện Visual Web Studio (`http://localhost:8321`)

![Màn Hình Web UI Studio Dashboard](docs/assets/ui_studio_dashboard.png)

Bên cạnh khả năng tự động hóa 100% qua AI Agent, ESP32 Master tích hợp sẵn giao diện Web UI Studio:
- **Vòng Tròn Nhịp Tim Thiết Bị (Heartbeat Ring)**: Hiển thị trạng thái mạch sống/chết trực quan bằng màu xanh/đỏ thời gian thực.
- **Trợ Lý Sửa Lỗi Tự Động**: Tự động dịch lỗi crash đơ mạch thành hướng dẫn khắc phục ngôn ngữ tự nhiên.
- **Nhật Ký Thời Gian Thực (Log Terminal)**: Giao diện dòng lệnh chuẩn font monospace, phân màu `INFO`, `WARN`, `PANIC`.
- **Bảng Điều Khiển Nhanh 1-Click**: Nút bấm cảm ứng gửi lệnh nhanh (**Bật/Tắt LED**, **Reboot**, **Decode Crash**).
- **Hỗ Trợ Song Ngữ**: Nút đổi ngôn ngữ Tiếng Anh / Tiếng Việt `[ 🌐 VI | 🌐 EN ]` linh hoạt.

---

## 🛠️ Danh Mục 12 Công Cụ MCP Đã Đăng Ký

### Cấu Hình MCP Client

Thêm cấu hình vào AI client của bạn (Ví dụ: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "esp32-master": {
      "command": "python",
      "args": [
        "C:/Adruino/Esp32-Master/mcp/mcp_server.py"
      ],
      "env": {
        "LOCALAPPDATA": "C:/Users/YOUR_USER/AppData/Local"
      }
    }
  }
}
```

### Danh Mục 12 Công Cụ MCP

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

## 📄 Giấy Phép Sử Dụng (License)

Dự án được phát hành theo giấy phép bản quyền mở **MIT License**.
