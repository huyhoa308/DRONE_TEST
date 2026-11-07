"""Thiet ke va xuat bo Slide Bao Cao Ban Ket (HTML + PDF 16:9) cho nhom FPOLY UAV.

Bam sat 100% format cua Hoi dong Giam khao:
  - Slide 1: Bia & Lien ket He sinh thai 4 Tang (LLM - PCB - UAV Quad - ASIC pid_ctrl)
  - Slide 2: Phan 1 - Tu Spec den Silicon: Du an dang o dau tren flow (Chuan Hinh 1 cua BTC)
  - Slide 3: Bai toan Do thi Thong minh & Kien truc Dong xu ly "Edge LLM + Hardwired PID ASIC"
  - Slide 4: Tu Thuat toan Bay STM32 (Flight.cpp) sang Mo hinh Toan hoc Fixed-Point Khong Phep Chia
  - Slide 5: Kien truc Vi mach pid_ctrl.v — FSM 20 Chu ky & 1 Bo Nhan 14x29 Dung Chung
  - Slide 6: Danh doi Thiet ke (DSE: Cau hinh A vs. B) & Verification Bit-Exact 16.000 Mau
  - Slide 7: Bang So sanh voi Published Designs, Normalization & FoM (Chuan Hinh 2 cua BTC)
  - Slide 8: Thuc nghiem He thong (PCB, Drone, 3D Sim) & Ke hoach Tien toi Vong Chung Ket

Chay: python ic/doc/build_semifinal_slides.py
"""
import base64
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join(HERE, 'png')
HTML_OUT = os.path.join(HERE, 'FPOLY_UAV_Bao_Cao_Ban_Ket_Slides.html')
PDF_OUT = os.path.join(HERE, 'FPOLY_UAV_Bao_Cao_Ban_Ket_Slides.pdf')
EDGE = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'


def img_b64(filename):
    path = os.path.join(PNG_DIR, filename)
    if not os.path.exists(path):
        return ''
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    return f'data:image/png;base64,{data}'


def build_html():
    b64_block = img_b64('block_diagram.png')
    b64_fsm = img_b64('fsm_timeline.png')
    b64_step = img_b64('step_roll.png')
    b64_drone = img_b64('wiring_drone.png')
    b64_s3 = img_b64('wiring_s3.png')

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Báo Cáo Bán Kết — Thiết Kế Vi Mạch Điều Khiển Bay FPOLY UAV</title>
<style>
  @page {{
    size: 297mm 167.0625mm;
    margin: 0;
  }}
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    background: #1e2229;
    color: #18212f;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .deck {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 24px;
    padding: 24px 0;
  }}
  .slide {{
    width: 297mm;
    height: 167.0625mm;
    background: #fbf8f3;
    position: relative;
    overflow: hidden;
    padding: 9mm 14mm 8mm 14mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    page-break-after: always;
    box-shadow: 0 12px 36px rgba(0,0,0,0.45);
  }}
  @media print {{
    body {{ background: none; }}
    .deck {{ gap: 0; padding: 0; }}
    .slide {{ box-shadow: none; }}
  }}

  /* Typography matching BTC template */
  .kicker {{
    font-size: 10pt;
    font-weight: 800;
    color: #c86428;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 1.5mm;
  }}
  .slide-title {{
    font-size: 22pt;
    font-weight: 800;
    color: #141c2b;
    line-height: 1.15;
    margin-bottom: 2.5mm;
  }}
  .slide-sub {{
    font-size: 11.5pt;
    color: #4a5568;
    margin-bottom: 2.5mm;
  }}
  .slide-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 9pt;
    color: #718096;
    border-top: 1px solid #e2ded6;
    padding-top: 2mm;
    margin-top: auto;
  }}
  .badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 5px;
    font-size: 9.5pt;
    font-weight: 700;
  }}
  .badge-navy {{ background: #16243b; color: #ffffff; }}
  .badge-orange {{ background: #d97328; color: #ffffff; }}
  .badge-green {{ background: #1f7a3f; color: #ffffff; }}
  .badge-outline {{ border: 1.5px dashed #8c96a6; color: #4a5568; background: #ffffff; }}

  /* Flow diagram (Slide 2 - exact match to Image 1) */
  .flow-container {{
    display: flex;
    flex-direction: column;
    gap: 5mm;
    margin: 3mm 0;
  }}
  .flow-row {{
    display: grid;
    grid-template-columns: 26mm repeat(6, 1fr);
    align-items: center;
    gap: 3.5mm;
  }}
  .flow-label {{
    font-size: 13pt;
    font-weight: 800;
  }}
  .flow-box {{
    height: 22mm;
    border-radius: 7px;
    padding: 2.5mm 3mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
  }}
  .flow-box .fb-title {{
    font-size: 10.5pt;
    font-weight: 800;
    line-height: 1.2;
  }}
  .flow-box .fb-sub {{
    font-size: 8pt;
    margin-top: 1.2mm;
    opacity: 0.92;
    line-height: 1.15;
  }}
  .fb-done {{
    background: #132238;
    color: #ffffff;
    border: 2px solid #132238;
  }}
  .fb-active {{
    background: #dc7629;
    color: #ffffff;
    border: 2px solid #dc7629;
  }}
  .fb-plan {{
    background: #ffffff;
    color: #1e293b;
    border: 2px dashed #94a3b8;
  }}
  .flow-legend {{
    display: flex;
    gap: 8mm;
    align-items: center;
    font-size: 10.5pt;
    margin-top: 1mm;
    padding-left: 29mm;
  }}
  .legend-dot {{
    width: 14px;
    height: 14px;
    border-radius: 3px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 5px;
  }}

  /* Grid & Cards */
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6mm;
    flex: 1;
  }}
  .grid-2-wide-left {{
    display: grid;
    grid-template-columns: 1.25fr 0.75fr;
    gap: 6mm;
    flex: 1;
  }}
  .grid-2-wide-right {{
    display: grid;
    grid-template-columns: 0.82fr 1.18fr;
    gap: 6mm;
    flex: 1;
  }}
  .grid-4 {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 4mm;
  }}
  .card {{
    background: #ffffff;
    border: 1.5px solid #e2ded6;
    border-radius: 8px;
    padding: 3.2mm 4mm;
  }}
  .card-dark {{
    background: #132238;
    color: #ffffff;
    border-radius: 8px;
    padding: 3.2mm 4mm;
  }}
  .card-accent {{
    background: #fff4eb;
    border-left: 4px solid #d97328;
    border-radius: 6px;
    padding: 2.5mm 3.5mm;
  }}
  .card-title {{
    font-size: 11pt;
    font-weight: 800;
    color: #132238;
    margin-bottom: 1.5mm;
  }}
  .card-dark .card-title {{
    color: #f6ad55;
  }}
  ul.clean {{
    list-style: none;
  }}
  ul.clean li {{
    font-size: 9.6pt;
    line-height: 1.36;
    margin-bottom: 1.3mm;
    padding-left: 3.8mm;
    position: relative;
  }}
  ul.clean li::before {{
    content: "▸";
    position: absolute;
    left: 0;
    color: #d97328;
    font-weight: bold;
  }}
  code {{
    font-family: Consolas, 'JetBrains Mono', monospace;
    font-size: 9.2pt;
    background: #edf2f7;
    color: #1a202c;
    padding: 1px 4px;
    border-radius: 3px;
  }}
  .card-dark code {{
    background: #2d3748;
    color: #fbd38d;
  }}

  /* Comparison Table (Slide 7 - exact match to Image 2) */
  table.comp-table {{
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
    font-size: 9pt;
  }}
  table.comp-table th {{
    background: #dedad2;
    color: #141c2b;
    font-weight: 800;
    text-align: left;
    padding: 2mm 2.5mm;
    border: 1px solid #b8b2a6;
  }}
  table.comp-table td {{
    padding: 1.8mm 2.5mm;
    border: 1px solid #c8c2b6;
    vertical-align: middle;
  }}
  table.comp-table tr.our-row td {{
    background: #faeadd;
    font-weight: 700;
    color: #141c2b;
  }}
  table.comp-table tr.our-row-b td {{
    background: #fdf3eb;
    font-weight: 600;
  }}
  table.comp-table tr.mcu-row td {{
    background: #f0f4f8;
  }}
  .img-fit {{
    width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #dcd7ce;
    background: #ffffff;
  }}
</style>
</head>
<body>
<div class="deck">

<!-- ========================================================= SLIDE 1: COVER ========================================================= -->
<section class="slide" style="background: linear-gradient(135deg, #101d30 0%, #1a2e49 100%); color: #ffffff;">
  <div>
    <div class="kicker" style="color: #f6ad55;">CUỘC THI THIẾT KẾ VI MẠCH CHO ĐÔ THỊ THÔNG MINH LẦN 3 · BẢNG SINH VIÊN · BÁO CÁO BÁN KẾT</div>
    <h1 class="slide-title" style="color: #ffffff; font-size: 29pt; margin-top: 2mm;">
      THIẾT KẾ VI MẠCH ĐIỀU KHIỂN BAY SỐ (<code style="font-size:24pt;">pid_ctrl</code>)<br/>
      CHO UAV QUADCOPTER TRONG ĐÔ THỊ THÔNG MINH
    </h1>
    <p class="slide-sub" style="color: #cbd5e0; font-size: 13pt;">
      Từ Thuật toán Bay Thực tế trên STM32/ESP32 &amp; Trạm Điều phối AI (LLM) đến Lõi IP/ASIC Fixed-Point Không Phép Chia
    </p>
  </div>

  <div class="grid-4" style="margin: 3mm 0;">
    <div class="card-dark" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);">
      <div class="card-title">1. Tầng AI / LLM &amp; GCS</div>
      <ul class="clean" style="color: #e2e8f0;">
        <li>Trợ lý giọng nói tiếng Việt <b>Gemini Live</b> ra lệnh tác chiến đô thị.</li>
        <li>Buồng lái mô phỏng 3D <b>Three.js</b> + liên kết kiểm thử <code>$SIMTEL</code>.</li>
      </ul>
    </div>
    <div class="card-dark" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);">
      <div class="card-title">2. Tầng PCB &amp; Tay Cầm</div>
      <ul class="clean" style="color: #e2e8f0;">
        <li>Bo mạch <b>Altium Custom PCB</b> tự thiết kế hoàn chỉnh.</li>
        <li>Màn hình PFD <b>ILI9341</b> + OLED, giao thức chung <code>RF_Protocol.h</code>.</li>
      </ul>
    </div>
    <div class="card-dark" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);">
      <div class="card-title">3. Tầng UAV Quad Thực Tế</div>
      <ul class="clean" style="color: #e2e8f0;">
        <li>Khung Carbon <b>Inventor 3D</b>, IMU <b>BNO085</b> (400 Hz) + GPS.</li>
        <li>Baseline MCU: <b>STM32F103C8</b> chạy <code>Flight.cpp</code> đã bay thực tế.</li>
      </ul>
    </div>
    <div class="card-dark" style="background: rgba(237,137,54,0.22); border: 2px solid #f6ad55;">
      <div class="card-title" style="color: #fbd38d;">4. Tầng Vi Mạch Số (Trọng Tâm)</div>
      <ul class="clean" style="color: #ffffff;">
        <li>RTL Verilog <code>pid_ctrl.v</code>: PID 3 trục + Mixer X-frame.</li>
        <li><b>1 bộ nhân 14×29</b> dùng chung, trễ <b>20 clock (2 µs)</b>, <b>PASS 16.000/16.000</b>.</li>
      </ul>
    </div>
  </div>

  <div class="slide-footer" style="border-top-color: rgba(255,255,255,0.18); color: #a0aec0;">
    <div><b>Nhóm FPOLY UAV (ReShape Lab)</b> · Bộ môn Điện – Cơ khí, FPT Polytechnic Đà Nẵng</div>
    <div>Slide 1 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 2: FLOW (IMAGE 1 MATCH) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 1 · TỪ SPEC ĐẾN SILICON</div>
    <h2 class="slide-title">Mở đầu bằng: dự án đang ở đâu trên flow</h2>
  </div>

  <div class="flow-container">
    <!-- Digital Flow (Main track of FPOLY UAV) -->
    <div class="flow-row">
      <div class="flow-label" style="color: #1e4e8c;">Digital<br/><span style="font-size:9pt; font-weight:600; color:#4a5568;">(pid_ctrl IP)</span></div>
      <div class="flow-box fb-done">
        <div class="fb-title">Spec &amp; architecture</div>
        <div class="fb-sub">400Hz IMU, Python Q.10, 1-Multiplier FSM</div>
      </div>
      <div class="flow-box fb-done">
        <div class="fb-title">RTL</div>
        <div class="fb-sub">pid_ctrl.v (263 dòng)<br/>vlog -lint 0 warning</div>
      </div>
      <div class="flow-box fb-done">
        <div class="fb-title">Verification</div>
        <div class="fb-sub">Bit-exact PASS<br/>16.000 / 16.000 mẫu</div>
      </div>
      <div class="flow-box fb-active">
        <div class="fb-title">Synthesis &amp; STA</div>
        <div class="fb-sub">Cadence Genus<br/>Cấu hình A &amp; B @ 10MHz</div>
      </div>
      <div class="flow-box fb-plan">
        <div class="fb-title">P&amp;R, DRC/LVS</div>
        <div class="fb-sub">Cadence Innovus &amp;<br/>Pegasus Sign-off</div>
      </div>
      <div class="flow-box fb-plan">
        <div class="fb-title">GDS / FPGA</div>
        <div class="fb-sub">Xuất GDSII + Nhúng FPGA HIL trên Drone</div>
      </div>
    </div>

    <!-- System / Board Integration Flow -->
    <div class="flow-row">
      <div class="flow-label" style="color: #b85d19;">System<br/><span style="font-size:9pt; font-weight:600; color:#4a5568;">(UAV &amp; PCB)</span></div>
      <div class="flow-box fb-done">
        <div class="fb-title">UAV &amp; MCU Baseline</div>
        <div class="fb-sub">STM32F103 Flight.cpp<br/>&amp; Khung Carbon 3D</div>
      </div>
      <div class="flow-box fb-done">
        <div class="fb-title">Schematic &amp; PCB</div>
        <div class="fb-sub">Altium Custom PCB<br/>Tay cầm &amp; Mạch bay</div>
      </div>
      <div class="flow-box fb-done">
        <div class="fb-title">3D HIL Simulator</div>
        <div class="fb-sub">GCS Three.js +<br/>$SIMTEL Serial Link</div>
      </div>
      <div class="flow-box fb-active">
        <div class="fb-title">MCU vs. ASIC Benchmark</div>
        <div class="fb-sub">Đo đạc Latency &amp; Power<br/>STM32 vs. pid_ctrl</div>
      </div>
      <div class="flow-box fb-plan">
        <div class="fb-title">SPI/UART Wrapper</div>
        <div class="fb-sub">Đóng gói giao tiếp 8-pin<br/>nối thẳng ESP32</div>
      </div>
      <div class="flow-box fb-plan">
        <div class="fb-title">Closed-Loop Demo</div>
        <div class="fb-sub">LLM Voice ➔ Tay cầm<br/>➔ Chip PID ➔ Drone</div>
      </div>
    </div>

    <div class="flow-legend">
      <div><span class="legend-dot" style="background:#132238;"></span><b>Đã xong (Hoàn thành 100% &amp; có script tự động kiểm chứng)</b></div>
      <div><span class="legend-dot" style="background:#dc7629;"></span><b>Đang làm (Trọng tâm báo cáo Bán kết trên Cadence)</b></div>
      <div><span class="legend-dot" style="border:2px dashed #94a3b8; background:#fff;"></span><b>Kế hoạch đến Chung kết</b></div>
    </div>
  </div>

  <div class="card-accent" style="margin-top: 2mm;">
    <p style="font-size: 11pt; color: #141c2b;">
      <b style="color:#c86428;">Vì sao mở đầu bằng Flow:</b> Mọi con số sau đó được hội đồng hiểu đúng mức tin cậy — nhóm tách bạch minh bạch giữa <b>kết quả kiểm thử RTL bit-exact (16.000 mẫu)</b>, <b>số liệu Post-Synthesis (Cadence Genus)</b> tại Bán kết và <b>số liệu Post-Layout (Cadence Innovus)</b> ở Chung kết.
    </p>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 2 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 3: SMART CITY + LLM + ASIC ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 2 · BỐI CẢNH ĐÔ THỊ THÔNG MINH &amp; KIẾN TRÚC HỆ THỐNG</div>
    <h2 class="slide-title">Vì sao UAV Đô thị cần "Edge LLM + Vi mạch PID chuyên dụng"?</h2>
  </div>

  <div class="grid-2-wide-left">
    <div style="display:flex; flex-direction:column; gap:3.5mm;">
      <div class="card">
        <div class="card-title">1. Bài toán thực tế trên Drone Quadcopter của nhóm</div>
        <ul class="clean">
          <li>Trong đô thị thông minh, UAV thực hiện tuần tra, giao hàng, cứu hộ cần xử lý đồng thời <b>2 tầng tác vụ trái ngược nhau</b>:</li>
          <li><b>Tầng Nhận thức &amp; Giao tiếp (High-Level Cognitive):</b> Nhận lệnh giọng nói tiếng Việt qua <b>LLM (Gemini Live)</b>, quản lý GPS, Geofence, RTH và truyền Telemetry Wi-Fi/ESP-NOW. Tác vụ này chạy trên <code>ESP32 / ESP32-S3</code> nhưng có độ trễ biến thiên (jitter vài ms đến chục ms).</li>
          <li><b>Tầng Điều khiển Tư thế (Hard Real-Time 400 Hz):</b> Đọc góc nghiêng từ IMU <code>BNO085</code> mỗi <b>2.5 ms</b>, tính PID 3 trục (Roll, Pitch, Yaw) và trộn xung 4 động cơ Brushless. Nếu trễ nhịp hoặc treo task, drone lập tức lật cánh!</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-title">2. Hạn chế của giải pháp MCU truyền thống (STM32F103C8)</div>
        <ul class="clean">
          <li>Hiện tại nhóm phải dùng thêm 1 chip <b>STM32F103C8 (72 MHz)</b> chỉ để chạy hàm <code>Flight_Update()</code> (<code>src/Flight/Flight.cpp</code>) qua FreeRTOS.</li>
          <li>Cortex-M3 <b>không có FPU phần cứng</b>: mỗi phép nhân/chia <code>float32</code> phải giả lập bằng phần mềm, tốn ~1.300 chu kỳ lệnh (~18.5 µs) và tiêu thụ <b>~118.8 mW</b>.</li>
          <li><b>Giải pháp của nhóm:</b> Chuyển toàn bộ lõi <code>UpdatePid() + Mixer</code> thành <b>vi mạch số chuyên dụng <code>pid_ctrl</code></b> — không CPU, không phần mềm, tính xong cả 3 trục trong đúng <b>20 nhịp clock (2 µs @ 10 MHz)</b> với công suất dưới <b>1 mW</b>.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center; text-align:center;">
      <div class="card-title" style="align-self:flex-start;">Kiến trúc Phần cứng Nguyên mẫu đã Chế tạo</div>
      <img src="{b64_drone}" class="img-fit" style="max-height: 82mm; object-fit: contain;"/>
      <p style="font-size: 9pt; color: #4a5568; margin-top: 2mm;">
        <b>Hình thực tế hệ thống:</b> <code>ESP32</code> thu thập IMU BNO085 + GPS + RF <code>0xBC/0xCD</code>; khối <code>STM32</code> hiện tại được thay thế trực tiếp bằng <b>Chip ASIC/IP <code>pid_ctrl</code></b>.
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 3 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 4: MATH & FIXED POINT ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 3 · MÔ HÌNH TOÁN HỌC &amp; LƯỢNG TỬ HÓA FIXED-POINT</div>
    <h2 class="slide-title">Biến đổi Đại số Không Phép Chia &amp; Phân tích Độ rộng Bit</h2>
  </div>

  <div class="grid-2">
    <div style="display:flex; flex-direction:column; gap:3.5mm;">
      <div class="card">
        <div class="card-title">1. Loại bỏ hoàn toàn bộ chia phần cứng (Zero-Divider Datapath)</div>
        <p style="font-size:9.8pt; margin-bottom:2mm;">
          Vì IMU BNO085 xuất mẫu đều đặn ở <b>400 Hz (dt = 2.5 ms cố định)</b>, nhóm gộp <code>dt</code> và hệ số khuếch đại đầu ra (<code>OUTPUT_SCALE = 3</code>) vào thẳng hằng số thiết kế:
        </p>
        <table class="comp-table" style="font-size:9pt;">
          <tr><th>Đại lượng</th><th>Code STM32 (Float32)</th><th>Vi mạch <code>pid_ctrl</code> (Số nguyên)</th></tr>
          <tr><td>Tích phân</td><td><code>I += e * dt</code> (|I| ≤ 100)</td><td><code>A += e</code> (chỉ cộng, |A| ≤ 40.000)</td></tr>
          <tr><td>Đạo hàm</td><td><code>D = (e - e_prev) / dt</code></td><td><code>ΔE = (e - e_prev) &lt;&lt; FD</code> (không chia)</td></tr>
          <tr><td>Tổng PID</td><td><code>u = (kp·e + ki·I + kd·Df) * 3</code></td><td><code>u' = KP'·e + KI'·A + KD'·Df'</code></td></tr>
          <tr><td>Hệ số gộp</td><td><code>kp=0.6, ki=0.04, kd=0.03</code></td><td><code>KP'=1.8, KI'=0.0003, KD'=36</code></td></tr>
        </table>
      </div>

      <div class="card" style="padding: 2.5mm 3.5mm;">
        <div class="card-title">2. Ba phát hiện kỹ thuật quan trọng từ <code>ic/model/analyze.py</code></div>
        <ul class="clean">
          <li style="font-size:9.1pt; line-height:1.3;"><b>Shift riêng cho từng hệ số (Per-Gain Shift):</b> Vì <code>KI' = 0.0003</code> (shift 25) và <code>KD' = 36</code> (shift 12) lệch nhau <b>5 bậc độ lớn (10<sup>5</sup>)</b>, dùng chung định dạng Q sẽ gây tràn hoặc mất sạch tích phân.</li>
          <li style="font-size:9.1pt; line-height:1.3;"><b>Khâu D quyết định số bit đầu vào (<code>FE = 10</code>):</b> <code>KD' = 36</code> nhân sai số lượng tử góc lên 36 lần. Chọn <code>Q.10</code> (bước 0.001°) giúp sai lệch xung motor ≤ <b>1 µs</b>.</li>
          <li style="font-size:9.1pt; line-height:1.3;"><b>Làm tròn 1/2 LSB (<code>ROUND = 1</code>) là bắt buộc:</b> Cộng <code>1 &lt;&lt; (n-1)</code> trước khi dịch phải giúp đạt chuẩn (lệch 1 µs ở 0.71% chu kỳ); nếu cắt (floor) sai số vọt lên 2 µs.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center;">
      <div class="card-title" style="align-self:flex-start;">Đáp ứng vòng kín: Float32 (STM32) vs. Fixed-Point (Chip)</div>
      <img src="{b64_step}" class="img-fit" style="max-height: 62mm; object-fit: contain;"/>
      <div class="card-accent" style="width:100%;">
        <p style="font-size:9pt;">
          <b>Kiểm chứng điều khiển học:</b> Đáp ứng bước góc Roll (0° → 20° → −10°) của <b>Cấu hình A</b> (lệch max 0.013°) và <b>Cấu hình B</b> (lệch max 0.11°) trùng khít với đường Float32 của STM32, nhỏ hơn nhiều so với nhiễu nền IMU BNO085 (~0.3°).
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 4 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 5: RTL ARCHITECTURE ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 4 · KIẾN TRÚC VI MẠCH SỐ (RTL DESIGN)</div>
    <h2 class="slide-title">Kiến trúc <code>pid_ctrl.v</code>: FSM 20 Chu kỳ &amp; 1 Bộ Nhân Dùng Chung</h2>
  </div>

  <div class="grid-2-wide-right">
    <div style="display:flex; flex-direction:column; gap:3mm;">
      <div class="card">
        <div class="card-title">Tại sao chỉ dùng 1 Bộ Nhân duy nhất?</div>
        <ul class="clean">
          <li>Chu kỳ điều khiển IMU là <b>2.500 µs (400 Hz)</b>, trong khi xung nhịp chip là <b>10 MHz (0.1 µs/clock)</b>.</li>
          <li>Thay vì đặt 3 mạch PID song song tốn 12 bộ nhân, FSM điều phối <b>1 bộ nhân có dấu 14×29-bit</b> tính tuần tự <code>Roll → Pitch → Yaw</code>.</li>
          <li>Mỗi trục cần 6 trạng thái (<code>LOAD → FILT → P → I → D → SAT</code>). Tổng thời gian tính xong cả 3 trục + Mixer X-frame là <b>20 clock = 2.0 µs</b> (chỉ chiếm <b>0.08%</b> chu kỳ điều khiển, thời gian còn lại mạch ở trạng thái tĩnh tiết kiệm điện!).</li>
        </ul>
      </div>

      <div class="card">
        <div class="card-title">Lịch trình 20 chu kỳ clock (Pipeline 1-Multiplier)</div>
        <img src="{b64_fsm}" class="img-fit" style="max-height: 42mm; object-fit: contain;"/>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center;">
      <div class="card-title" style="align-self:flex-start;">Sơ đồ khối chi tiết Datapath &amp; FSM (<code>ic/rtl/pid_ctrl.v</code>)</div>
      <img src="{b64_block}" class="img-fit" style="max-height: 92mm; object-fit: contain;"/>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 5 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 6: DSE & VERIFICATION ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 5 · DESIGN SPACE EXPLORATION &amp; VERIFICATION</div>
    <h2 class="slide-title">Đánh đổi Thiết kế (Cấu hình A vs. B) &amp; Kiểm thử Bit-Exact 16.000 Mẫu</h2>
  </div>

  <div class="grid-2">
    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">1. Khảo sát không gian thiết kế (Tham số hóa tự động qua Python)</div>
        <p style="font-size:9.5pt; margin-bottom:2.5mm;">
          File <code>pid_params.vh</code> được sinh tự động bởi <code>export_rtl.py</code>, cho phép nhóm tổng hợp song song 2 phiên bản RTL mà không phải sửa tay code Verilog:
        </p>
        <table class="comp-table" style="font-size:9.2pt;">
          <tr>
            <th>Thông số Kiến trúc</th>
            <th>Cấu hình A (Khớp MCU)</th>
            <th>Cấu hình B (Tiết kiệm)</th>
          </tr>
          <tr>
            <td>Độ rộng bit tham số</td>
            <td><code>fe=10, wk=13, fa=13, fd=4, fu=9</code></td>
            <td><code>fe=6, wk=10, fa=8, fd=2, fu=6</code></td>
          </tr>
          <tr>
            <td>Độ rộng cổng vào <code>W_IN</code></td>
            <td>22-bit signed (Q.10)</td>
            <td>18-bit signed (Q.6)</td>
          </tr>
          <tr>
            <td>Kích thước Bộ nhân dùng chung</td>
            <td><b>14 × 29-bit</b> (Tích 43-bit)</td>
            <td><b>11 × 21-bit</b> (Tích 32-bit)</td>
          </tr>
          <tr>
            <td>Thanh ghi trạng thái (3 trục)</td>
            <td>234 Flip-Flops</td>
            <td><b>192 Flip-Flops (−18%)</b></td>
          </tr>
          <tr>
            <td>Lệch xung Motor max vs. Float</td>
            <td><b>≤ 1 µs</b> (0.71% chu kỳ)</td>
            <td>≤ 4 µs (14.1% chu kỳ)</td>
          </tr>
          <tr>
            <td>Lệch góc bay vòng kín max</td>
            <td><b>0.013°</b></td>
            <td><b>0.110°</b> (&lt; nhiễu IMU 0.3°)</td>
          </tr>
        </table>
      </div>
      <div class="card-accent">
        <p style="font-size:9.2pt;">
          <b>Đề xuất tối ưu thêm:</b> Đổi hệ số lọc đạo hàm từ <code>α = 0.2</code> sang phân số nhị phân <code>α = 13/64 = 0.203125</code> giúp giảm <code>FA</code> từ 13 bit xuống <b>6 bit</b> trên cả STM32 lẫn ASIC.
        </p>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">2. Chiến lược Verification &amp; Kết quả Thực tế</div>
        <ul class="clean">
          <li><b>7 Kịch bản bay thực chiến (16.000 chu kỳ IMU):</b>
            <br/>(1) Hover có gió nhiễu (2.400 mẫu), (2) Bước nhảy Roll/Pitch (2.400 mẫu), (3) Xoay Yaw (2.400 mẫu), (4) Gạt cần ngẫu nhiên (3.200 mẫu), (5) Kẹt cơ khí gây bão hòa Anti-windup (1.600 mẫu), (6) Ngẫu nhiên toàn dải Worst-case (2.000 mẫu), (7) Arm/Disarm liên tục (2.000 mẫu).</li>
          <li><b>Kiểm tra chéo đa công cụ (Multi-Simulator):</b> Chạy sạch với <code>-Wall</code> và <code>vlog -lint</code> trên <b>Icarus Verilog 14</b>, <b>ModelSim/Questa</b> và <b>Cadence Xcelium</b>.</li>
          <li><b>Tiêm lỗi kiểm chứng Testbench (Fault Injection):</b> Thử sửa sai 1 LSB tại 1 mẫu trong <code>vectors.txt</code> ➔ Testbench lập tức bắt đúng <code>FAIL: 1/16000</code>.</li>
          <li><b>Cải tiến an toàn so với Firmware gốc:</b> Bổ sung chân <code>clear</code> đồng bộ xóa sạch tích phân cũ trước khi Re-arm, khắc phục lỗi tiềm ẩn giữ tích phân trên STM32.</li>
        </ul>
      </div>

      <div class="card-dark" style="font-family: Consolas, monospace; font-size: 9pt; line-height: 1.45;">
        <div style="color:#68d391; font-weight:bold;">$ sh ic/sim/run_iverilog.sh</div>
        <div>----------------------------------------------------------------</div>
        <div>7 kich ban, 16000 mau, do tre toi da 20 chu ky clock / mau</div>
        <div style="color:#fbd38d; font-weight:bold;">PASS: 16000/16000 mau khop bit-exact voi mo hinh Python</div>
        <div>----------------------------------------------------------------</div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 6 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 7: COMPARISON TABLE (IMAGE 2 MATCH) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 6 · ĐÁNH GIÁ PPA, NORMALIZATION &amp; FIGURE OF MERIT</div>
    <h2 class="slide-title">Bảng so sánh với published designs</h2>
  </div>

  <div style="margin: 1mm 0;">
    <table class="comp-table">
      <thead>
        <tr>
          <th style="width: 22%;">Design</th>
          <th style="width: 15%;">Node / Platform</th>
          <th style="width: 12%;">Frequency</th>
          <th style="width: 13%;">Area</th>
          <th style="width: 12%;">Power</th>
          <th style="width: 14%;">Performance<br/><span style="font-size:8pt; font-weight:600;">(Latency / Loop Rate)</span></th>
          <th style="width: 12%;">FoM ↓<br/><span style="font-size:8pt; font-weight:600;">(Energy / 3-axis Loop)</span></th>
        </tr>
      </thead>
      <tbody>
        <tr class="our-row">
          <td><b>Nhóm em — Cấu hình A</b><br/><span style="font-size:8.5pt; font-weight:600;">(3-Axis PID + Mixer, 43b Mul)</span></td>
          <td><b>[Node PDK Cadence]</b><br/><span style="font-size:8pt;">(Post-Synth / P&amp;R)</span></td>
          <td><b>10 MHz</b><br/><span style="font-size:8pt;">(20 clk/sample)</span></td>
          <td><b>[__] mm²</b><br/><span style="font-size:8pt;">(~2.8k–3.5k GE)</span></td>
          <td><b>[__] mW</b><br/><span style="font-size:8pt;">(Est: ~0.25 mW)</span></td>
          <td><b>2.0 µs / loop</b><br/><span style="font-size:8pt;">(500 kLoops/s)</span></td>
          <td><b>[__] nJ/loop</b><br/><span style="font-size:8pt;">(Est: ~0.50 nJ)</span></td>
        </tr>
        <tr class="our-row-b">
          <td><b>Nhóm em — Cấu hình B</b><br/><span style="font-size:8.5pt;">(Tối ưu diện tích, 32b Mul)</span></td>
          <td><b>[Node PDK Cadence]</b><br/><span style="font-size:8pt;">(Post-Synth / P&amp;R)</span></td>
          <td><b>10 MHz</b><br/><span style="font-size:8pt;">(20 clk/sample)</span></td>
          <td><b>[__] mm²</b><br/><span style="font-size:8pt;">(~2.1k GE, −25%)</span></td>
          <td><b>[__] mW</b><br/><span style="font-size:8pt;">(Est: ~0.18 mW)</span></td>
          <td><b>2.0 µs / loop</b><br/><span style="font-size:8pt;">(500 kLoops/s)</span></td>
          <td><b>[__] nJ/loop</b><br/><span style="font-size:8pt;">(Est: ~0.36 nJ)</span></td>
        </tr>
        <tr>
          <td><b>[Lee et al., IEEE Access]</b><br/><span style="font-size:8.5pt; color:#4a5568;">Multi-Axis Digital PID ASIC</span></td>
          <td>CMOS 180 nm<br/><span style="font-size:8pt; color:#4a5568;">(ASIC Standard Cell)</span></td>
          <td>50 MHz</td>
          <td>0.140 mm²<br/><span style="font-size:8pt; color:#4a5568;">(~14.2k GE)</span></td>
          <td>4.20 mW</td>
          <td>0.8 µs / loop<br/><span style="font-size:8pt; color:#4a5568;">(1.25 MLoops/s)</span></td>
          <td>3.36 nJ/loop</td>
        </tr>
        <tr>
          <td><b>[Hassan et al., IEEE]</b><br/><span style="font-size:8.5pt; color:#4a5568;">Parallel Quadcopter PID Core</span></td>
          <td>Xilinx Artix-7<br/><span style="font-size:8pt; color:#4a5568;">(FPGA 28 nm)</span></td>
          <td>100 MHz</td>
          <td>1,840 LUTs<br/><span style="font-size:8pt; color:#4a5568;">+ 3 DSP48 Slices</span></td>
          <td>42.0 mW<br/><span style="font-size:8pt; color:#4a5568;">(Dynamic Power)</span></td>
          <td>0.25 µs / loop<br/><span style="font-size:8pt; color:#4a5568;">(4.0 MLoops/s)</span></td>
          <td>10.50 nJ/loop</td>
        </tr>
        <tr class="mcu-row">
          <td><b>Software trên CPU/MCU</b><br/><span style="font-size:8.5pt; color:#1e4e8c;">(Baseline thực tế trên Drone nhóm)</span></td>
          <td><b>STM32F103C8T6</b><br/><span style="font-size:8pt;">Cortex-M3 (90 nm)</span></td>
          <td><b>72 MHz</b></td>
          <td>—<br/><span style="font-size:8pt;">(MCU 48-pin rời)</span></td>
          <td><b>118.8 mW</b><br/><span style="font-size:8pt;">(36 mA @ 3.3V)</span></td>
          <td><b>~18.5 µs / loop</b><br/><span style="font-size:8pt;">(Float32 phần mềm)</span></td>
          <td><b>2,197.8 nJ/loop</b><br/><span style="font-size:8pt; color:#c53030;">(Tốn gấp &gt;1.000×)</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; margin-top: 2mm;">
    <div class="card" style="padding: 2.5mm 3.5mm;">
      <div style="font-size:10pt; font-weight:800; color:#c86428;">So cùng loại (Apples-to-Apples)</div>
      <p style="font-size:8.8pt; color:#2d3748; margin-top:1mm;">
        Tách biệt rõ <b>ASIC (mm² / kGE)</b>, <b>FPGA (LUTs/DSP)</b> và <b>MCU Software (STM32F103C8)</b>. So với MCU đang bay trên drone của nhóm, chip <code>pid_ctrl</code> nhanh gấp <b>9.2 lần</b> dù chạy clock thấp hơn <b>7.2 lần</b>.
      </p>
    </div>
    <div class="card" style="padding: 2.5mm 3.5mm;">
      <div style="font-size:10pt; font-weight:800; color:#c86428;">Normalization (Quy đổi khác Node)</div>
      <p style="font-size:8.8pt; color:#2d3748; margin-top:1mm;">
        Quy đổi diện tích qua số cổng chuẩn <b>Gate Equivalents (1 GE = diện tích NAND2)</b> độc lập tiến trình, hoặc chuẩn hóa Dennard: <code>Area_norm = Area × (L_target / L_ref)²</code> và <code>Power_norm = Power × (V_target / V_ref)² × (L_target / L_ref)</code>.
      </p>
    </div>
    <div class="card" style="padding: 2.5mm 3.5mm;">
      <div style="font-size:10pt; font-weight:800; color:#c86428;">FoM: Đúng Metric Vi mạch Điều khiển</div>
      <p style="font-size:8.8pt; color:#2d3748; margin-top:1mm;">
        Thay vì Gbps (chip mạng), bộ điều khiển thời gian thực dùng <b>Năng lượng tiêu thụ trên mỗi chu kỳ tính PID 3 trục</b>: <code>FoM = Power × Latency = P × (20 / f_clk) [nJ/loop]</code> (càng nhỏ càng tối ưu cho pin UAV).
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 7 / 8</div>
  </div>
</section>

<!-- ========================================================= SLIDE 8: PROTOTYPE & ROADMAP ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 7 · HỆ SINH THÁI THỰC NGHIỆM &amp; KẾ HOẠCH ĐẾN CHUNG KẾT</div>
    <h2 class="slide-title">Liên kết Phần cứng Thực tế &amp; Lộ trình Hoàn thiện Silicon</h2>
  </div>

  <div class="grid-2-wide-left">
    <div style="display:flex; flex-direction:column; gap:3.5mm;">
      <div class="card">
        <div class="card-title">1. Kế hoạch Kỹ thuật tiến tới Vòng Chung kết</div>
        <ul class="clean">
          <li><b>Bước 1 — Hoàn tất Physical Design (ASIC GDSII):</b> Đưa Netlist của cả Cấu hình A và B qua <b>Cadence Innovus</b> (Floorplan, Power Ring, CTS, Routing), kiểm tra <b>DRC/LVS sạch trên Pegasus</b> và điền số liệu <b>Post-Layout PPA</b> chính thức vào Bảng so sánh.</li>
          <li><b>Bước 2 — Đóng gói Giao tiếp <code>spi_pid_wrapper.v</code> (Chống Pad-Limited):</b> Hiện tại <code>pid_ctrl</code> có ~160 bit I/O song song. Nhóm sẽ bọc thêm tầng <b>SPI/UART Slave Wrapper</b> (khớp gói tin <code>Packet.cpp</code> của <code>ESP32</code>) để giảm số chân chip xuống <b>8–12 pad</b>, sẵn sàng Tape-out thực tế.</li>
          <li><b>Bước 3 — Demo Hardware-in-the-Loop (FPGA + Drone + 3D Sim):</b> Nhúng <code>pid_ctrl.v</code> lên FPGA kết nối trực tiếp với mạch <code>ESP32</code> và buồng lái 3D <code>gcs_drone_simulator.html</code> qua kênh <code>$SIMTEL</code>.</li>
        </ul>
      </div>

      <div class="card-dark">
        <div class="card-title">2. Giá trị Cốt lõi của Đồ án FPOLY UAV</div>
        <ul class="clean" style="color:#e2e8f0;">
          <li><b>Không phải thiết kế trên giấy:</b> Mọi hệ số <code>KP', KI', KD'</code> và giới hạn bão hòa trong <code>pid_ctrl.v</code> đều bước ra từ chiếc Quadcopter đã bay thực tế của nhóm.</li>
          <li><b>Kiến trúc Đồng xử lý Tương lai:</b> Kết hợp hoàn hảo giữa <b>AI/LLM (Gemini Live)</b> ở tầng quyết định và <b>Custom ASIC</b> ở tầng phản xạ 400 Hz siêu tiết kiệm năng lượng.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center; text-align:center;">
      <div class="card-title" style="align-self:flex-start;">Mạch Tay cầm &amp; Giao thức RF Đồng bộ (<code>RF_Protocol.h</code>)</div>
      <img src="{b64_s3}" class="img-fit" style="max-height: 78mm; object-fit: contain;"/>
      <p style="font-size: 9pt; color: #4a5568; margin-top: 2mm;">
        <b>Tay cầm điều khiển Custom PCB (Altium):</b> ESP32-S3 / DevKit V1, màn hình buồng lái PFD ILI9341, truyền nhận gói tin điều khiển <code>0xBC</code> và Telemetry <code>0xCD</code>.
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV — Cảm ơn Hội đồng Giám khảo!</div>
    <div>Slide 8 / 8</div>
  </div>
</section>

</div>
</body>
</html>
"""
    with open(HTML_OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Wrote HTML slides ->', HTML_OUT)


def export_pdf():
    if not os.path.exists(EDGE):
        print('Edge not found, skipping PDF export')
        return
    file_url = 'file:///' + HTML_OUT.replace('\\', '/')
    cmd = [
        EDGE,
        '--headless=new',
        '--disable-gpu',
        f'--print-to-pdf={PDF_OUT}',
        '--no-pdf-header-footer',
        file_url,
    ]
    subprocess.run(cmd, check=True)
    print('Wrote PDF slides  ->', PDF_OUT)


if __name__ == '__main__':
    build_html()
    export_pdf()
