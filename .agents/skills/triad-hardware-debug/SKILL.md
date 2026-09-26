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

# Quy chuẩn Tài liệu README (README.md Standards)
Mỗi dự án mới đều **bắt buộc kèm file `README.md`** theo form chuẩn mà Cinq và Claude đã thống nhất:
0. **Banner động đầu trang (BẮT BUỘC)**:
   - Luôn đặt block banner ở đầu file:
     ```html
     <div align="center">
     <img src="assets/banner.svg" alt="CINQ - RESHAPE LAB. Automation, PCB, hardware, 3D engineer. Flight test, firmware STM32 and ESP, UAV, USV. Stack: C++, Python, Verilog. GitHub statistics." width="100%">
     </div>
     ```
   - Kèm thư mục `assets/` chứa `banner.svg` và `logo.svg` của ReShape Lab / TRIAD.
1. **Tiêu đề & Giới thiệu ngắn**: `# TÊN_REPO`, tóm tắt 1-2 câu mục đích/vai trò của firmware/hardware.
2. **Bảng môi trường PlatformIO**: Bảng `| Env | Board | Vai trò |` liệt kê các environment trong `platformio.ini`.
3. **Lệnh build / upload**: Khối code bash `pio run -e <env> -t upload`.
4. **Bảng sơ đồ đấu nối chân (Pinout Mapping)**:
   - Cột chuẩn: `| Linh kiện | Chân linh kiện | Chân MCU (GPIO) | Ghi chú kỹ thuật |`.
   - Phân cụm rõ ràng: Nguồn, Màn hình, Âm thanh, Cảm biến, Động cơ/Servo.
5. **Kiến trúc nguồn & Chống nhiễu**: Cảnh báo dòng tải (peak current), mạch hạ áp (Buck/BEC), tụ lọc nhiễu và quy tắc nối mass chung (Star Grounding).
6. **Lưu ý phần cứng thực tế (Gotchas)**: Chân strapping, điện áp Logic 3.3V/5V, chân chia sẻ bus SPI/I2S/I2C.
7. **Liên kết chéo (Cross-references)**: Dẫn link file code ([`src/...`](src/...)), sơ đồ SVG trong `docs/`, và các repo liên quan trong hệ sinh thái (TRIAD, JS-CONTROLER, GCS-STATION, Xiaozhi).
