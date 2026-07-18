---
title: SOP - Serial Debugging and Crash Decoding
description: Step-by-step Standard Operating Procedure for monitoring ESP32 serial output and decoding crash stack traces.
keywords: sop, debugging, serial monitor, crash, decode, backtrace, addr2line
robots: index, follow
---

# SOP: Serial Debugging & Crash Decoding / Hướng dẫn Gỡ lỗi & Dịch Crash

This guide outlines the Standard Operating Procedure (SOP) for monitoring ESP32 serial logs, sending serial commands, and decoding register backtrace errors.

*Hướng dẫn chi tiết quy trình theo dõi log Serial, truyền lệnh điều khiển và giải mã ngược lỗi crash vi điều khiển.*

---

## 📈 Step 1: Start Serial Monitor / Khởi chạy Giám sát Serial
Keep a continuous background listener on the board's serial port.

1.  Call the MCP tool `start_serial_monitor` (uses cached COM port and default 115200 baud).
2.  Logs are written continuously to `.cm/esp32_serial.log`.
3.  To read the latest log output, call `read_serial_log` with the number of lines required (default `50`).

*Gọi `start_serial_monitor` để bắt đầu ghi log cổng COM chạy ẩn. Dùng `read_serial_log` bất kỳ lúc nào để lấy nhanh dữ liệu log mới nhất.*

---

## 📥 Step 2: Send Serial Commands / Truyền dữ liệu xuống Board
Send configuration strings or instructions to the running firmware.

1.  Call the MCP tool `serial_send` with the payload string:
    ```json
    {
      "data": "SET_THRESHOLD:25"
    }
    ```
2.  The payload is queued in `.cm/serial_input.queue`.
3.  The active serial monitor reads this queue, writes it to the ESP32 UART RX pin, and deletes the queue.

*Gọi `serial_send` kèm chuỗi dữ liệu. Monitor sẽ nhận và truyền trực tiếp xuống RX của chip.*

---

## 💥 Step 3: Decode Guru Meditation Crashes / Giải mã Exception Crash
When the chip encounters an exception (e.g. Null pointer, Divide by Zero, Watchdog Timeout), it prints a backtrace.

1.  Locate the backtrace output in the log:
    ```text
    Backtrace:0x40081234:0x3ffb001c 0x400d5678:0x3ffb002c
    ```
2.  Call the MCP tool `decode_crash_stack`:
    ```json
    {
      "log_text": "Backtrace:0x40081234:0x3ffb001c 0x400d5678:0x3ffb002c",
      "elf_path": ".cm/build/my_project.elf"
    }
    ```
3.  The tool outputs the exact C++ source line numbers:
    ```text
    0x40081234: my_project.ino at line 14
    0x400d5678: FreeRTOS_task.c at line 102
    ```

*Gọi `decode_crash_stack` kèm chuỗi Backtrace và tệp ELF được sinh ra trong quá trình build để hiển thị rõ vị trí dòng lệnh lỗi.*

---

## ❓ FAQ / Câu hỏi thường gặp

::: tip GỢI Ý: Lấy file ELF ở đâu?
Mỗi khi biên dịch bằng công cụ `compile_sketch`, tệp ELF trung gian sẽ được tự động lưu trữ tại thư mục đầu ra `.cm/build/<project_name>.elf`. Hãy dùng đường dẫn này để giải mã stack trace.
:::
