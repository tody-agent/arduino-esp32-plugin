---
title: API Reference - MCP Server Tools
description: Full reference documentation for all 11 JSON-RPC tools exposed by the arduino-esp32-plugin MCP server.
keywords: api, reference, json-rpc, mcp tools, schema
robots: index, follow
---

# API Reference / Tra cứu Công cụ

This page catalogs all 11 JSON-RPC tools exposed by the `arduino-esp32-plugin` MCP Server.

*Bảng tra cứu toàn bộ 11 công cụ được đăng ký trên hệ thống MCP Server.*

---

## 📑 Tools Reference Table / Bảng Tham chiếu

| Tool Name / Tên công cụ | Parameters / Tham số | Description / Mô tả |
|---|---|---|
| **`detect_ports`** | None | Scans USB ports for CP210x, CH340, and FTDI chips; saves state to cache. <br>*Quét cổng COM và lưu cấu hình vào cache.* |
| **`compile_sketch`**| `sketch_path` (string, req)<br>`fqbn` (string, opt)<br>`build_path` (string, opt) | Compiles ESP32 sketches; provides smart compiler warning translations. <br>*Biên dịch mã nguồn Arduino C++.* |
| **`upload_sketch`** | `sketch_path` (string, req)<br>`port` (string, opt)<br>`fqbn` (string, opt) | Uploads binary via serial; automatically handles port locking.<br>*Nạp chương trình xuống chip.* |
| **`start_serial_monitor`**| `port` (string, opt)<br>`baud_rate` (int, opt)<br>`log_path` (string, opt) | Starts serial logger background job.<br>*Chạy ngầm luồng ghi log serial.* |
| **`read_serial_log`**| `log_path` (string, opt)<br>`lines_count` (int, opt) | Returns the last N lines of the serial monitor log.<br>*Đọc N dòng cuối của tệp log.* |
| **`decode_crash_stack`**| `log_text` (string, req)<br>`elf_path` (string, req) | Decodes Guru Meditation hex pointer crash stack to C++ line numbers.<br>*Giải mã lỗi crash sang dòng code nguồn.* |
| **`serial_send`** | `data` (string, req) | Writes data to the serial input queue for physical/virtual monitoring.<br>*Gửi chuỗi dữ liệu xuống serial.* |
| **`audit_pins`** | `sketch_path` (string, req) | Audits sketch pin configurations for safety violations.<br>*Quét phát hiện đấu nối chân GPIO nguy hiểm.* |
| **`start_simulation`**| `sketch_path` (string, req) | Translates C++ sketch to Python and runs logic simulation ngầm.<br>*Khởi chạy giả lập chương trình cục bộ.* |
| **`stop_simulation`** | None | Terminates the background simulation subprocess.<br>*Dừng tiến trình giả lập đang chạy.* |
| **`get_simulation_status`**| None | Returns simulation process state (RUNNING or STOPPED).<br>*Lấy trạng thái tiến trình giả lập.* |

---

## 📋 JSON-RPC Payloads Examples / Ví dụ Yêu cầu mẫu

### 1. `compile_sketch` Request
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 42,
  "params": {
    "name": "compile_sketch",
    "arguments": {
      "sketch_path": "C:/Users/block/Documents/antigravity/jolly-planck/led_blink",
      "fqbn": "esp32:esp32:esp32"
    }
  }
}
```

### 2. `decode_crash_stack` Request
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 43,
  "params": {
    "name": "decode_crash_stack",
    "arguments": {
      "log_text": "Backtrace:0x400810aa:0x3ffb0060 0x400d11bb:0x3ffb0070",
      "elf_path": "C:/Users/block/Documents/antigravity/jolly-planck/.cm/build/led_blink.elf"
    }
  }
}
```

### 3. `start_simulation` Request
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 44,
  "params": {
    "name": "start_simulation",
    "arguments": {
      "sketch_path": "C:/Users/block/Documents/antigravity/jolly-planck/led_blink"
    }
  }
}
```
│
