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

# Quy chuẩn Tài liệu README & Banner SVG (ReShape Lab Standards)
Mỗi dự án mới đều **bắt buộc có Banner SVG động (`docs/banner.svg`) và file `README.md` chuyên biệt**, thiết kế đúng chất kỹ sư Automation theo phong cách thực chiến của Cinq và Claude (như `QUAD-UAV`, `JS-CONTROLER`, `esp32s3_weact_xiaozhirobot`):

## 1. Kiến trúc Banner SVG Động (`docs/banner.svg`)
- **Khung & Tỷ lệ**: `viewBox="0 0 1200 {HEIGHT}" width="1200" height="{HEIGHT}" rx="24" fill="#0E0E0E"`.
- **Hoạt ảnh Logo (Giữ nguyên 100%)**:
  - Logo ReShape Gear (`#lg`) rơi xuống từ đỉnh (`split-a`, `split-b`, 0-1.7s), dừng ở giữa (2.8s) rồi tách ra 2 góc trên-trái và dưới-phải (4.4s).
  - Hoạt ảnh chữ thương hiệu: `TRIAD` (Serif font-size 60), `SUBTITLE` (Mono font-size 17), `RESHAPE LAB` (Mono font-size 17).
  - Hoạt ảnh idle trôi nhẹ nhàng (`.float a`, `.float b`).
- **Font Stack (Bắt buộc giữ nguyên font & size)**:
  - `.serif`: `'Tiempos Headline', Georgia, 'Times New Roman', serif;`
  - `.sans`: `'Styrene A', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;`
  - `.mono`: `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;`
- **Cấu trúc 4 Section thông tin ngắn trên Banner**:
  - `info i1`: `TRIAD · RESHAPE LAB` (Mono 19) + `TÊN DỰ ÁN` (Serif 110) + `Mô tả 2 dòng` (Sans 30).
  - `info i2`: `FIRMWARE` (Serif 72) + Tên môi trường & file cpp chính.
  - `info i3`: `FEATURES / PERIPHERALS` (Serif 72) + Các cụm ngoại vi chính.
  - `info i4`: `RELATED REPOS` (Serif 72) + Các repo liên kết trong hệ sinh thái TRIAD.

## 2. Phần Markdown Chi tiết Bên dưới Banner (`README.md`)
- `<div align="center"><img src="docs/banner.svg" alt="..." width="100%"></div>`
- **Tiêu đề & Tóm tắt**: `# TÊN_DỰ_ÁN`, mô tả tổng quan kỹ thuật.
- **Bảng môi trường PlatformIO**: `| Env PlatformIO | Bo mạch MCU | Vai trò kỹ thuật | Lệnh nạp firmware |`.
- **Lệnh build / nạp nhanh**: Khối code bash `pio run -e <env> -t upload` và `pio device monitor`.
- **Bảng linh kiện & Giao tiếp (BOM)**: Liệt kê chi tiết linh kiện, chuẩn giao tiếp (I2S, SPI, I2C, PWM) và vai trò.
- **Sơ đồ chân trực quan (ASCII Art Board)**: Vẽ sơ đồ 2 hàng chân thực tế của board MCU (WeAct ESP32-S3-A / DevKit V1 30-pin).
- **Bảng tra cứu chân chi tiết (Pinout Mapping Table)**: Cột chuẩn `| Cụm thiết bị | Chân linh kiện | Chân MCU (GPIO) | Điện áp | Ghi chú kỹ thuật |`.
- **Kiến trúc nguồn & Chống nhiễu**: Sơ đồ Buck DC-DC, tụ bù ($470\mu F - 1000\mu F$), nguyên tắc Star Grounding.
- **Lưu ý phần cứng thực tế (Gotchas)**: Strapping pins, USB CDC Native, PSRAM OPI, bus SPI riêng, font chữ.
- **Lộ trình tính năng (Roadmap)**: Checklist các phase phát triển.
- **Liên kết chéo hệ sinh thái (Cross-references)**: Link sang các repo anh em trong hệ sinh thái.
