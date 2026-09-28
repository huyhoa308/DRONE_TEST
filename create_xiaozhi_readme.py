import os

banner_template_path = r"d:/PlatformIO/Projects/QUAD-UAV/docs/banner.svg"
with open(banner_template_path, "r", encoding="utf-8") as f:
    uav_svg = f.read()

defs_start = uav_svg.find("<defs>")
defs_end = uav_svg.find("</defs>") + len("</defs>")
defs_content = uav_svg[defs_start:defs_end]

banner_height = 1760
split_b_y = 1007

xiaozhi_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {banner_height}" width="1200" height="{banner_height}" role="img" aria-label="XIAOZHI-ROBOT by RESHAPE LAB: desktop AI robot assistant firmware, ESP32-S3 WeAct N16R8, audio, vision, motion">
{defs_content}
  <style>
    .serif {{ font-family: 'Tiempos Headline', Georgia, 'Times New Roman', serif; }}
    .sans  {{ font-family: 'Styrene A', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif; }}
    .mono  {{ font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}

    /* 1. intro: the logo drops in from the top (0-1.7s), holds, then splits in two (2.8-4.4s) */
    .lg-a {{ animation: split-a 5s both; }}
    .lg-b {{ animation: split-b 5s both; }}
    .lg-a use, .lg-b use {{ animation: tint 5s both; }}
    @keyframes split-a {{
      0%   {{ transform: translate(450px, -420px) scale(1.66); animation-timing-function: cubic-bezier(.5,0,1,.6) }}
      18%  {{ transform: translate(450px, 330px) scale(1.66);  animation-timing-function: ease-out }}
      26%  {{ transform: translate(450px, 276px) scale(1.66);  animation-timing-function: ease-in }}
      34%  {{ transform: translate(450px, 330px) scale(1.66) }}
      56%  {{ transform: translate(450px, 330px) scale(1.66);  animation-timing-function: cubic-bezier(.65,0,.35,1) }}
      88%, 100% {{ transform: translate(-333px, -377px) scale(5.525) }}
    }}
    @keyframes split-b {{
      0%   {{ transform: translate(450px, -420px) scale(1.66); animation-timing-function: cubic-bezier(.5,0,1,.6) }}
      18%  {{ transform: translate(450px, 330px) scale(1.66);  animation-timing-function: ease-out }}
      26%  {{ transform: translate(450px, 276px) scale(1.66);  animation-timing-function: ease-in }}
      34%  {{ transform: translate(450px, 330px) scale(1.66) }}
      56%  {{ transform: translate(450px, 330px) scale(1.66);  animation-timing-function: cubic-bezier(.65,0,.35,1) }}
      88%, 100% {{ transform: translate(533px, {split_b_y}px) scale(5.525) }}
    }}
    @keyframes tint {{ 0%, 56% {{ fill: #F1EFE8 }} 88%, 100% {{ fill: #1E1E1D }} }}
    .brand {{ transform-box: fill-box; transform-origin: 50% 50%; animation: brand 5s both; }}
    @keyframes brand {{
      0%, 20% {{ opacity: 0; transform: scale(1.9) }}
      26%  {{ opacity: 1; transform: scale(1.9) }}
      36%  {{ opacity: 1; transform: scale(1) }}
      52%  {{ opacity: 1; transform: scale(1) }}
      60%, 100% {{ opacity: 0; transform: scale(1) }}
    }}

    /* 2. then the information appears, section by section */
    .info {{ animation: show .9s ease-out both; }}
    .i1 {{ animation-delay: 4.3s }} .i2 {{ animation-delay: 4.7s }} .i3 {{ animation-delay: 5.1s }} .i4 {{ animation-delay: 5.5s }}
    @keyframes show {{ from {{ opacity: 0; transform: translateY(14px) }} to {{ opacity: 1; transform: translateY(0) }} }}

    /* 3. idle motion */
    .float {{ animation: drift 11s ease-in-out 5s infinite alternate; }}
    .float.b {{ animation-name: drift2; animation-duration: 14s; }}
    @keyframes drift  {{ from {{ transform: translate(0, 0) }} to {{ transform: translate(-16px, 22px) }} }}
    @keyframes drift2 {{ from {{ transform: translate(0, 0) }} to {{ transform: translate(16px, -22px) }} }}
    .flame {{ transform-box: fill-box; transform-origin: 50% 100%; animation: flicker 2.4s ease-in-out infinite; }}
    @keyframes flicker {{
      0%, 100% {{ transform: scale(1, 1) skewX(0deg); stroke-opacity: 1 }}
      25% {{ transform: scale(1.03, 1.06) skewX(-2deg); stroke-opacity: .85 }}
      50% {{ transform: scale(.98, 1.02) skewX(1.5deg); stroke-opacity: 1 }}
      75% {{ transform: scale(1.02, 1.05) skewX(-1deg); stroke-opacity: .9 }}
    }}
    .spark {{ opacity: 0; animation: rise 3s ease-out infinite; }}
    .spark.s2 {{ animation-delay: 1.4s; }}
    @keyframes rise {{ 0% {{ opacity: 0; transform: translateY(6px) }} 25% {{ opacity: .9 }} 100% {{ opacity: 0; transform: translateY(-16px) }} }}
    @media (prefers-reduced-motion: reduce) {{
      .lg-a, .lg-b, .lg-a use, .lg-b use, .info, .float, .flame, .spark {{ animation: none }}
      .brand {{ display: none }}
    }}
  </style>
  <g clip-path="url(#frame)">
    <rect width="1200" height="{banner_height}" fill="#0E0E0E"/>

    <g class="float a"><g class="lg-a" transform="translate(-333 -377) scale(5.525)"><use href="#lg" fill="#1E1E1D"/></g></g>
    <g class="float b"><g class="lg-b" transform="translate(533 {split_b_y}) scale(5.525)"><use href="#lg" fill="#1E1E1D"/></g></g>
    <text class="brand serif" x="600" y="756" font-size="60" letter-spacing="10" text-anchor="middle" fill="#F1EFE8">TRIAD</text>
    <text class="brand mono" x="600" y="806" font-size="17" letter-spacing="5" text-anchor="middle" fill="#8B8983">DESKTOP AI ROBOT ASSISTANT</text>
    <text class="brand mono" x="600" y="842" font-size="17" letter-spacing="5" text-anchor="middle" fill="#8B8983">RESHAPE LAB</text>

    <!-- SECTION 1: HEADER & TITLE -->
    <g class="info i1">
      <line x1="100" y1="420" x2="1100" y2="420" stroke="#33332F" stroke-width="2"/>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="120">TRIAD  &#183;  RESHAPE LAB</text>
      <text class="serif" font-size="110" fill="#F1EFE8" x="94" y="262">XIAOZHI-ROBOT</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="340">Desktop AI Robot Assistant firmware</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="384">for ESP32-S3 WeAct N16R8.</text>
    </g>

    <!-- SECTION 2: FIRMWARE -->
    <g class="info i2">
      <text class="serif" font-size="72" fill="#F1EFE8" x="96" y="516">FIRMWARE</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="600">ESP32-S3  &#183;  esp32s3_xiaozhi</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="641">AI Voice Assistant, Avatar Emotion &amp; 4-DOF Motion</text>
      <text class="mono" font-size="19" fill="#77756E" x="100" y="675">main_xiaozhi.cpp</text>
      <line x1="100" y1="730" x2="1100" y2="730" stroke="#33332F" stroke-width="2"/>
    </g>

    <!-- SECTION 3: PERIPHERALS -->
    <g class="info i3">
      <text class="serif" font-size="72" fill="#F1EFE8" x="96" y="826">PERIPHERALS</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="910">AUDIO I/O</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="951">INMP441 MEMS Mic (I2S0) and MAX98357A Amp (I2S1)</text>
      <text class="mono" font-size="19" fill="#77756E" x="100" y="985">I2S Dual-Bus Audio Pipeline</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="1050">DISPLAY</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="1091">GMT147SPI 1.47" ST7789V3 (172x320) IPS</text>
      <text class="mono" font-size="19" fill="#77756E" x="100" y="1125">SPI3 HSPI  &#183;  Dynamic Avatar &amp; ReShape Boot Animations</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="1190">SENSORS &amp; ACTUATORS</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="1231">VL53L0X/1X ToF Distance Sensor &amp; 4x 180&#176; Servos</text>
      <text class="mono" font-size="19" fill="#77756E" x="100" y="1265">I2C Proximity Wakeup  &#183;  LEDC PWM Head &amp; Arm Motion</text>
      <line x1="100" y1="1320" x2="1100" y2="1320" stroke="#33332F" stroke-width="2"/>
    </g>

    <!-- SECTION 4: RELATED REPOS -->
    <g class="info i4">
      <text class="serif" font-size="72" fill="#F1EFE8" x="96" y="1416">RELATED REPOS</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="1500">QUAD-UAV</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="1541">Quadcopter flight controller firmware (ESP32 + STM32)</text>
      <text class="mono" font-size="19" letter-spacing="4.5" fill="#8B8983" x="100" y="1606">JS-CONTROLER</text>
      <text class="sans" font-size="30" fill="#F1EFE8" x="100" y="1647">Handheld dual-joystick controller with TFT &amp; audio telemetry</text>
    </g>
  </g>
</svg>
"""

target_docs = r"d:/PlatformIO/Projects/esp32s3_weact_xiaozhirobot/docs"
os.makedirs(target_docs, exist_ok=True)

target_svg = os.path.join(target_docs, "banner.svg")
with open(target_svg, "w", encoding="utf-8") as f:
    f.write(xiaozhi_svg)
print(f"Written banner.svg to {target_svg}")

readme_content = """<div align="center">

<img src="docs/banner.svg" alt="XIAOZHI-ROBOT by RESHAPE LAB: desktop AI robot assistant firmware, ESP32-S3 WeAct N16R8, audio, vision, motion" width="100%">

</div>

# XIAOZHI-ROBOT

Firmware trợ lý AI để bàn **Xiaozhi Desktop Robot** phát triển trên nền tảng vi điều khiển **ESP32-S3 WeAct CoreBoard N16R8** (16MB Flash, 8MB PSRAM OPI). 

Robot tích hợp tương tác giọng nói 2 chiều (Micro MEMS INMP441 + Khuếch đại I2S MAX98357A), màn hình IPS **GMT147SPI** hiển thị avatar/biểu cảm động và logo boot ReShape Lab, cảm biến quang học ToF **VL53L0X / VL53L1X** nhận diện người lại gần / vẫy tay đánh thức, cùng hệ thống **4 động cơ Servo 180°** điều khiển cử động đầu (Pan/Tilt) và 2 cánh tay.

| Môi trường (Env) | Bo mạch MCU | Vai trò kỹ thuật | Lệnh nạp firmware |
| :--- | :--- | :--- | :--- |
| `esp32s3_xiaozhi` | WeAct ESP32-S3-A N16R8 | Firmware chính robot Xiaozhi | `pio run -e esp32s3_xiaozhi -t upload` |

```bash
# Biên dịch và nạp firmware qua cổng Type-C Native
pio run -e esp32s3_xiaozhi -t upload

# Mở serial monitor (115200 baud)
pio device monitor -b 115200
```

---

## 🛠 Danh mục Linh kiện (Hardware BOM)

| Cụm chức năng | Linh kiện | Giao tiếp | Vai trò trong Robot | Ghi chú kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| **Xử lý trung tâm** | WeAct ESP32-S3 CoreBoard | — | Chạy FreeRTOS, xử lý Audio/WiFi, điều khiển ngoại vi | Bản A (N16R8: 16MB Flash, 8MB PSRAM OPI) |
| **Màn hình biểu cảm** | GMT147SPI (ST7789V3) | SPI (HSPI) | Hiển thị mắt biểu cảm, cử động miệng, HUD thông số | IPS 172×320 pixel, 262K màu |
| **Micro thu âm** | INMP441 MEMS | I2S (I2S0) | Thu giọng nói người dùng gửi lên server STT/LLM | Micro kỹ thuật số 24-bit, độ nhạy cao |
| **Phát âm thanh** | MAX98357A | I2S (I2S1) | Khuếch đại âm thanh phản hồi từ server TTS | Mạch DAC/Amp Class-D công suất 3W |
| **Cảm biến khoảng cách**| VL53L0X / VL53L1X v2 | I2C | Nhận diện người lại gần, nhận diện cử chỉ vẫy tay | Cảm biến ToF đo khoảng cách bằng laser |
| **Cơ cấu cử động** | 4× Servo 180° | PWM (LEDC) | Cử động đầu (Pan/Tilt) và 2 cánh tay | Tần số 50Hz, góc quay 0° – 180° |
| **Hạ áp nguồn** | WeAct Buck DC/DC | Nguồn xung | Hạ áp từ pin 2S (7.4V) xuống 5.0V 3A cấp cho Servo & ESP32 | Hiệu suất cao (~92%), chịu tải đỉnh 3A |

---

## 🔌 Sơ đồ đấu nối chân WeAct ESP32-S3-A

Vị trí chân thực tế trên board WeAct ESP32-S3 CoreBoard (Bản A):

```
                             ┌───────────────────┐
                       3.3V ─┤ 3V3           GND ├─ GND
                        EN  ─┤ EN             44 ├─ (UART0 RX)
          MIC_WS (INMP441)  ─┤ 4              43 ├─ (UART0 TX)
          MIC_SCK(INMP441)  ─┤ 5              42 ├─ TFT_MISO (HSPI)
          MIC_SD (INMP441)  ─┤ 6              41 ├─ TFT_MOSI (HSPI)
          TOF_SDA (VL53L0X) ─┤ 7              40 ├─ TFT_SCLK (HSPI)
          TOF_SCL (VL53L0X) ─┤ 8              39 ├─ TFT_CS (HSPI)
               SERVO_1_PAN  ─┤ 9              38 ├─ TFT_DC
              SERVO_2_TILT  ─┤ 10             37 ├─ (PSRAM OPI - Cam dung)
              SERVO_3_ARM_L ─┤ 11             36 ├─ (PSRAM OPI - Cam dung)
              SERVO_4_ARM_R ─┤ 12             35 ├─ (PSRAM OPI - Cam dung)
             SPK_BCLK (MAX) ─┤ 15              0 ├─ BOOT Button
              SPK_LRC (MAX) ─┤ 16             45 ├─ (Strapping - Cam dung)
              SPK_DIN (MAX) ─┤ 17             48 ├─ WS2812 RGB LED Onboard
              SPK_SD  (MAX) ─┤ 18             47 ├─ TFT_RST
               USB D-       ─┤ 19             21 ├─ (Du phong GPIO)
               USB D+       ─┤ 20             14 ├─ (Du phong GPIO)
                        5V  ─┤ 5V             13 ├─ (Du phong GPIO)
                             └───────────────────┘
                                     [USB-C]
```

### Bảng tra cứu chân chi tiết

| Cụm thiết bị | Chân linh kiện | Chân ESP32-S3 | Điện áp | Ghi chú kỹ thuật |
| :--- | :--- | :--- | :--- | :--- |
| **Màn hình GMT147SPI** | VCC | 3V3 | 3.3V | Lấy nguồn 3.3V từ board |
| | GND | GND | 0V | Nối mass chung |
| | SCL | **GPIO 40** | 3.3V | SPI Clock — Bắt buộc dùng bus SPI3 (HSPI) |
| | SDA | **GPIO 41** | 3.3V | MOSI (HSPI) |
| | CS  | **GPIO 39** | 3.3V | Chip Select |
| | DC  | **GPIO 38** | 3.3V | Data / Command |
| | RES | **GPIO 47** | 3.3V | Reset cứng màn hình |
| | BL  | 3V3 | 3.3V | **Nối thẳng 3.3V**, không nối GPIO48 để tránh đụng LED RGB |
| **Micro INMP441** | VDD | 3V3 | 3.3V | Không cấp 5V |
| | GND | GND | 0V | |
| | SCK | **GPIO 5** | 3.3V | I2S0 Bit Clock |
| | WS  | **GPIO 4** | 3.3V | I2S0 Word Select (LRCK) |
| | SD  | **GPIO 6** | 3.3V | I2S0 Serial Data In |
| | L/R | GND | 0V | Kéo xuống GND để thu kênh trái |
| **Loa MAX98357A** | VIN | **5V** | 5.0V | **Bắt buộc cấp 5V từ Buck** để đạt công suất 3W |
| | GND | GND | 0V | |
| | BCLK | **GPIO 15** | 3.3V | I2S1 Bit Clock |
| | LRC  | **GPIO 16** | 3.3V | I2S1 Word Select |
| | DIN  | **GPIO 17** | 3.3V | I2S1 Data Out |
| | SD_MODE | **GPIO 18** | 3.3V | Mute/Shutdown control (Active High) |
| | GAIN | GND | 0V | Mặc định 12dB (hoặc 100k lên GND để chọn 9dB) |
| **ToF VL53L0X/1X** | VIN | 3V3 | 3.3V | Cảm biến chạy 3.3V |
| | GND | GND | 0V | |
| | SDA | **GPIO 7** | 3.3V | I2C Data |
| | SCL | **GPIO 8** | 3.3V | I2C Clock |
| **4× Servo 180°** | VCC (Đỏ) | **5V Buck** | 5.0V | **Tuyệt đối không lấy từ 3.3V của ESP32** |
| | GND (Nâu/Đen) | GND | 0V | Nối mass chung về trạm nguồn |
| | Signal (Vàng/Cam) | **GPIO 9, 10, 11, 12** | 3.3V | Điều khiển xung PWM (LEDC channel 0..3, 50Hz) |
| **Status LED** | RGB LED | **GPIO 48** | 3.3V | Đèn WS2812 tích hợp sẵn trên board WeAct |

> [!NOTE]
> Cần tuân thủ phân tách 2 bus I2S riêng biệt trên ESP32-S3: **I2S0** dành cho Microphone thu âm (INMP441) và **I2S1** dành cho Speaker phát âm thanh (MAX98357A) để tránh nghẽn xung nhịp và nhiễu tín hiệu.

---

## ⚡ Kiến trúc Nguồn & Chống nhiễu Audio

1. **Dòng tải đỉnh (Peak Current)**:
   - ESP32-S3 phát WiFi + WebSocket: ~350mA.
   - Loa MAX98357A: ~500mA đỉnh ở 5V.
   - 4 Servo chuyển động đồng thời: Mỗi servo ăn dòng đỉnh 300mA – 600mA ➔ **Tổng 4 servo đỉnh từ 1.5A đến 2.4A!**
   - **Tổng dòng đỉnh toàn hệ thống: ~2.5A – 3.0A ở 5V.**
   - *Khuyến cáo*: Cấp nguồn bằng pin Li-ion 2S (7.4V – 8.4V) qua mạch **Buck WeAct (hạ áp ra 5V 3A)** kèm mạch sạc 2S cổng Type-C (IP2326 hoặc TP5100). Khi đang code để bàn, dùng củ sạc Type-C 5V 3A cắm trực tiếp.

2. **Chống nhiễu âm thanh (Star Grounding & Tụ lọc)**:
   - Động cơ chổi than trong servo khi quay sẽ sinh ra tia lửa điện và xung gai dội ngược về đường mass, gây tiếng rè/sôi loa hoặc lỗi micro.
   - **Tụ bù sụt áp**: Hàn song song **1 tụ hóa 470µF – 1000µF (10V/16V)** ngay tại trạm cấp nguồn 5V của 4 servo.
   - **Nối mass hình sao (Star Grounding)**: Dây mass GND từ ngõ ra của module Buck WeAct phải chia thành 2 nhánh độc lập:
     - *Nhánh 1*: Chạy thẳng về chân GND của 4 Servo.
     - *Nhánh 2*: Chạy về chân GND của ESP32, màn hình, Micro và Loa.
     - *Không đi dây GND nối tiếp (daisy-chain) qua cụm servo rồi mới về micro/loa*.

```
 [ Pin Lipo 2S (7.4V - 8.4V) / Nguon DC 9V-12V ]
                        │
                        ▼
         ┌───────────────────────────────┐
         │     WeAct Buck DC/DC (5V 3A)   │
         └──────────────┬────────────────┘
                        │ Đường nguồn 5.0V (Dây lớn >= 22AWG)
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
   ┌─────────────────┐     ┌────────────────────────┐
   │ Chân 5V ESP32-S3 │     │ VCC (+) 4 Động cơ Servo │
   │ (Nuôi MCU + TFT) │     │ (Dong khoi dong > 1.5A)│
   └─────────────────┘     └────────────────────────┘
            │                       │
            └───────────┬───────────┘
                        ▼
                 [ GND Chung ]
```

---

## ⚠️ Lưu ý Phần cứng ESP32-S3 WeAct (Gotchas)

- **Chân cấm sử dụng**:
  - `GPIO 0, 3, 45, 46`: Chân cấu hình khởi động (Strapping pins).
  - `GPIO 19, 20`: Kênh USB D- / D+ Native (dùng để nạp firmware và in Serial CDC).
  - `GPIO 35, 36, 37`: Kết nối trực tiếp với chip PSRAM OPI 8MB bên trong module. Không được cấu hình làm GPIO thường.
- **Cờ biên dịch màn hình**: Màn hình GMT147SPI cắm ở GPIO 40/41 bắt buộc phải định nghĩa cờ `-DUSE_HSPI_PORT=1` trong `platformio.ini` để thư viện `TFT_eSPI` sử dụng bộ điều khiển SPI3 (HSPI), tránh lỗi crash loop `StoreProhibited`.
- **Lỗi font TFT_eSPI**: Font 6 chỉ chứa số (0–9), không hiển thị được chữ cái. Để hiển thị chữ to cần dùng Font 4 với `tft.setTextSize(2)`.

---

## 🗺 Lộ trình Phát triển (Development Roadmap)

- [x] **Phase 1: Display & UI Engine**: Khởi tạo màn hình GMT147SPI, render ReShape Logo animation (Sprite 1bpp chống giật, ~35 FPS), thanh HUD stats và dải Marquee chạy chữ.
- [ ] **Phase 2: I2S Audio Bring-up**: Kiểm tra thu âm micro INMP441 và phát âm thanh qua MAX98357A.
- [ ] **Phase 3: Sensor & Servo Integration**: Đọc khoảng cách từ VL53L0X/1X, tạo thuật toán điều khiển 4 servo biểu cảm mượt mà (chuyển động gia tốc S-curve).
- [ ] **Phase 4: Xiaozhi Cloud AI Protocol**: Tích hợp giao thức WebSocket / MQTT kết nối server Xiaozhi (STT, LLM, TTS Opus streaming).
- [ ] **Phase 5: Emotional Facial Expressions**: Thiết kế bộ biểu cảm động (chớp mắt, lắng nghe, suy nghĩ, nói chuyện) khớp với trạng thái AI.

---

## 🔗 Liên kết Hệ sinh thái (Related Repos)

Dự án Xiaozhi Robot là một thành phần trong hệ sinh thái điều khiển nhúng **TRIAD / ReShape Lab**:

* **[QUAD-UAV](https://github.com/trungnguyenhpa-cpu/QUAD-UAV)**: Firmware điều khiển bay Quadcopter phối hợp ESP32 (Flight Link) và STM32F103 (Cascade PID).
* **[JS-CONTROLER](https://github.com/trungnguyenhpa-cpu/JS-CONTROLER)**: Firmware tay cầm điều khiển 2 joystick, màn hình kép TFT & OLED, âm thanh I2S.
* **[DRONE_TEST](https://github.com/gwaen-jung/DRONE_TEST)**: Workspace tổng hợp phát triển firmware và kiểm thử phần cứng.

---

<div align="center">
  <sub>Developed by <b>Cinq / ReShape Lab</b> • Robotics &amp; Autonomous Systems</sub>
</div>
"""

target_readme = r"d:/PlatformIO/Projects/esp32s3_weact_xiaozhirobot/README.md"
with open(target_readme, "w", encoding="utf-8") as f:
    f.write(readme_content)
print(f"Updated README.md at {target_readme}")
