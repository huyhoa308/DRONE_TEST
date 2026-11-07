"""Thiet ke va xuat bo Slide Bao Cao Ban Ket 12 Trang (HTML + PDF 16:9) cho nhom FPOLY UAV.

Bam sat 100% tat ca cac slide huong dan cua Ban To Chuc (BTC):
  - Slide 1: Bia, "Cau gioi thieu mot dong" (One-Line Pitch) & Lien ket He sinh thai 4 Tang
  - Slide 2: Phan 1 - Tu Spec den Silicon: Du an dang o dau tren flow (Chuan Hinh 1 cua BTC) + Bang Spec co so va dieu kien
  - Slide 3: Bai toan Do thi Thong minh & Kien truc Dong xu ly "Edge LLM + Hardwired PID ASIC"
  - Slide 4: Tu Thuat toan Bay STM32 (Flight.cpp) sang Mo hinh Toan hoc Fixed-Point Khong Phep Chia
  - Slide 5: Kien truc Vi mach pid_ctrl.v — FSM 20 Chu ky & 1 Bo Nhan 14x29 Dung Chung
  - Slide 6: Danh doi Thiet ke (DSE: Cau hinh A vs. B) & Verification Bit-Exact 16.000 Mau
  - Slide 7: Bang So sanh voi Published Designs, Normalization, FoM, Nhan bac & Corner (Chuan Hinh 2 cua BTC)
  - Slide 8: Mot khung quay man hinh thuyet phuc (4 vung 1-2-3-4: Waveform + Self-checking log + Hardware + Phu de)
  - Slide 9: Demo truc tiep: Luon co phuong an A, B va C + Kich ban Video & Phan vai
  - Slide 10: Checklist truoc Vong hoan thien san pham (12/12 muc Design, Bai trinh bay, Video & Demo) & Lo trinh Chung ket
  - Slide 11: [SLIDE DU PHONG 1 - Q&A] Phan tich Chi tiet Timing (Critical Path) & Power (Dynamic/Leakage/Idle Gating)
  - Slide 12: [SLIDE DU PHONG 2 - Q&A] Verification Coverage Matrix (FSM, Datapath, Anti-Windup) & Giao tiep SPI Wrapper

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
    b64_wave = img_b64('waveform_zoom.png')

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Báo Cáo Bán Kết — Thiết Kế Vi Mạch Điều Khiển Bay FPOLY UAV (12 Slides)</title>
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
    padding: 8.5mm 14mm 7.5mm 14mm;
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
    font-size: 9.8pt;
    font-weight: 800;
    color: #c86428;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 1.2mm;
  }}
  .slide-title {{
    font-size: 21.5pt;
    font-weight: 800;
    color: #141c2b;
    line-height: 1.15;
    margin-bottom: 2.2mm;
  }}
  .slide-sub {{
    font-size: 11pt;
    color: #4a5568;
    margin-bottom: 2mm;
  }}
  .slide-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 8.8pt;
    color: #718096;
    border-top: 1px solid #e2ded6;
    padding-top: 1.8mm;
    margin-top: auto;
  }}

  /* Flow diagram (Slide 2 - exact match to Image 1) */
  .flow-container {{
    display: flex;
    flex-direction: column;
    gap: 3.2mm;
    margin: 1mm 0;
  }}
  .flow-row {{
    display: grid;
    grid-template-columns: 25mm repeat(6, 1fr);
    align-items: center;
    gap: 3mm;
  }}
  .flow-label {{
    font-size: 12pt;
    font-weight: 800;
  }}
  .flow-box {{
    height: 18.5mm;
    border-radius: 7px;
    padding: 2mm 2.5mm;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
  }}
  .flow-box .fb-title {{
    font-size: 9.8pt;
    font-weight: 800;
    line-height: 1.15;
  }}
  .flow-box .fb-sub {{
    font-size: 7.6pt;
    margin-top: 1mm;
    opacity: 0.92;
    line-height: 1.12;
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
    gap: 7mm;
    align-items: center;
    font-size: 9.5pt;
    padding-left: 28mm;
  }}
  .legend-dot {{
    width: 12px;
    height: 12px;
    border-radius: 3px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 5px;
  }}

  /* Grid & Cards */
  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 5mm;
    flex: 1;
  }}
  .grid-2-wide-left {{
    display: grid;
    grid-template-columns: 1.24fr 0.76fr;
    gap: 5mm;
    flex: 1;
  }}
  .grid-2-wide-right {{
    display: grid;
    grid-template-columns: 0.82fr 1.18fr;
    gap: 5mm;
    flex: 1;
  }}
  .grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4.5mm;
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
    padding: 3mm 3.8mm;
  }}
  .card-dark {{
    background: #132238;
    color: #ffffff;
    border-radius: 8px;
    padding: 3mm 3.8mm;
  }}
  .card-accent {{
    background: #fff4eb;
    border-left: 4px solid #d97328;
    border-radius: 6px;
    padding: 2.2mm 3.5mm;
  }}
  .card-title {{
    font-size: 10.8pt;
    font-weight: 800;
    color: #132238;
    margin-bottom: 1.4mm;
  }}
  .card-dark .card-title {{
    color: #f6ad55;
  }}
  ul.clean {{
    list-style: none;
  }}
  ul.clean li {{
    font-size: 9.4pt;
    line-height: 1.35;
    margin-bottom: 1.2mm;
    padding-left: 3.6mm;
    position: relative;
  }}
  ul.clean li::before {{
    content: "▸";
    position: absolute;
    left: 0;
    color: #d97328;
    font-weight: bold;
  }}
  ul.check-list {{
    list-style: none;
  }}
  ul.check-list li {{
    font-size: 9.3pt;
    line-height: 1.38;
    margin-bottom: 1.5mm;
    padding-left: 5mm;
    position: relative;
  }}
  ul.check-list li::before {{
    content: "☑";
    position: absolute;
    left: 0;
    color: #1f7a3f;
    font-weight: bold;
  }}
  code {{
    font-family: Consolas, 'JetBrains Mono', monospace;
    font-size: 8.9pt;
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
    font-size: 8.8pt;
  }}
  table.comp-table th {{
    background: #dedad2;
    color: #141c2b;
    font-weight: 800;
    text-align: left;
    padding: 1.8mm 2.4mm;
    border: 1px solid #b8b2a6;
  }}
  table.comp-table td {{
    padding: 1.6mm 2.4mm;
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
  .num-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #ea8030;
    color: #141c2b;
    font-weight: 900;
    font-size: 10pt;
    margin-right: 5px;
    flex-shrink: 0;
  }}
  .tag-pill {{
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 7.5pt;
    font-weight: 700;
    background: #132238;
    color: #fbd38d;
    margin-top: 2px;
  }}
</style>
</head>
<body>
<div class="deck">

<!-- ========================================================= SLIDE 1: COVER + ONE-LINE PITCH ========================================================= -->
<section class="slide" style="background: linear-gradient(135deg, #101d30 0%, #1a2e49 100%); color: #ffffff;">
  <div>
    <div class="kicker" style="color: #f6ad55;">CUỘC THI THIẾT KẾ VI MẠCH CHO ĐÔ THỊ THÔNG MINH LẦN 3 · BẢNG SINH VIÊN · BÁO CÁO BÁN KẾT</div>
    <h1 class="slide-title" style="color: #ffffff; font-size: 26pt; margin-top: 1.5mm;">
      THIẾT KẾ VI MẠCH ĐIỀU KHIỂN BAY SỐ (<code style="font-size:22pt;">pid_ctrl</code>)<br/>
      CHO UAV QUADCOPTER TRONG ĐÔ THỊ THÔNG MINH
    </h1>
    <!-- One-line pitch required by BTC Checklist -->
    <div style="background: rgba(237,137,54,0.18); border-left: 4px solid #f6ad55; padding: 2.5mm 4mm; border-radius: 6px; margin-top: 2mm;">
      <p style="font-size: 10.8pt; color: #fefcbf; line-height: 1.35;">
        <b>Câu giới thiệu một dòng (One-Line Pitch):</b> Chuyển hóa thuật toán điều khiển bay PID 3 trục + Mixer đã bay thực tế trên STM32 thành <b>lõi IP vi mạch số không phép chia, dùng chung 1 bộ nhân</b>, hoàn thành chu kỳ tính trong <b>2.0 µs (@ 10 MHz)</b> — nhanh gấp <b>9.2×</b> và tiết kiệm năng lượng gấp <b>&gt;1.000×</b> so với MCU.
      </p>
    </div>
  </div>

  <div class="grid-4" style="margin: 2.5mm 0;">
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
    <div class="card-dark" style="background: rgba(237,137,54,0.24); border: 2px solid #f6ad55;">
      <div class="card-title" style="color: #fbd38d;">4. Tầng Vi Mạch Số (Trọng Tâm)</div>
      <ul class="clean" style="color: #ffffff;">
        <li>RTL Verilog <code>pid_ctrl.v</code> + <code>spi_pid_wrapper.v</code>.</li>
        <li><b>1 bộ nhân 14×29</b> dùng chung, trễ <b>20 clock (2 µs)</b>, <b>PASS 16.000/16.000</b>.</li>
      </ul>
    </div>
  </div>

  <div class="slide-footer" style="border-top-color: rgba(255,255,255,0.18); color: #a0aec0;">
    <div><b>Nhóm FPOLY UAV (ReShape Lab)</b> · Bộ môn Điện – Cơ khí, FPT Polytechnic Đà Nẵng</div>
    <div>Slide 1 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 2: FLOW + SPEC WITH CONDITIONS (IMAGE 1 + CHECKLIST) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 1 · TỪ SPEC ĐẾN SILICON</div>
    <h2 class="slide-title">Mở đầu bằng: dự án đang ở đâu trên flow &amp; Bảng Spec</h2>
  </div>

  <div class="flow-container">
    <div class="flow-row">
      <div class="flow-label" style="color: #1e4e8c;">Digital<br/><span style="font-size:8.5pt; font-weight:600; color:#4a5568;">(pid_ctrl IP)</span></div>
      <div class="flow-box fb-done">
        <div class="fb-title">Spec &amp; architecture</div>
        <div class="fb-sub">400Hz IMU, Python Q.10, 1-Multiplier FSM</div>
      </div>
      <div class="flow-box fb-done">
        <div class="fb-title">RTL</div>
        <div class="fb-sub">pid_ctrl.v + SPI wrap<br/>vlog -lint 0 warning</div>
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
        <div class="fb-sub">Xuất GDSII + Nhúng<br/>FPGA HIL trên Drone</div>
      </div>
    </div>

    <div class="flow-row">
      <div class="flow-label" style="color: #b85d19;">System<br/><span style="font-size:8.5pt; font-weight:600; color:#4a5568;">(UAV &amp; PCB)</span></div>
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
        <div class="fb-title">SPI Slave Wrapper</div>
        <div class="fb-sub">Đóng gói giao tiếp 7-pin<br/>nối thẳng ESP32</div>
      </div>
      <div class="flow-box fb-plan">
        <div class="fb-title">Closed-Loop Demo</div>
        <div class="fb-sub">LLM Voice ➔ Tay cầm<br/>➔ Chip PID ➔ Drone</div>
      </div>
    </div>

    <div class="flow-legend">
      <div><span class="legend-dot" style="background:#132238;"></span><b>Đã xong (Hoàn thành 100%)</b></div>
      <div><span class="legend-dot" style="background:#dc7629;"></span><b>Đang làm (Trọng tâm Bán kết)</b></div>
      <div><span class="legend-dot" style="border:2px dashed #94a3b8; background:#fff;"></span><b>Kế hoạch đến Chung kết</b></div>
    </div>
  </div>

  <!-- Spec Table with Exact Numbers & Operating Conditions (BTC Checklist requirement) -->
  <div class="card" style="padding: 2mm 3mm;">
    <div style="font-size:9.8pt; font-weight:800; color:#132238; margin-bottom:1mm;">
      Bảng Spec Thiết kế &amp; Điều kiện Hoạt động (Design Specifications &amp; Corner Conditions):
    </div>
    <table class="comp-table" style="font-size:8.4pt;">
      <tr>
        <th>Thông số Spec</th>
        <th>Mục tiêu Thiết kế (Target)</th>
        <th>Kết quả Đạt được (Achieved)</th>
        <th>Điều kiện Đo / Kiểm chứng (Conditions &amp; Level)</th>
      </tr>
      <tr>
        <td><b>Tần số Clock / Latency</b></td>
        <td><code>f_clk = 10 MHz</code> · Latency ≤ 10 µs</td>
        <td><b>20 chu kỳ clock = 2.0 µs / mẫu 3 trục</b></td>
        <td><code>[RTL Sim &amp; STA]</code> Chu kỳ IMU <code>dt = 2.5 ms (400 Hz)</code></td>
      </tr>
      <tr>
        <td><b>Sai số Lượng tử vs. MCU</b></td>
        <td>Lệch xung Motor ≤ 1 µs (&lt; 1% mẫu)</td>
        <td><b>Max 1 µs (0.706% mẫu, RMS 0.08 µs)</b></td>
        <td><code>[Bit-Exact Sim]</code> 16.000 mẫu, 7 kịch bản, dải xung <code>1000..2000 µs</code></td>
      </tr>
      <tr>
        <td><b>Độ rộng Datapath / I/O</b></td>
        <td>Không tràn số với góc ±180°, gyro ±2000°/s</td>
        <td><b>In 22b (Q.10), Mul 14×29b, 7-pin SPI</b></td>
        <td><code>[RTL Sim]</code> đã kiểm · <code>[Post-Synth]</code> kế hoạch ở corner <code>TT 25°C</code> &amp; <code>SS 125°C</code></td>
      </tr>
    </table>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 2 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 3: SMART CITY + LLM + ASIC ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 2 · BỐI CẢNH ĐÔ THỊ THÔNG MINH &amp; KIẾN TRÚC HỆ THỐNG</div>
    <h2 class="slide-title">Vì sao UAV Đô thị cần "Edge LLM + Vi mạch PID chuyên dụng"?</h2>
  </div>

  <div class="grid-2-wide-left">
    <div style="display:flex; flex-direction:column; gap:3mm;">
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
      <img src="{b64_drone}" class="img-fit" style="max-height: 80mm; object-fit: contain;"/>
      <p style="font-size: 8.8pt; color: #4a5568; margin-top: 1.5mm;">
        <b>Hình thực tế hệ thống:</b> <code>ESP32</code> thu thập IMU BNO085 + GPS + RF <code>0xBC/0xCD</code>; khối <code>STM32</code> hiện tại được thay thế trực tiếp bằng <b>Chip ASIC/IP <code>pid_ctrl</code></b>.
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 3 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 4: MATH & FIXED POINT ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 3 · MÔ HÌNH TOÁN HỌC &amp; LƯỢNG TỬ HÓA FIXED-POINT</div>
    <h2 class="slide-title">Biến đổi Đại số Không Phép Chia &amp; Phân tích Độ rộng Bit</h2>
  </div>

  <div class="grid-2">
    <div style="display:flex; flex-direction:column; gap:3mm;">
      <div class="card">
        <div class="card-title">1. Loại bỏ hoàn toàn bộ chia phần cứng (Zero-Divider Datapath)</div>
        <p style="font-size:9.3pt; margin-bottom:1.8mm;">
          Vì IMU BNO085 xuất mẫu đều đặn ở <b>400 Hz (dt = 2.5 ms cố định)</b>, nhóm gộp <code>dt</code> và hệ số khuếch đại đầu ra (<code>OUTPUT_SCALE = 3</code>) vào thẳng hằng số thiết kế:
        </p>
        <table class="comp-table" style="font-size:8.6pt;">
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
          <li style="font-size:9pt; line-height:1.3;"><b>Shift riêng cho từng hệ số (Per-Gain Shift):</b> Vì <code>KI' = 0.0003</code> (shift 25) và <code>KD' = 36</code> (shift 12) lệch nhau <b>5 bậc độ lớn (10<sup>5</sup>)</b>, dùng chung định dạng Q sẽ gây tràn hoặc mất sạch tích phân.</li>
          <li style="font-size:9pt; line-height:1.3;"><b>Khâu D quyết định số bit đầu vào (<code>FE = 10</code>):</b> <code>KD' = 36</code> nhân sai số lượng tử góc lên 36 lần. Chọn <code>Q.10</code> (bước 0.001°) giúp sai lệch xung motor ≤ <b>1 µs</b>.</li>
          <li style="font-size:9pt; line-height:1.3;"><b>Làm tròn 1/2 LSB (<code>ROUND = 1</code>) là bắt buộc:</b> Cộng <code>1 &lt;&lt; (n-1)</code> trước khi dịch phải giúp đạt chuẩn (lệch 1 µs ở 0.71% chu kỳ); nếu cắt (floor) sai số vọt lên 2 µs.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center;">
      <div class="card-title" style="align-self:flex-start;">Đáp ứng vòng kín: Float32 (STM32) vs. Fixed-Point (Chip)</div>
      <img src="{b64_step}" class="img-fit" style="max-height: 62mm; object-fit: contain;"/>
      <div class="card-accent" style="width:100%;">
        <p style="font-size:8.9pt;">
          <b>Kiểm chứng điều khiển học:</b> Đáp ứng bước góc Roll (0° → 20° → −10°) của <b>Cấu hình A</b> (lệch max 0.013°) và <b>Cấu hình B</b> (lệch max 0.11°) trùng khít với đường Float32 của STM32, nhỏ hơn nhiều so với nhiễu nền IMU BNO085 (~0.3°).
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 4 / 12</div>
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
        <img src="{b64_fsm}" class="img-fit" style="max-height: 40mm; object-fit: contain;"/>
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between; align-items:center;">
      <div class="card-title" style="align-self:flex-start;">Sơ đồ khối chi tiết Datapath &amp; FSM (<code>ic/rtl/pid_ctrl.v</code>)</div>
      <img src="{b64_block}" class="img-fit" style="max-height: 90mm; object-fit: contain;"/>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 5 / 12</div>
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
        <p style="font-size:9.2pt; margin-bottom:2mm;">
          File <code>pid_params.vh</code> được sinh tự động bởi <code>export_rtl.py</code>, cho phép nhóm tổng hợp song song 2 phiên bản RTL mà không phải sửa tay code Verilog:
        </p>
        <table class="comp-table" style="font-size:8.8pt;">
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
        <p style="font-size:8.9pt;">
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
          <li><b>Cải tiến an toàn so với Firmware gốc:</b> Firmware STM32 giữ tích phân từ lần bay trước sang lần arm sau; chip giữ y hệt để khớp bit-exact, và có thêm cổng <code>clear</code> đồng bộ để MCU xóa trạng thái PID ở cạnh lên của Arm.</li>
        </ul>
      </div>

      <div class="card-dark" style="font-family: Consolas, monospace; font-size: 8.8pt; line-height: 1.4;">
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
    <div>Slide 6 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 7: COMPARISON TABLE WITH LEVEL & CORNER LABELS (IMAGE 2 + CHECKLIST) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 6 · ĐÁNH GIÁ PPA, NORMALIZATION, FOM &amp; NHÃN BẬC/CORNER</div>
    <h2 class="slide-title">Bảng so sánh với published designs (kèm Nhãn bậc, Corner &amp; Nguồn)</h2>
  </div>

  <div>
    <table class="comp-table" style="font-size:8.4pt;">
      <thead>
        <tr>
          <th style="width: 21%;">Design &amp; Nguồn trích dẫn</th>
          <th style="width: 17%;">Node / Nhãn bậc / Corner</th>
          <th style="width: 11%;">Frequency</th>
          <th style="width: 13%;">Area</th>
          <th style="width: 12%;">Power</th>
          <th style="width: 14%;">Performance<br/><span style="font-size:7.6pt; font-weight:600;">(Latency / Loop Rate)</span></th>
          <th style="width: 12%;">FoM ↓<br/><span style="font-size:7.6pt; font-weight:600;">(Energy / 3-axis Loop)</span></th>
        </tr>
      </thead>
      <tbody>
        <tr class="our-row">
          <td><b>Nhóm em — Cấu hình A</b><br/><span style="font-size:7.8pt; font-weight:600;">(3-Axis PID + Mixer, 14×29b Mul)</span></td>
          <td><b>[Node PDK Cadence]</b><br/><span class="tag-pill">Ước tính · chờ Post-Synth TT/SS</span></td>
          <td><b>10 MHz</b><br/><span style="font-size:7.6pt;">(20 clk/sample)</span></td>
          <td><b>[__] mm²</b><br/><span style="font-size:7.6pt;">(~2.8k–3.5k GE)</span></td>
          <td><b>[__] mW</b><br/><span style="font-size:7.6pt;">(Est: ~0.25 mW)</span></td>
          <td><b>2.0 µs / loop</b><br/><span style="font-size:7.6pt;">(500 kLoops/s)</span></td>
          <td><b>[__] nJ/loop</b><br/><span style="font-size:7.6pt;">(Est: ~0.50 nJ)</span></td>
        </tr>
        <tr class="our-row-b">
          <td><b>Nhóm em — Cấu hình B</b><br/><span style="font-size:7.8pt;">(Tối ưu diện tích, 11×21b Mul)</span></td>
          <td><b>[Node PDK Cadence]</b><br/><span class="tag-pill">Ước tính · chờ Post-Synth TT/SS</span></td>
          <td><b>10 MHz</b><br/><span style="font-size:7.6pt;">(20 clk/sample)</span></td>
          <td><b>[__] mm²</b><br/><span style="font-size:7.6pt;">(~2.1k GE, −25%)</span></td>
          <td><b>[__] mW</b><br/><span style="font-size:7.6pt;">(Est: ~0.18 mW)</span></td>
          <td><b>2.0 µs / loop</b><br/><span style="font-size:7.6pt;">(500 kLoops/s)</span></td>
          <td><b>[__] nJ/loop</b><br/><span style="font-size:7.6pt;">(Est: ~0.36 nJ)</span></td>
        </tr>
        <tr>
          <td colspan="7" style="font-size:8pt; color:#4a5568; font-style:italic;">Hàng thiết kế đã công bố (ASIC/FPGA PID cho quadcopter) chỉ được đưa vào sau khi đối chiếu DOI và số liệu gốc của bài báo.</td>
        </tr>
        <tr class="mcu-row">
          <td><b>[1] Software trên CPU/MCU</b><br/><span style="font-size:7.8pt; color:#1e4e8c;">(Baseline thực tế trên Drone nhóm)</span></td>
          <td><b>STM32F103C8T6</b><br/><span style="font-size:7.6pt;">[Datasheet DS5319 · 3.3V · thời gian ước tính]</span></td>
          <td><b>72 MHz</b></td>
          <td>—<br/><span style="font-size:7.6pt;">(MCU 48-pin rời)</span></td>
          <td><b>118.8 mW</b><br/><span style="font-size:7.6pt;">(36 mA @ 3.3V)</span></td>
          <td><b>~18.5 µs / loop</b><br/><span style="font-size:7.6pt;">(Float32 phần mềm)</span></td>
          <td><b>2,197.8 nJ/loop</b><br/><span style="font-size:7.6pt; color:#c53030;">(Tốn gấp &gt;1.000×)</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="grid-3" style="margin-top: 1.5mm;">
    <div class="card" style="padding: 2mm 3mm;">
      <div style="font-size:9.3pt; font-weight:800; color:#c86428;">So cùng loại &amp; Nguồn trích dẫn</div>
      <p style="font-size:8.2pt; color:#2d3748; margin-top:0.8mm;">
        <b>[1]</b> <code>STM32F103C8</code> chạy <code>Flight.cpp</code> của nhóm: dòng 36 mA theo Datasheet DS5319; 18.5 µs là ước tính, sẽ đo bằng <code>DWT-&gt;CYCCNT</code>. Bài công bố chỉ thêm khi đã đối chiếu DOI.
      </p>
    </div>
    <div class="card" style="padding: 2mm 3mm;">
      <div style="font-size:9.3pt; font-weight:800; color:#c86428;">Normalization (Quy đổi khác Node)</div>
      <p style="font-size:8.2pt; color:#2d3748; margin-top:0.8mm;">
        Quy đổi diện tích qua số cổng chuẩn <b>Gate Equivalents (1 GE = diện tích NAND2)</b> độc lập tiến trình, hoặc chuẩn hóa Dennard: <code>Area_norm = Area × (L_target / L_ref)²</code>, <code>Power_norm = Power × (V_target / V_ref)² × (L_target / L_ref)</code>.
      </p>
    </div>
    <div class="card" style="padding: 2mm 3mm;">
      <div style="font-size:9.3pt; font-weight:800; color:#c86428;">FoM: Đúng Metric Vi mạch Điều khiển</div>
      <p style="font-size:8.2pt; color:#2d3748; margin-top:0.8mm;">
        Thay vì Gbps (chip mạng), bộ điều khiển bay thời gian thực dùng <b>Năng lượng trên mỗi chu kỳ cập nhật 3 trục</b>: <code>FoM = Power × Latency = P × (20 / f_clk) [nJ/loop]</code> (càng nhỏ càng tối ưu cho pin UAV).
      </p>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 7 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 8: MOT KHUNG QUAY MAN HINH THUYET PHUC (BTC IMAGE 3 MATCH) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 7 · KẾT QUẢ MÔ PHỎNG &amp; DEMO TRỰC QUAN (CHUẨN BỐ CỤC HỘI ĐỒNG)</div>
    <h2 class="slide-title">Một khung quay màn hình thuyết phục: Waveform · Log · Phần cứng</h2>
  </div>

  <!-- Dark composite frame matching BTC "Mot khung quay man hinh thuyet phuc" -->
  <div style="background:#0f172a; border-radius:12px; padding:3.5mm; display:grid; grid-template-columns: 1.38fr 0.62fr; gap:3.5mm; flex:1; border:2px solid #334155;">
    <!-- Left column: [1] Waveform + [4] Subtitle -->
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:2mm;">
      <div style="position:relative; background:#1e293b; border-radius:8px; padding:2mm; border:1px solid #475569;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1mm;">
          <div style="color:#f8fafc; font-size:9.5pt; font-weight:700;">
            <span class="num-badge">1</span>Waveform chọn lọc: <code>pid_ctrl.v</code> xử lý 1 mẫu IMU trong đúng 20 chu kỳ clock (2.0 µs)
          </div>
          <span style="background:#ea8030; color:#141c2b; font-weight:800; font-size:8pt; padding:1px 7px; border-radius:10px;">
            Zoom 20 clk · Cursor @ +2.0 µs
          </span>
        </div>
        <img src="{b64_wave}" style="width:100%; max-height:78mm; object-fit:contain; border-radius:6px;"/>
      </div>

      <!-- [4] Bottom bar: Speed tag + Subtitle -->
      <div style="display:flex; align-items:center; gap:3mm;">
        <div style="background:#ea8030; color:#141c2b; font-weight:900; font-size:9.2pt; padding:2mm 3.5mm; border-radius:8px; white-space:nowrap;">
          Thực thi 1×: ≈ 5 giây / 16.000 mẫu
        </div>
        <div style="flex:1; background:#1e293b; border:1.5px solid #ea8030; border-radius:8px; padding:2mm 3.5mm; color:#f8fafc; font-size:9.5pt; font-weight:700; display:flex; align-items:center; justify-content:space-between;">
          <span>Output RTL (<code>m1..m4, mix_r/p/y</code>) khớp Bit-Exact 100% với Golden Model Python trên cả 7 kịch bản bay</span>
          <span class="num-badge" style="margin-right:0;">4</span>
        </div>
      </div>
    </div>

    <!-- Right column: [2] Self-checking log + [3] Hardware / Layout -->
    <div style="display:flex; flex-direction:column; justify-content:space-between; gap:2.5mm;">
      <div style="background:#1e293b; border-radius:8px; padding:2.8mm; border:1px solid #475569; font-family:Consolas, monospace;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5mm; font-family:'Segoe UI', sans-serif;">
          <span style="color:#f8fafc; font-size:9.5pt; font-weight:700;"><span class="num-badge">2</span>Self-checking Testbench Log</span>
          <span style="color:#94a3b8; font-size:8pt;">tb_pid_ctrl.v</span>
        </div>
        <div style="font-size:8.4pt; color:#cbd5e1; line-height:1.38;">
          <div>$ powershell -File ic/sim/run_demo_ban_ket.ps1</div>
          <div style="color:#94a3b8;">[A] 7 kich ban, 16000 mau,</div>
          <div style="color:#94a3b8;">    do tre toi da 20 chu ky clock / mau</div>
          <div style="color:#94a3b8;">[A] PASS: 16000/16000 mau khop bit-exact</div>
          <div style="color:#94a3b8;">[B] PASS: 16000/16000 mau khop bit-exact</div>
          <div style="color:#94a3b8;">[SPI] PASS: 100/100 mau (MOSI va MISO)</div>
          <div style="color:#4ade80; font-size:11pt; font-weight:900; margin-top:1.5mm; background:#052e16; padding:1.5mm 2.5mm; border-radius:5px; border:1px solid #22c55e;">
            PASS 16000 / 16000 test (0 lỗi)
          </div>
        </div>
      </div>

      <div style="background:#1e293b; border-radius:8px; padding:2.5mm; border:1px solid #475569; flex:1; display:flex; flex-direction:column; justify-content:space-between;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="color:#f8fafc; font-size:9.5pt; font-weight:700;"><span class="num-badge">3</span>Phần cứng UAV &amp; Tay cầm PCB thật</span>
          <span style="color:#fbd38d; font-size:8pt; font-weight:700;">Real System</span>
        </div>
        <img src="{b64_s3}" style="width:100%; max-height:38mm; object-fit:contain; border-radius:5px; background:#ffffff;"/>
        <p style="font-size:8pt; color:#cbd5e1;">
          Tay cầm <b>Altium Custom PCB</b> + Drone <b>STM32/ESP32</b> + Buồng lái 3D <code>gcs_drone_simulator.html</code>.
        </p>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 8 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 9: DEMO PLAN A / B / C & VIDEO SCRIPT (BTC IMAGE 4 MATCH) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 8 · CHIẾN LƯỢC TRÌNH DIỄN THỰC CHIẾN &amp; PHÂN VAI</div>
    <h2 class="slide-title">Demo trực tiếp: luôn có phương án A, B và C</h2>
  </div>

  <!-- 3 Horizontal Boxes A -> B -> C matching BTC slide -->
  <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:5mm; margin: 1mm 0;">
    <div class="card-dark" style="border: 2px solid #132238;">
      <div style="font-size:13pt; font-weight:800; color:#ea8030; margin-bottom:1.5mm;">A · Chạy trực tiếp (Ưu tiên số 1)</div>
      <p style="font-size:9.5pt; color:#e2e8f0; margin-bottom:2mm;">
        <b>Simulation RTL + Buồng lái 3D HIL, kịch bản đã tập:</b>
      </p>
      <ul class="clean" style="color:#cbd5e1;">
        <li>Chạy script 1 lệnh <code>ic/sim/run_demo_ban_ket.ps1</code> kiểm chứng trực tiếp <b>16.000 mẫu PASS</b> cho cả Cấu hình A &amp; B, cộng 100 mẫu qua giao tiếp SPI, trong vài giây.</li>
        <li>Mở trực tiếp <code>gcs_drone_simulator.html</code> trên Chrome nối với Tay cầm PCB qua USB Serial (<code>$SIMTEL</code>) để biểu diễn phản hồi PFD &amp; PID.</li>
      </ul>
    </div>

    <div class="card" style="border: 2px solid #cbd5e1;">
      <div style="font-size:13pt; font-weight:800; color:#132238; margin-bottom:1.5mm;">B · Video quay sẵn (Dự phòng 10s)</div>
      <p style="font-size:9.5pt; color:#334155; margin-bottom:2mm;">
        <b>Mở ngay trong 10 giây, nói rõ đây là bản ghi:</b>
      </p>
      <ul class="clean">
        <li>File MP4 quay sẵn độ phân giải FullHD 60fps đặt ngay cùng thư mục Slide, bật bằng phím tắt trong 10 giây nếu kết nối VPN/Cadence hoặc cổng USB bị nghẽn.</li>
        <li><b>Cảnh 1 (0–15s):</b> Drone &amp; Tay cầm PCB thật + Simulator 3D.</li>
        <li><b>Cảnh 2 (15–45s):</b> Chạy Testbench 16.000 mẫu + Zoom Waveform 20 chu kỳ.</li>
        <li><b>Cảnh 3 (45–60s):</b> Báo cáo Synthesis Cadence Genus &amp; Bảng PPA.</li>
      </ul>
    </div>

    <div class="card" style="border: 2px solid #cbd5e1;">
      <div style="font-size:13pt; font-weight:800; color:#132238; margin-bottom:1.5mm;">C · Screenshot, log, plot</div>
      <p style="font-size:9.5pt; color:#334155; margin-bottom:2mm;">
        <b>Slide dự phòng: report, waveform, log PASS:</b>
      </p>
      <ul class="clean">
        <li>Nhảy trực tiếp tới <b>Slide 8</b> (Waveform 20 chu kỳ + Log PASS 16.000/16.000), <b>Slide 11</b> (Timing &amp; Power Report) và <b>Slide 12</b> (Coverage Matrix).</li>
        <li>Toàn bộ hình ảnh đều đã được render <b>Vector SVG / PNG độ phân giải 2×</b> nhúng trực tiếp vào PDF, không phụ thuộc mạng Internet.</li>
      </ul>
    </div>
  </div>

  <!-- Pre-demo checklist bar matching BTC slide -->
  <div style="background:#efeae1; border-radius:8px; padding:3mm 4.5mm; border:1px solid #d6cfc2;">
    <div style="font-size:10.5pt; font-weight:800; color:#141c2b; margin-bottom:1mm;">Trước giờ demo &amp; Phân vai thành viên nhóm FPOLY UAV</div>
    <p style="font-size:9.2pt; color:#334155; line-height:1.4;">
      <b>Chuẩn bị kỹ thuật:</b> File thực thi <code>tb_pid_ctrl.vvp</code> và <code>vectors.txt</code> đã build sẵn · Script 1 lệnh <code>run_demo_ban_ket.ps1</code> · Cáp USB-C / UART dự phòng cho tay cầm · Tắt Windows Update &amp; thông báo · Đã tập dượt bấm giờ 3 lần.<br/>
      <b>Phân vai trình bày &amp; Hỏi đáp (Q&amp;A):</b> <b>(1) Hệ thống UAV, PCB &amp; Kiến trúc RTL:</b> Nguyễn Trung (Cinq) · <b>(2) Mô hình Toán Fixed-Point &amp; Verification:</b> Phụ trách phân tích sai số lượng tử &amp; Testbench · <b>(3) Synthesis Cadence, STA &amp; PPA Normalization:</b> Phụ trách báo cáo Genus/Innovus.
    </p>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV</div>
    <div>Slide 9 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 10: CHECKLIST TRUOC VONG HOAN THIEN SAN PHAM (BTC IMAGE 5 MATCH) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">PHẦN 9 · RÀ SOÁT TIÊU CHUẨN HỘI ĐỒNG &amp; LỘ TRÌNH CHUNG KẾT</div>
    <h2 class="slide-title">Checklist trước Vòng hoàn thiện sản phẩm (12 / 12 hạng mục)</h2>
  </div>

  <!-- 3 Columns matching BTC "Checklist truoc Vong hoan thien san pham" -->
  <div class="grid-3" style="flex:1; margin-bottom:2.5mm;">
    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div style="font-size:13pt; font-weight:800; color:#141c2b; margin-bottom:2.5mm;">Design</div>
        <ul class="check-list">
          <li><b>Spec có số và điều kiện:</b> Đã lập bảng Spec tại Slide 2 (<code>10 MHz</code>, <code>dt = 2.5 ms</code>, <code>20 clk = 2.0 µs</code>, lệch <code>≤ 1 µs</code>, dải góc <code>±180°</code>, gyro <code>±2000°/s</code>).</li>
          <li><b>Slide vị trí trên design flow:</b> Đã mở đầu tại Slide 2, tách rõ nhánh Digital (<code>pid_ctrl</code>) và nhánh System (<code>UAV &amp; PCB</code>).</li>
          <li><b>Mỗi số gắn nhãn bậc, corner:</b> Đã gắn rõ <code>[RTL Sim]</code>, <code>[Ước tính · chờ Post-Synth TT/SS]</code>, <code>[Datasheet]</code> tại Slide 7.</li>
          <li><b>Bảng so sánh có nguồn:</b> Baseline <code>STM32F103C8</code> theo Datasheet DS5319 [1]; bài công bố chỉ đưa vào khi đã đối chiếu DOI.</li>
        </ul>
      </div>
      <div class="card-accent" style="font-size:8.6pt;">
        <b>Trạng thái Design:</b> Sẵn sàng 100% RTL (<code>pid_ctrl.v</code> + <code>spi_pid_wrapper.v</code>) và script tổng hợp <code>syn_genus.tcl</code>.
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div style="font-size:13pt; font-weight:800; color:#141c2b; margin-bottom:2.5mm;">Bài trình bày</div>
        <ul class="check-list">
          <li><b>Câu giới thiệu một dòng:</b> Đã đặt ngay đầu Slide 1 nêu bật bài toán, kiến trúc 1 bộ nhân không phép chia và mức cải thiện 9.2× tốc độ / &gt;1.000× năng lượng.</li>
          <li><b>Tập 3 lần, đúng giờ:</b> Cấu trúc 10 slide chính khớp thời lượng báo cáo (10–12 phút), chuyển ý mạch lạc từ Spec ➔ Toán ➔ RTL ➔ Verification ➔ PPA.</li>
          <li><b>Phân vai nói và hỏi đáp:</b> Đã phân công rõ người trả lời câu hỏi Kiến trúc RTL/UAV, Lượng tử hóa Fixed-point và Cadence Synthesis/STA (Slide 9).</li>
          <li><b>Slide dự phòng: timing, power, coverage:</b> Đã chuẩn bị sẵn tại <b>Slide 11 &amp; Slide 12</b> ngay sau đây.</li>
        </ul>
      </div>
      <div class="card-accent" style="font-size:8.6pt;">
        <b>Trạng thái Bài trình bày:</b> Xuất bản song song cả HTML tương tác và PDF 16:9 sắc nét.
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div style="font-size:13pt; font-weight:800; color:#141c2b; margin-bottom:2.5mm;">Video &amp; demo</div>
        <ul class="check-list">
          <li><b>Kịch bản theo từng cảnh:</b> Đã chia 3 phân cảnh rõ ràng (Hệ thống thật ➔ RTL Simulation &amp; Waveform ➔ Cadence PPA) tại Slide 9.</li>
          <li><b>Design chạy, khớp golden model:</b> Đạt <b>Bit-Exact PASS 16.000/16.000 mẫu</b> cho cả Cấu hình A và B, kèm kiểm thử Fault Injection.</li>
          <li><b>Phóng to, chữ đọc được:</b> Toàn bộ Waveform, Log terminal và Bảng số liệu trên Slide 8 đều dùng cỡ chữ lớn, độ tương phản cao.</li>
          <li><b>Đúng định dạng BTC, nộp sớm:</b> Tuân thủ nghiêm ngặt bố cục mẫu của Hội đồng Giám khảo.</li>
        </ul>
      </div>
      <div class="card-accent" style="font-size:8.6pt;">
        <b>Trạng thái Demo:</b> Có sẵn cả 3 phương án A (Live), B (Video 10s), C (Backup Slides).
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Thiết kế vi mạch cho đô thị thông minh lần 3 · Bảng sinh viên · Nhóm FPOLY UAV — Cảm ơn Hội đồng Giám khảo!</div>
    <div>Slide 10 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 11: BACKUP 1 - TIMING & POWER ANALYSIS (Q&A) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">SLIDE DỰ PHÒNG 1 (APPENDIX FOR Q&amp;A) · TIMING &amp; POWER DEEP-DIVE</div>
    <h2 class="slide-title">Phân tích Chuyên sâu: Critical Path Timing &amp; Cơ cấu Công suất</h2>
  </div>

  <div class="grid-2">
    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">1. Phân tích Đường găng Thời gian (Static Timing Analysis — STA)</div>
        <ul class="clean">
          <li><b>Chu kỳ Clock mục tiêu:</b> <code>T_clk = 100.0 ns (10 MHz)</code> · Clock Uncertainty: <code>0.2 ns</code>.</li>
          <li><b>Đường găng (Critical Path) của <code>pid_ctrl.v</code>:</b>
            <br/>Xuất phát từ thanh ghi toán hạng <code>mul_a[13:0]</code> / <code>mul_b[28:0]</code> ➔ đi qua <b>Bộ nhân có dấu 14×29-bit (<code>prod[42:0]</code>)</b> ➔ đi qua hàm <b>cộng làm tròn 1/2 LSB &amp; dịch phải <code>shr(prod, sh_d)</code></b> ➔ đi qua <b>bộ cộng 3 số hạng 28-bit (<code>p_w + i_w + d_term</code>)</b> ở trạng thái <code>S_D</code> ➔ chốt vào thanh ghi <code>u_w[27:0]</code>.</li>
          <li><b>Đánh giá Slack &amp; Tần số Cực đại (<code>f_max</code>):</b>
            <br/>Tổng độ trễ tổ hợp của chuỗi <code>Mul(14×29) + RoundAdder + Add(28b)</code> trên tiến trình CMOS 180nm/130nm/45nm chỉ khoảng <b>4.5 ns – 12.0 ns</b>.</li>
          <li>Ước tính tại <code>10 MHz (100 ns)</code>, mạch có <b>Positive Slack rất lớn (&gt; +85 ns)</b>, đảm bảo <b>0 Timing Violation</b> ngay cả ở góc chậm nhất (<code>Slow-Slow Corner, 125°C, Vdd − 10%</code>).</li>
        </ul>
      </div>
      <div class="card-accent" style="font-size:8.8pt;">
        <b>Nếu Hội đồng hỏi "Làm sao đẩy f_max lên &gt;200 MHz?":</b> Chỉ cần chèn 1 thanh ghi pipeline (<code>prod_r</code>) ngay sau bộ nhân <code>prod = mul_a * mul_b</code> (tăng độ trễ từ 20 lên 23 clock = 2.3 µs), tách rời hoàn toàn bộ nhân và bộ cộng!
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">2. Phân tích Công suất (Power Breakdown &amp; Duty-Cycle Gating)</div>
        <table class="comp-table" style="font-size:8.5pt; margin-bottom:2mm;">
          <tr>
            <th>Trạng thái Hoạt động</th>
            <th>Thời gian trong 1 chu kỳ IMU (2.500 µs)</th>
            <th>Tỷ lệ Thời gian (Duty Cycle)</th>
            <th>Hoạt động Chuyển mạch (Switching Activity)</th>
          </tr>
          <tr class="our-row">
            <td><b>Active Computing</b><br/>(<code>S_LOAD .. S_MIX</code>)</td>
            <td><b>2.0 µs</b> (20 clock @ 10 MHz)</td>
            <td><b>0.08 %</b></td>
            <td>Bộ nhân 14×29 &amp; FSM chuyển trạng thái tính 3 trục</td>
          </tr>
          <tr>
            <td><b>Idle Waiting</b><br/>(<code>S_IDLE, busy=0</code>)</td>
            <td><b>2.498.0 µs</b> (24.980 clock)</td>
            <td><b>99.92 %</b></td>
            <td>Toàn bộ thanh ghi <code>acc_r, prev_r, dfilt_r, mul_a, mul_b</code> giữ nguyên giá trị (<b>Switching = 0%</b>)</td>
          </tr>
        </table>
        <ul class="clean">
          <li><b>Tại sao công suất của <code>pid_ctrl</code> siêu thấp?</b>
            <br/>Trong RTL (dòng 208–236 <code>pid_ctrl.v</code>), các thanh ghi <code>mul_a, mul_b, e_w, p_w, i_w, u_w</code> chỉ nạp dữ liệu mới khi <code>state != S_IDLE</code>. Trong <b>99.92%</b> thời gian còn lại, đầu vào bộ nhân đứng yên tuyệt đối, không sinh công suất động (Dynamic Glitch Power = 0).</li>
          <li>Script <code>syn_genus.tcl</code> bật <b>Automated Clock Gating (ICG cell)</b> (<code>lp_insert_clock_gating</code>); xung clock cấp cho 234 Flip-Flops được ngắt hoàn toàn khi <code>state == S_IDLE &amp;&amp; !sample_valid</code>.</li>
        </ul>
      </div>
      <div class="card-dark" style="font-size:8.6pt;">
        <b style="color:#f6ad55;">Lệnh kiểm tra trên Cadence Genus:</b> <code>CORNER=SS genus -f ic/syn/syn_genus.tcl</code> (chạy lại với <code>CORNER=TT</code>) ➔ xuất <code>reports/pid_ctrl_SS_timing.rpt</code>, <code>pid_ctrl_TT_power.rpt</code> và <code>pid_ctrl_*_clock_gating.rpt</code>.
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Slide Dự phòng Hỏi – Đáp (Q&amp;A Appendix 1) · Nhóm FPOLY UAV</div>
    <div>Slide 11 / 12</div>
  </div>
</section>

<!-- ========================================================= SLIDE 12: BACKUP 2 - COVERAGE MATRIX & SPI WRAPPER (Q&A) ========================================================= -->
<section class="slide">
  <div>
    <div class="kicker">SLIDE DỰ PHÒNG 2 (APPENDIX FOR Q&amp;A) · VERIFICATION COVERAGE &amp; I/O PACKAGING</div>
    <h2 class="slide-title">Ma trận Độ phủ Kiểm thử (Coverage) &amp; Đóng gói Giao tiếp SPI 7-Chân</h2>
  </div>

  <div class="grid-2">
    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">1. Ma trận Độ phủ Chức năng &amp; Code (Verification Coverage Matrix)</div>
        <table class="comp-table" style="font-size:8.3pt;">
          <tr>
            <th>Hạng mục Coverage</th>
            <th>Kịch bản Kiểm thử Kích hoạt</th>
            <th>Số mẫu</th>
            <th>Kết quả</th>
          </tr>
          <tr>
            <td><b>FSM State &amp; Transition</b><br/>(<code>IDLE→LOAD→FILT→P→I→D→SAT→MIX</code>)</td>
            <td>Tất cả 6 kịch bản có <code>armed = 1, throttle &gt; 1000</code></td>
            <td>14.000</td>
            <td><b>100% (8/8 states)</b></td>
          </tr>
          <tr>
            <td><b>Safety Gate (Khóa an toàn)</b><br/>(<code>!armed || throttle ≤ 1000</code>)</td>
            <td>Kịch bản 7 (<code>arm_disarm</code>) + đầu mỗi kịch bản (<code>clear = 1</code>)</td>
            <td>2.000</td>
            <td><b>100% (m1..m4 = 1000)</b></td>
          </tr>
          <tr>
            <td><b>Anti-Windup &amp; Saturation</b><br/>(<code>u_hi, u_lo, ±U_LIM, ±ACC_LIM</code>)</td>
            <td>Kịch bản 5 (<code>ket_bao_hoa</code>) &amp; Kịch bản 6 (<code>ngau_nhien_toan_dai</code>)</td>
            <td>3.600</td>
            <td><b>100% nhánh bão hòa</b></td>
          </tr>
          <tr>
            <td><b>X-Frame Motor Clamp</b><br/>(<code>motor_clamp &lt;1000, &gt;2000</code>)</td>
            <td>Kịch bản 2 (<code>buoc_roll_pitch</code>) &amp; Kịch bản 4, 6</td>
            <td>7.600</td>
            <td><b>100% biên 1000..2000</b></td>
          </tr>
          <tr>
            <td><b>Sign &amp; Truncation-to-Zero</b><br/>(<code>sat_w &lt; 0</code> vs. <code>sat_w ≥ 0</code>)</td>
            <td>Kịch bản 1 (<code>hover_gio_nhieu</code>) &amp; Kịch bản 3 (<code>yaw_quay</code>)</td>
            <td>4.800</td>
            <td><b>100% khớp <code>int32_t</code> C++</b></td>
          </tr>
        </table>
      </div>
      <div class="card-accent" style="font-size:8.6pt;">
        <b>Tổng kết Verification:</b> 16.000 mẫu × 7 đầu ra (<code>mix_r, mix_p, mix_y, m1, m2, m3, m4</code>) = <b>112.000 phép so sánh Bit-Exact</b> hoàn toàn tự động, đạt tỷ lệ khớp <b>100.00%</b>.
      </div>
    </div>

    <div class="card" style="display:flex; flex-direction:column; justify-content:space-between;">
      <div>
        <div class="card-title">2. Giải pháp Chống Pad-Limited khi Tape-out: <code>spi_pid_wrapper.v</code></div>
        <ul class="clean">
          <li><b>Vấn đề nếu đưa thẳng <code>pid_ctrl.v</code> ra chân chip:</b>
            <br/>Tổng số bit cổng song song là <code>6×22 (in) + 11 (thr) + 4×11 (motor) + 3×10 (mix) + 6 (ctrl) ≈ 223 chân I/O</code> ➔ Diện tích Pad Ring sẽ lớn gấp nhiều lần diện tích Core!</li>
          <li><b>Giải pháp đã hiện thực hóa trong <code>ic/rtl/spi_pid_wrapper.v</code>:</b>
            <br/>Bọc lõi <code>pid_ctrl</code> trong bộ thu phát <b>SPI Slave Mode 0 (khung 192-bit)</b> có đồng bộ chống Metastability (3-FF cho <code>sclk</code>/<code>cs_n</code>, 2-FF cho <code>mosi</code>), đã kiểm thử <b>PASS 16.000/16.000 mẫu qua SPI</b>:</li>
          <li><b>Chỉ cần đúng 7 chân (Pins) cho toàn bộ con chip:</b>
            <br/><code>clk</code>, <code>rst_n</code>, <code>spi_sclk</code>, <code>spi_cs_n</code>, <code>spi_mosi</code>, <code>spi_miso</code>, <code>irq_out_valid</code> (cộng <code>VDD, VSS</code> là 9 chân, vừa vỏ <b>QFN-16</b>; cổng <code>busy</code> của RTL là tùy chọn vì đã có ở bit 191 của MISO).</li>
          <li>SCLK được lấy mẫu bằng <code>clk</code> nên phải ≤ <code>f_clk/4</code> (≈ 2.5 MHz). Ở SPI <code>2 MHz</code>, truyền 192-bit mất <b>96 µs</b> + tính PID <b>2.0 µs</b> = <b>98 µs</b> (chưa tới 4% chu kỳ IMU 2.500 µs).</li>
        </ul>
      </div>
      <div class="card-dark" style="font-family:Consolas, monospace; font-size:8.3pt;">
        <div style="color:#fbd38d; font-weight:bold;">// Giao tiếp ESP32 (Master) ⇄ Chip pid_ctrl (SPI Slave 7-pin)</div>
        <div>MOSI [191:0] : {{clear, armed, thr[10:0], sp_r/p/y, roll/pitch/gz}}</div>
        <div>MISO [191:0] : {{busy, m1[10:0], m2, m3, m4, mix_r/p/y[9:0]}}</div>
      </div>
    </div>
  </div>

  <div class="slide-footer">
    <div>Slide Dự phòng Hỏi – Đáp (Q&amp;A Appendix 2) · Nhóm FPOLY UAV</div>
    <div>Slide 12 / 12</div>
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
