---
name: cm-esp32-build
description: Biên dịch mã nguồn Arduino ESP32, tối ưu bộ nhớ đệm cache, biên dịch phân vùng dữ liệu SPIFFS, LittleFS và FATFS trên CLI.
version: 1.0.0
platforms:
  - windows
---

# ESP32 Build & Filesystem Compiler

Mục tiêu của skill này là tối ưu hóa tốc độ biên dịch mã nguồn ESP32 và hướng dẫn đóng gói phân vùng hệ thống tệp (SPIFFS/LittleFS) để nạp các tệp tĩnh (HTML, CSS, JSON cấu hình, hình ảnh) xuống bộ nhớ Flash của chip.

---

## 1. Tối ưu tốc độ biên dịch (Build Caching)

Biên dịch cho ESP32 thường mất nhiều thời gian do kích thước mã nguồn framework lớn. Bằng cách tái sử dụng cache, thời gian biên dịch lần thứ hai sẽ giảm từ 1-2 phút xuống chỉ còn 5-10 giây:

```powershell
# Sử dụng cache và xuất kết quả biên dịch ra thư mục cụ thể
arduino-cli compile --fqbn esp32:esp32:esp32 --build-path .cm/build --build-cache-path .cm/build-cache <SketchFolder>
```
*Lưu ý: Thư mục `.cm/build` sẽ chứa file `.elf` và `.bin` cần thiết để nạp code và gỡ lỗi.*

---

## 2. Làm việc với Hệ thống tệp (SPIFFS / LittleFS)

ESP32 có khả năng gắn kết bộ nhớ Flash làm ổ đĩa ảo để lưu trữ tệp (ví dụ giao diện WebServer tĩnh). Ta cần đóng gói thư mục dữ liệu (`data/`) thành file ảnh binary `.bin` và nạp vào phân vùng lưu trữ của chip.

### Các công cụ đóng gói đi kèm ESP32 Core:
Công cụ thường nằm trong thư mục cài đặt của ESP32 package:
`%LOCALAPPDATA%\Arduino15\packages\esp32\tools\mklittlefs\**\mklittlefs.exe`

### Quy trình đóng gói và nạp dữ liệu:
1.  **Chuẩn bị:** Tạo thư mục `data` bên trong thư mục chứa sketch Arduino của bạn (ví dụ: `MyProject/data/index.html`).
2.  **Tìm công cụ đóng gói:** Tìm file `mklittlefs.exe` hoặc `mkspiffs.exe` trong máy tính của bạn:
    ```powershell
    $mklittlefs = Get-ChildItem -Path "$env:LOCALAPPDATA\Arduino15\packages\esp32" -Filter "mklittlefs.exe" -Recurse | Select-Object -First 1 -ExpandProperty FullName
    ```
3.  **Đóng gói thư mục `data` thành file ảnh `.bin`:**
    Giả sử kích thước phân vùng chứa file của bạn trên bảng phân vùng (Partition Table) là `0x150000` (khoảng 1.3MB):
    ```powershell
    # Tạo file image LittleFS
    & $mklittlefs -c MyProject/data -s 0x150000 -p 256 -b 4096 MyProject/littlefs.bin
    ```
4.  **Nạp file ảnh xuống ESP32:**
    Sử dụng công cụ `esptool.exe` đi kèm trong core để nạp trực tiếp file ảnh này vào địa chỉ bắt đầu của phân vùng lưu trữ trên bộ nhớ Flash (ví dụ địa chỉ `0x290000`):
    ```powershell
    $esptool = Get-ChildItem -Path "$env:LOCALAPPDATA\Arduino15\packages\esp32" -Filter "esptool.exe" -Recurse | Select-Object -First 1 -ExpandProperty FullName
    
    # Nạp dữ liệu qua cổng COM4
    & $esptool --chip esp32 --port COM4 --baud 921600 write_flash 0x290000 MyProject/littlefs.bin
    ```
