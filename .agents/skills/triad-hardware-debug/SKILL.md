---
name: triad-hardware-debug
description: >-
  Knowledge base for TRIAD project hardware, including ESP32-S3 WeAct, GMT147SPI display debugging, and working guidelines for Cinq.
---

# User Info & Workflow
- **User:** Nguyễn Trung (Cinq) - Sinh viên Automation.
- **Projects:** TRIAD (Hệ sinh thái phương tiện tự hành/bán tự hành), Xiaozhi, Bài tập trên trường.
- **Agent Workflow:** 
  - Ưu tiên hoàn thành task một cách linh động, tự đưa ra quyết định mà không hỏi (confirm) những chi tiết nhỏ nhặt.
  - Chỉ hỏi những câu thực sự quan trọng liên quan đến phần cứng mà Agent không thể tự test.
  - **Bắt buộc:** Sau khi hoàn thành một task/mission, tự động commit và push code lên GitHub.

# Bài học phần cứng (Hardware Lessons Learned)

Đặc biệt áp dụng cho **ESP32-S3 WeAct N16R8** và màn hình **GMT147SPI (ST7789V3)**:

## 1. Xung đột GPIO (GPIO Conflicts)
- Tránh dùng các GPIO 10, 11, 12, 13, 14, 15 vì các chân này thường bị module NRF24 (CE/CSN/SCK/MOSI/MISO) hoặc I2S chiếm dụng trong project TRIAD.
- Cấu hình an toàn cho TFT SPI (dành cho ESP32-S3 WeAct):
  - `TFT_SCLK=40`
  - `TFT_MOSI=41`
  - `TFT_CS=39`
  - `TFT_DC=38`
  - `TFT_RST=47`

## 2. Lựa chọn SPI Bus
- ESP32-S3 khi sử dụng GPIO 40/41/42 cần phải trỏ sang bus SPI3 (HSPI).
- Bắt buộc khai báo cờ `-DUSE_HSPI_PORT=1` trong `platformio.ini`. Nếu không khai báo, ESP32 sẽ dùng FSPI mặc định dẫn đến lỗi con trỏ (`Guru Meditation Error: StoreProhibited`) ngay khi gọi `tft.init()`.

## 3. Lỗi Font chữ trong TFT_eSPI
- **Font 6** trong thư viện `TFT_eSPI` là font **chỉ chứa chữ số** (numbers-only).
- Cố tình dùng Font 6 để in chữ cái (ví dụ `"HELLO"`) sẽ không hiển thị gì cả.
- Cách khắc phục: Dùng `Font 4` kết hợp với `tft.setTextSize(2)` để tạo ra chữ có kích thước tương đương Font 6.

## 4. Điều khiển đèn nền (TFT Backlight)
- Các chân mặc định như `TFT_BL=48` trên WeAct S3 là LED RGB (WS2812) tích hợp, không thể điều khiển bằng `digitalWrite`.
- Không sử dụng cờ `-DTFT_BL` và `-DTFT_BACKLIGHT_ON` nếu nối sai hoặc xung đột. Cách tốt nhất để debug màn hình là **nối trực tiếp chân BL/BLK vào 3.3V** để loại trừ lỗi phần mềm.

## 5. Xử lý Bootloop (Crash Loop)
- Khi board bị crash loop liên tục (reset do lỗi code), tính năng nạp qua USB JTAG (`upload_protocol = esp-builtin`) thường bị đứt kết nối (Libusb error).
- Cần chuyển tạm về `upload_protocol = esptool` và ép board vào Bootloader mode thủ công bằng tay: 
  - Giữ nút `BOOT` -> Bấm thả nút `RST` -> Thả nút `BOOT`.
