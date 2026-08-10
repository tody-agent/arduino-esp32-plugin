# ESP32 Arduino CLI Developer Plugin (Tiếng Việt)

[![GitHub Release](https://img.shields.io/github/v/release/tody-agent/arduino-esp32-plugin)](https://github.com/tody-agent/arduino-esp32-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Bộ plugin và máy chủ Model Context Protocol (MCP) chuyên dụng hỗ trợ các AI Agent (như Antigravity, Claude Desktop, Cursor, Cline, Roo Code) phát triển dự án vi điều khiển **ESP32** sử dụng **Arduino CLI** trên hệ điều hành Windows. Bộ công cụ giúp biên dịch, nạp chương trình, giám sát serial hai chiều, kiểm định an toàn chân cắm, giải mã lỗi crash CPU và chạy giả lập logic offline.

---

## 📑 Bộ Tài liệu Chuẩn hóa

Chúng tôi cung cấp bộ tài liệu song ngữ toàn diện tại thư mục `docs/`:

1.  **Phân tích Mã nguồn**:
    *   [analysis.md](docs/analysis.md) — Chi tiết cấu trúc thư mục, các script bổ trợ và dependencies.
2.  **Thiết kế & Chiến lược**:
    *   [personas.md](docs/personas.md) — Hồ sơ các nhóm người dùng mục tiêu (Embedded Developer, AI Coding Agent, Educator).
    *   [jtbd.md](docs/jtbd.md) — Khảo sát Jobs-To-Be-Done và các chỉ số đo lường hiệu quả.
3.  **Sơ đồ Luồng hoạt động & Kiến trúc**:
    *   [flows.md](docs/flows.md) — Sơ đồ tuần trình khóa cổng serial, giải mã lỗi và giả lập logic.
    *   [architecture.md](docs/architecture.md) — Giải thích kiến trúc hệ thống lai (Hybrid Engine) và nhật ký thiết kế ADR.
4.  **Hướng dẫn Quy trình SOP**:
    *   [sop-flashing.md](docs/sop/sop-flashing.md) — Hướng dẫn biên dịch, nạp code và xử lý lỗi nạp.
    *   [sop-debugging.md](docs/sop/sop-debugging.md) — Hướng dẫn giám sát log, truyền lệnh nối tiếp và dịch ngược lỗi CPU crash.
    *   [sop-simulation.md](docs/sop/sop-simulation.md) — Hướng dẫn cấu hình sóng cảm biến và chạy máy ảo logic offline.
5.  **Tra cứu API công cụ**:
    *   [api-reference.md](docs/api/api-reference.md) — Tham chiếu 11 công cụ JSON-RPC đăng ký trên MCP server.

Để nạp bộ tài liệu này vào Google NotebookLM phục vụ tra cứu AI, tham khảo danh sách đường dẫn tuyệt đối:
👉 [sitemap-urls.txt](docs/sitemap-urls.txt)

---

## 🛠️ Tính năng nổi bật

*   💻 **Giả lập Logic Offline**: Chuyển đổi mã nguồn C++ sang mã Python và chạy giả lập logic ngầm ngay trên máy tính mà không cần kết nối với mạch thật.
*   🖥️ **Trang Visual Log Debugger Web UI**: Giao diện Web trực quan (tại `http://localhost:8321`) theo dõi log thời gian thực, 1-click giải mã lỗi crash Backtrace, kiểm định an toàn GPIO và gửi lệnh nối tiếp 2 chiều.
*   📈 **Tạo tín hiệu cảm biến giả lập**: Mô phỏng cảm biến đọc giá trị chân pin (`analogRead`) dạng sóng hình sin, hằng số hoặc ngẫu nhiên thông qua cấu hình trong `simulation_sensors.json`.
*   🔒 **Kiểm định an toàn GPIO (`audit_pins`)**: Tự động phát hiện việc khai báo chân cấm (như chân SPI flash 6-11) làm ngõ ra, chặn nạp code để tránh gây chập cháy thiết bị.
*   🧠 **Chẩn đoán biên dịch thông minh**: Phân tích lỗi stderr và tự động gợi ý tải thư viện còn thiếu hoặc tùy chỉnh bảng phân vùng nhớ cho chương trình dung lượng lớn.
*   ⚡ **Giám sát Serial hai chiều**: Ghi log serial ngầm ra tệp tin đồng thời hỗ trợ gửi lệnh điều khiển từ AI Agent xuống mạch qua hàng đợi lệnh.
*   🔍 **Giải mã lỗi CPU Crash (`decode_crash_stack`)**: Đọc log Backtrace của ESP32 Guru Meditation Error và dịch ngược trực tiếp ra đường dẫn file và số dòng code C++ lỗi.
*   📦 **Bộ nhớ đệm Workspace (`board_state.json`)**: Tự động ghi nhớ cấu hình cổng nạp và FQBN của bo mạch để tối ưu tốc độ thực thi.

---

## ⚙️ Cài đặt & Tích hợp

Thêm cấu hình máy chủ MCP vào tệp cấu hình AI Agent của bạn (ví dụ: `%APPDATA%\Claude\claude_desktop_config.json`):

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
