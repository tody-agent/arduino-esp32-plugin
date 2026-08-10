---
name: cm-arduino-esp32
description: Skill phát triển phần mềm cho chip ESP32 sử dụng Arduino CLI và bộ công cụ tự động hóa của CodyMaster (dò tìm cổng COM, monitor nền, tự động giải mã crash stack trace và OTA).
version: 1.0.0
platforms:
  - windows
---

# ESP32 Arduino CLI Development Skill

Bộ skill này hướng dẫn Agent cách lập trình, biên dịch, nạp code (upload), debug và triển khai OTA cho ESP32 sử dụng `arduino-cli` kết hợp với bộ script PowerShell tự động hóa.

---

## 1. Khi nào kích hoạt Skill này (Triggers)
Kích hoạt skill này bất cứ khi nào người dùng yêu cầu:
- Lập trình ESP32, viết code Arduino cho ESP32.
- Dò tìm cổng kết nối, nạp chương trình (upload/flash/burn) cho ESP32.
- Giám sát cổng nối tiếp (serial monitor/log), đọc log chạy ngầm.
- Giải mã lỗi crash (Guru Meditation Error, CPU panic, Stack trace/Backtrace).
- Cập nhật phần mềm không dây (OTA - Over The Air).

---

## 2. Bảng lệnh nhanh (Quick Reference)

### A. Dò tìm cổng kết nối (Auto-detect Port)
Quét các thiết bị cắm vào máy tính, nhận dạng cổng của chip nạp ESP32:
```powershell
powershell -File .agents/skills/cm-arduino-esp32/scripts/detect_ports.ps1
```
*Kết quả trả về dạng JSON chứa thông tin cổng COM và cờ `IsESP32`.*

### B. Biên dịch chương trình (Compile)
Luôn lưu tệp biên dịch trung gian (ELF) để dùng cho việc giải mã stack trace và cấu hình bộ nhớ cache tăng tốc độ build:
```powershell
arduino-cli compile --fqbn esp32:esp32:esp32 --build-path .cm/build --build-cache-path .cm/build-cache <SketchFolder>
```

### C. Nạp code an toàn (Safe Upload via Serial)
Trước khi nạp code, luôn đặt Lock File để tắt Serial Monitor nền, sau đó tháo lock để tự động kết nối lại:
```powershell
# 1. Tạo Lock File để báo hiệu ngắt Serial Monitor
New-Item -Path .cm/upload.lock -ItemType File -Force

# 2. Thực hiện nạp code
arduino-cli upload -p <COMPORT> --fqbn esp32:esp32:esp32 <SketchFolder>

# 3. Xóa Lock File để mở lại Serial Monitor
Remove-Item -Path .cm/upload.lock -Force
```

### D. Giám sát Serial ngầm (Background Serial Monitor)
Chạy giám sát cổng Serial dưới dạng Job chạy ngầm để không chặn luồng lệnh của Agent:
```powershell
# Bắt đầu giám sát
Start-Job -Name Esp32Monitor -ScriptBlock { powershell -File .agents/skills/cm-arduino-esp32/scripts/serial_monitor.ps1 -Port "<COMPORT>" -LogPath ".cm/esp32_serial.log" -LockFile ".cm/upload.lock" }

# Xem log trực tiếp (50 dòng cuối)
Get-Content -Path .cm/esp32_serial.log -Tail 50

# Xem các job đang chạy
Get-Job

# Dừng giám sát khi hoàn tất dự án
Stop-Job -Name Esp32Monitor
Remove-Job -Name Esp32Monitor
```

### E. Giải mã lỗi Crash (Decode Stack Trace)
Khi ESP32 bị crash, nó sẽ in ra dòng `Backtrace:...` trong log. Sử dụng script giải mã để tìm ra dòng code bị lỗi:
```powershell
powershell -File .agents/skills/cm-arduino-esp32/scripts/decode_stack.ps1 -LogText (Get-Content .cm/esp32_serial.log | Out-String) -ElfPath .cm/build/<SketchName>.ino.elf
```

### G. Kiểm định An toàn GPIO (GPIO Safety Audit)
Trước khi nạp mã nguồn xuống thiết bị vật lý, hãy quét mã nguồn để đảm bảo không sử dụng sai các chân pin nhạy cảm (ví dụ chân SPI flash GPIO 6-11 hoặc cấu hình sai chân Serial):
```powershell
powershell -File .agents/skills/cm-arduino-esp32/scripts/audit_pins.ps1 -SketchPath <SketchFolderOrFile>
```
*Kết quả trả về danh sách JSON chứa các cảnh báo WARNING/ERROR nếu phát hiện cấu hình chân cấm.*

### H. Gửi lệnh hai chiều (Bidirectional Serial Send)
Khi cổng Serial đang được monitor ngầm, gửi lệnh điều khiển trực tiếp xuống thiết bị bằng cách ghi vào tệp hàng đợi:
```powershell
"LED_ON" | Out-File -FilePath .cm/serial_input.queue -Encoding UTF8 -Force
```
*Tiến trình monitor nền sẽ tự động đọc, truyền qua Serial, và xóa hàng đợi.*

### I. Giao diện Visual Log Debugger Web UI Dashboard (Mới)
Khởi chạy trang Web UI trực quan (chạy tại `http://localhost:8321`) để giám sát log thời gian thực, tự động giải mã crash stack trace và truyền lệnh 2 chiều trực quan:
```powershell
powershell -File .agents/skills/cm-arduino-esp32/scripts/launch_dashboard.ps1
```
*Hoặc sử dụng MCP Tool: `launch_log_dashboard`.*

---

## 3. Quy trình gỡ lỗi lỗi phần cứng phổ biến (Hardware Troubleshooting)

1.  **Lỗi nạp code (`Failed to connect to ESP32: Timed out waiting for packet header`):**
    - *Nguyên nhân:* Chip nạp không tự động kích hoạt được chân reset/bootloader của ESP32.
    - *Giải pháp:* Nhắc người dùng **giữ nút BOOT (hoặc IO0)** trên board ESP32 khi màn hình hiển thị chữ `Connecting...` và thả ra khi thấy bắt đầu ghi dữ liệu (`Writing at 0x...`).
2.  **Lỗi thiếu thư viện liên kết:**
    - Khi compile báo lỗi thiếu file `.h` (ví dụ `DHT.h`), chạy lệnh:
      ```powershell
      arduino-cli lib search dht
      arduino-cli lib install "DHT sensor library"
      ```
3.  **Lỗi Reset liên tục (Watchdog Timer Triggered / Stack Overflow):**
    - Đọc file log `.cm/esp32_serial.log`.
    - Trích xuất phần Backtrace và chạy `decode_stack.ps1`.
    - Phân tích vị trí crash: Nếu crash ở các thư viện Wifi/HTTP, hãy tăng dung lượng stack cho FreeRTOS task hoặc kiểm tra lỗi con trỏ Null.

---

## 4. Jobs-To-Be-Done (JTBD) Checklist cho Agent
Khi thực hiện các yêu cầu của người dùng, hãy tuân thủ nguyên tắc:
- **Think twice before compile:** ESP32 có nhiều dòng (ESP32-WROOM, ESP32-C3, ESP32-S3). Hãy hỏi người dùng FQBN cụ thể nếu biên dịch lỗi.
- **Always use Lock File:** Tuyệt đối không chạy lệnh `arduino-cli upload` khi chưa tạo `.cm/upload.lock` nếu có Job monitor đang chạy, tránh xung đột chiếm quyền sử dụng cổng COM.
- **Decode immediately on panic:** Thấy Guru Meditation Error trong log? Chạy ngay `decode_stack.ps1` để tìm dòng lỗi trước khi đề xuất giải pháp sửa code.
