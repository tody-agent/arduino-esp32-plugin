---
name: cm-esp32-debug
description: Giám sát cổng Serial nối tiếp, gỡ lỗi đa luồng FreeRTOS và giải mã các địa chỉ ngoại lệ crash (Guru Meditation Error) trên ESP32.
version: 1.0.0
platforms:
  - windows
---

# ESP32 Debugger & Crash Decryptor

Mục tiêu của skill này là hướng dẫn phân tích gỡ lỗi chạy ẩn (runtime debugging), giải quyết lỗi rò rỉ bộ nhớ (memory leaks) và giải mã các mã lỗi crash phần cứng (Guru Meditation Errors) bằng cách ánh xạ ngược địa chỉ hex sang dòng code nguồn.

---

## 1. Giải mã ngoại lệ Crash (Guru Meditation Error)

Khi ESP32 gặp các lỗi nghiêm trọng (truy cập con trỏ null, lỗi bus, chia cho 0), hệ thống sẽ khởi động lại và in ra log dạng:

```
Guru Meditation Error: Core  1 panic'ed (StoreProhibited). Exception was not handled.
Core  1 register dump:
...
Backtrace:0x400d0c35:0x3ffb1f20 0x400d0c7a:0x3ffb1f40
```

### Các lỗi Panic phổ biến:
-   **StoreProhibited / LoadProhibited:** Lỗi truy cập bộ nhớ không hợp lệ. Thường do tham chiếu con trỏ Null (ví dụ gọi hàm trên đối tượng chưa khởi tạo `object->method()`).
-   **IntegerDivideByZero:** Lỗi chia cho 0 trong code tính toán.
-   **IllegalInstruction:** Vi điều khiển cố chạy lệnh không hợp lệ, thường do ghi đè vùng nhớ code (buffer overflow) hoặc trỏ con trỏ hàm sai địa chỉ.

### Giải pháp giải mã tự động:
1. **Qua giao diện Visual Log Debugger Web UI (Khuyến nghị):**
   Mở trình duyệt Web tại `http://localhost:8321` (chạy `powershell -File .agents/skills/cm-arduino-esp32/scripts/launch_dashboard.ps1` hoặc MCP tool `launch_log_dashboard`) và bấm nút **"🔍 Decode Crash"**.

2. **Qua lệnh CLI:**
   Chạy script `decode_stack.ps1` để tự động chuyển đổi chuỗi `Backtrace` sang dòng code cụ thể:
```powershell
powershell -File .agents/skills/cm-arduino-esp32/scripts/decode_stack.ps1 -LogText (Get-Content .cm/esp32_serial.log | Out-String) -ElfPath .cm/build/<SketchName>.ino.elf
```

---

## 2. Gỡ lỗi đa luồng FreeRTOS

ESP32 là vi điều khiển 2 nhân chạy hệ điều hành thời gian thực FreeRTOS. Các lỗi liên quan đến xung đột luồng và tràn bộ nhớ rất thường gặp:

### A. Tràn bộ nhớ ngăn xếp luồng (Stack Overflow)
Nếu bạn tạo một Task mới bằng `xTaskCreate` hoặc `xTaskCreatePinnedToCore` nhưng cấp phát dung lượng Stack quá nhỏ, hệ thống sẽ crash khi task chạy phức tạp:
-   *Dấu hiệu:* Log lỗi `Stack overflow in task ...`.
-   *Khắc phục:* Tăng dung lượng Stack được cấp phát (tham số thứ 3 của `xTaskCreate`).
-   *Kiểm tra dung lượng ngăn xếp còn lại:*
    Gọi hàm `uxTaskGetStackHighWaterMark(NULL)` trong task để kiểm tra dung lượng stack tối thiểu còn trống (trả về giá trị càng nhỏ càng nguy hiểm, nếu bằng 0 nghĩa là đã tràn).

### B. Theo dõi rò rỉ bộ nhớ Heap (Memory Leaks)
Nếu bộ nhớ RAM của ESP32 giảm dần theo thời gian dẫn đến crash thiết bị sau vài giờ chạy:
-   *Cách kiểm tra:* Thêm dòng log in bộ nhớ heap còn trống trong `loop()` hoặc định kỳ:
    ```cpp
    Serial.printf("Free heap memory: %u bytes\n", ESP.getFreeHeap());
    ```
-   *Khắc phục:* Đảm bảo mọi đối tượng cấp phát động bằng `new` hoặc `malloc` đều phải được giải phóng bằng `delete` hoặc `free`.

### C. Watchdog Timer (WDT) Triggered
ESP32 có bộ đếm thời gian giám sát (Watchdog) trên mỗi nhân. Nếu một task chạy vòng lặp vô hạn mà không nhường quyền xử lý cho các task khác hoặc hệ thống điều phối (scheduler):
-   *Dấu hiệu:* Reset liên tục kèm lỗi `Task watchdog got triggered. The following tasks did not reset the watchdog: IDLE`.
-   *Khắc phục:* Thêm lệnh ngủ ngắn `vTaskDelay(pdMS_TO_TICKS(10))` hoặc `delay(10)` trong vòng lặp lớn để nhường quyền xử lý CPU cho nhân điều phối.
-   *Đảm bảo phân phối nhân:* Nếu chạy tác vụ tính toán nặng, hãy gán task đó sang nhân phụ (`Core 0` hoặc `Core 1`) thông qua hàm `xTaskCreatePinnedToCore`.

---

## 3. Giao tiếp cổng nối tiếp hai chiều (Bidirectional Serial testing)

Khi bạn phát triển các tính năng yêu cầu người dùng gửi lệnh xuống ESP32 qua Serial (ví dụ: gõ lệnh cấu hình Wi-Fi, kiểm tra trạng thái cảm biến):

### Gửi lệnh xuống bo mạch từ Agent:
Sử dụng công cụ `serial_send` (hoặc ghi trực tiếp vào hàng đợi tệp tin `.cm/serial_input.queue`):
```powershell
"SET_SSID:MyWiFi" | Out-File -FilePath .cm/serial_input.queue -Encoding UTF8 -Force
```

### Mã nguồn tham khảo xử lý lệnh trên ESP32:
```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "LED_ON") {
      digitalWrite(2, HIGH);
      Serial.println("LED is now ON");
    } else if (cmd == "LED_OFF") {
      digitalWrite(2, LOW);
      Serial.println("LED is now OFF");
    }
  }
}
```

