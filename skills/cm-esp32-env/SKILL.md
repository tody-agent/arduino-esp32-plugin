---
name: cm-esp32-env
description: Quản lý cấu hình môi trường phát triển ESP32, cài đặt driver, quản lý các thư viện phụ thuộc và thiết lập sơ đồ phân vùng nhớ (Partition Tables) trên Arduino CLI.
version: 1.0.0
platforms:
  - windows
---

# ESP32 Environment & Dependency Manager

Mục tiêu của skill này là hướng dẫn cấu hình môi trường Arduino CLI tối ưu cho ESP32, quản lý các thư viện ngoài và tối ưu hóa bảng phân vùng bộ nhớ (Partition Table) để giải quyết các giới hạn lưu trữ của dự án nhúng.

---

## 1. Khởi tạo & Cấu hình ESP32 Core

Để `arduino-cli` nhận diện được các dòng chip ESP32 (ESP32, ESP32-S2, ESP32-S3, ESP32-C3, v.v.), ta cần thêm URL của package Espressif vào file cấu hình `arduino-cli.yaml`:

```powershell
# 1. Thêm URL package ESP32 vào cấu hình
arduino-cli config add board_manager.additional_urls https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json

# 2. Cập nhật chỉ mục (index) của board manager
arduino-cli core update-index

# 3. Cài đặt ESP32 core mới nhất
arduino-cli core install esp32:esp32
```

---

## 2. Quản lý Thư viện Phụ thuộc (Libraries)

ESP32 thường sử dụng các thư viện phần cứng tối ưu hóa riêng. Hãy luôn kiểm tra sự tương thích của thư viện khi lập trình:
-   **Tìm kiếm thư viện:** `arduino-cli lib search <tên_thư_viện>`
-   **Cài đặt thư viện:** `arduino-cli lib install "DHT sensor library"`
-   **Kiểm tra các thư viện đã cài:** `arduino-cli lib list`

> [!WARNING]
> **Xung đột tên thư viện:**
> Một số thư viện như `WiFi.h` đi kèm sẵn trong ESP32 Core có thể bị xung đột nếu máy tính cài đặt các thư viện Wifi cũ (như `WiFiNINA` hoặc `WiFi101`). Tránh cài đặt các thư viện này một cách bừa bãi. Nếu gặp lỗi biên dịch liên quan đến nạp trùng thư viện, hãy đọc log biên dịch chi tiết để tìm và xóa thư viện trùng lặp trong thư mục `libraries/` của Arduino.

---

## 3. Thiết lập Sơ đồ Phân vùng nhớ (Partition Tables)

Mặc định, ESP32 chỉ phân bổ khoảng **1.2MB** cho chương trình (App). Khi dự án phình to (sử dụng Wifi, Bluetooth, OTA), bạn sẽ gặp lỗi biên dịch:
`sketch too large; WebUpdater.ino.elf section .text will not fit in region iram0_0_seg`

### Các sơ đồ phân vùng mặc định của ESP32:
Bạn có thể cấu hình phân vùng thông qua tham số biên dịch `--build-property`:

| Phân vùng | Mô tả | Lệnh cấu hình biên dịch |
| :--- | :--- | :--- |
| **Default** | 1.2MB App, 1.5MB SPIFFS, có OTA (Dual-app) | `--build-property build.partitions=default` |
| **No OTA** | 2.0MB App, 2.0MB SPIFFS, không hỗ trợ OTA | `--build-property build.partitions=no_ota` |
| **Huge App** | 3.1MB App, 1.0MB SPIFFS, không hỗ trợ OTA | `--build-property build.partitions=huge_app` |
| **Minimal SPIFFS**| 1.9MB App, 190KB SPIFFS, có OTA | `--build-property build.partitions=min_spiffs` |

### Tạo bảng phân vùng tùy biến (Custom Partition Table)
Nếu dự án của bạn cần phân vùng chính xác (ví dụ tăng bộ nhớ ứng dụng lên tối đa nhưng vẫn giữ OTA và LittleFS nhỏ):
1.  Tạo tệp cấu hình `partitions.csv` trong thư mục sketch của bạn:
    ```csv
    # Name,   Type, SubType, Offset,  Size, Flags
    nvs,      data, nvs,     0x9000,  0x5000,
    otadata,  data, ota,     0xe000,  0x2000,
    app0,     app,  ota_0,   0x10000, 0x1E0000,
    app1,     app,  ota_1,   0x1F0000,0x1E0000,
    spiffs,   data, spiffs,  0x3D0000,0x30000,
    ```
2.  Biên dịch sử dụng phân vùng tùy biến này:
    ```powershell
    arduino-cli compile --fqbn esp32:esp32:esp32 --build-property build.partitions=custom --build-property build.custom_partitions=partitions.csv <SketchFolder>
    ```
