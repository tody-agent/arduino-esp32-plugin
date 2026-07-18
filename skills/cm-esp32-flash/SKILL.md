---
name: cm-esp32-flash
description: Nạp chương trình (upload) xuống chip ESP32 qua Serial hoặc OTA, xử lý các sự cố bootloader vật lý và kết nối.
version: 1.0.0
platforms:
  - windows
---

# ESP32 Flasher & OTA Deployer

Mục tiêu của skill này là giải quyết triệt để các vấn đề khi nạp chương trình (upload) xuống ESP32 bằng cả phương thức có dây (Serial/COM) và không dây (OTA - Over The Air).

---

## 1. Nạp code qua cổng Serial (COM Port Flashing)

Khi nạp code qua cáp USB, hãy luôn sử dụng script `detect_ports.ps1` để tự động nhận dạng cổng nối tiếp phù hợp.

### Trình tự nạp code an toàn (Safe Upload Loop):
Để tránh lỗi cổng COM bị chiếm dụng do các chương trình monitor chạy ngầm:
1.  Tạo tệp lock báo hiệu tạm ngắt kết nối monitor:
    ```powershell
    New-Item -Path .cm/upload.lock -ItemType File -Force
    ```
2.  Chạy lệnh nạp code:
    ```powershell
    arduino-cli upload -p COM4 --fqbn esp32:esp32:esp32 <SketchFolder>
    ```
3.  Giải phóng lock sau khi nạp xong:
    ```powershell
    Remove-Item -Path .cm/upload.lock -Force
    ```

### Hướng dẫn sửa lỗi bootloader phần cứng:
Nếu gặp lỗi `Failed to connect to ESP32: Timed out waiting for packet header`:
*   **Nguyên nhân:** Mạch nạp trên board không kéo được chân `EN/RST` xuống mức thấp để kích hoạt chế độ nạp khi chân `IO0` ở mức thấp.
*   **Cách khắc phục:**
    1. Nhắc nhở người dùng nhấn giữ nút **BOOT** (hoặc nút ghi nhãn **IO0**) trên board ESP32.
    2. Nhấn phím chạy lệnh nạp.
    3. Khi terminal hiển thị dòng chữ `Connecting...` hoặc `Detecting chip type...`, lập tức nhả nút **BOOT** ra.
    4. Thiết bị sẽ bắt đầu ghi Flash (`Writing at 0x...`).

---

## 2. Nạp code không dây (ArduinoOTA)

Khi thiết bị đã được gắn cố định hoặc nằm ở vị trí khó cắm cáp, hãy chuyển sang nạp code qua mạng Wifi nội bộ (OTA).

### Mã nguồn C++ tích hợp vào Sketch (ArduinoOTA Boilerplate):
Để kích hoạt OTA trên ESP32, thêm đoạn mã sau vào chương trình của bạn:

```cpp
#include <WiFi.h>
#include <ArduinoOTA.h>

const char* ssid = "Ten_Wifi_Cua_Ban";
const char* password = "Mat_Khau_Wifi";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Thiết lập mật khẩu bảo mật OTA (Tùy chọn)
  // ArduinoOTA.setPassword("admin123");

  ArduinoOTA.onStart([]() {
    String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
    Serial.println("Start updating " + type);
  });
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
  });

  ArduinoOTA.begin();
}

void loop() {
  ArduinoOTA.handle(); // Bắt buộc gọi hàm này trong loop
}
```

### Lệnh nạp code không dây:
Khi thiết bị kết nối cùng mạng Wifi và in ra địa chỉ IP (ví dụ `192.168.1.50`), ta nạp code bằng cách chỉ định địa chỉ IP thay vì cổng COM:

```powershell
arduino-cli upload -p 192.168.1.50 --fqbn esp32:esp32:esp32 <SketchFolder>
```
*Lưu ý: Nếu cấu hình mật khẩu OTA, sử dụng thêm tham số `--upload-fields password=admin123`.*
